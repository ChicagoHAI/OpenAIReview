#!/usr/bin/env python3
"""Prepare a deep-review workspace: parse paper, split into sections, write files.

Usage:
    python3 scripts/prepare_workspace.py <input> [--slug SLUG] [--criteria PATH] [--output-dir DIR]

The script auto-detects input type (PDF, arXiv URL, .tex/.txt/.md), downloads if
needed, parses the paper, splits into sections, and writes a structured workspace
to <output-dir>/<slug>_review/ (default: ./review_results/<slug>_review/).

Workspace layout:
    <output-dir>/<slug>_review/
        metadata.json       -- title, slug, total character count
        full_text.md         -- complete paper text
        criteria.md          -- review criteria (if --criteria provided)
        sections/
            index.json       -- list of {file, heading, chars}
            00_intro.md      -- individual section files
            ...
        comments/            -- empty dir for sub-agent outputs
"""

import argparse
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

# Try to import the canonical reviewer.parsers pipeline (BeautifulSoup + Marker).
# If available it is preferred for all HTML and PDF parsing.  All parse_* helpers
# below fall back to stdlib-only implementations when the package is absent.
try:
    import reviewer.parsers as _rparsers
    _HAS_RPARSERS = True
except Exception:
    _rparsers = None  # type: ignore
    _HAS_RPARSERS = False


# ---------------------------------------------------------------------------
# Input detection
# ---------------------------------------------------------------------------

def detect_input_type(input_path: str) -> str:
    """Return one of: arxiv_abs, arxiv_html, pdf_url, pdf, html, text."""
    if input_path.startswith(("http://", "https://")):
        if "arxiv.org/abs/" in input_path:
            return "arxiv_abs"
        if "arxiv.org/html/" in input_path:
            return "arxiv_html"
        if input_path.lower().endswith(".pdf"):
            return "pdf_url"
        return "url"

    ext = Path(input_path).suffix.lower()
    if ext == ".pdf":
        return "pdf"
    if ext == ".html":
        return "html"
    return "text"


def make_slug(input_path: str) -> str:
    """Generate a slug from the input (arXiv ID or filename stem)."""
    m = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", input_path)
    if m:
        return re.sub(r"[.\-]", "", m.group(1))
    return re.sub(r"[^a-z0-9]+", "-", Path(input_path).stem.lower())[:80].strip("-")


# ---------------------------------------------------------------------------
# ArXiv HTML parser — stdlib fallback (no BeautifulSoup required)
# ---------------------------------------------------------------------------

_SKIP_CLASSES = (
    "ltx_bibliography", "ltx_bibnotes", "ltx_TOC",
    "ltx_authors", "ltx_dates", "ltx_role_affiliations",
    "ltx_page_footer", "ltx_pagination",
)


class _ArxivExtractor(HTMLParser):
    """Stdlib-only fallback: extract text from arXiv LaTeXML HTML."""

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "nav" or any(k in cls for k in _SKIP_CLASSES):
            self.skip_stack.append(tag)
        if self.skip_stack:
            return
        if tag == "h1" and "ltx_title_document" in cls:
            self.parts.append("\n\n# ")
        elif tag in ("h2", "h3", "h4", "h5") and "ltx_title" in cls:
            self.parts.append(f"\n\n{'#' * int(tag[1])} ")
        elif tag == "p":
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append("\n\u2022 ")

    def handle_endtag(self, tag):
        if self.skip_stack and self.skip_stack[-1] == tag:
            self.skip_stack.pop()
            return
        if self.skip_stack:
            return
        if tag == "p":
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_stack:
            self.parts.append(data)


def _parse_arxiv_html_stdlib(html_path: str) -> tuple[str, str]:
    """Stdlib-only fallback: parse a downloaded arXiv HTML file."""
    html = Path(html_path).read_text(errors="replace")
    ext = _ArxivExtractor()
    ext.feed(html)
    text = re.sub(r"\n{3,}", "\n\n", "".join(ext.parts)).strip()
    m = re.search(r"^# ", text, re.MULTILINE)
    if m:
        text = text[m.start():]
    title = text.split("\n")[0].lstrip("# ").strip()
    return title, text


# ---------------------------------------------------------------------------
# Top-level parse dispatcher — prefers reviewer.parsers, falls back to stdlib
# ---------------------------------------------------------------------------

def parse_input(source_type: str, input_path: str, slug: str) -> tuple[str, str]:
    """Parse any supported input type and return (title, full_text).

    Routing priority:
      1. reviewer.parsers (BeautifulSoup + lxml for HTML; Marker for PDFs) — best quality
      2. Built-in stdlib / pymupdf fallback — works without extra dependencies
    """

    # ---- arXiv abstract URL (e.g. https://arxiv.org/abs/2310.06825) ----------
    if source_type == "arxiv_abs":
        if _HAS_RPARSERS:
            try:
                print("  Using reviewer.parsers for arXiv abs URL.", file=sys.stderr)
                return _rparsers.parse_document(input_path)
            except Exception as e:
                print(f"  reviewer.parsers failed ({e}), using fallback.", file=sys.stderr)
        # Stdlib fallback: try HTML then PDF
        arxiv_id = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", input_path).group(1)
        html_path = f"/tmp/{slug}.html"
        subprocess.run(
            ["curl", "-sL", f"https://arxiv.org/html/{arxiv_id}", "-o", html_path],
            check=True, capture_output=True,
        )
        content = Path(html_path).read_text(errors="replace")
        if "<article" in content or "ltx_document" in content:
            return _parse_arxiv_html_stdlib(html_path)
        print("  HTML not available, falling back to PDF...", file=sys.stderr)
        pdf_path = f"/tmp/{slug}.pdf"
        subprocess.run(
            ["curl", "-sL", f"https://arxiv.org/pdf/{arxiv_id}", "-o", pdf_path],
            check=True, capture_output=True,
        )
        return _parse_pdf_fallback(pdf_path, slug)

    # ---- arXiv HTML URL (e.g. https://arxiv.org/html/2310.06825) -------------
    if source_type == "arxiv_html":
        if _HAS_RPARSERS:
            try:
                print("  Using reviewer.parsers for arXiv HTML URL.", file=sys.stderr)
                return _rparsers.parse_arxiv_html(input_path)
            except Exception as e:
                print(f"  reviewer.parsers failed ({e}), using fallback.", file=sys.stderr)
        # Stdlib fallback: download then parse
        html_path = f"/tmp/{slug}.html"
        subprocess.run(
            ["curl", "-sL", input_path, "-o", html_path],
            check=True, capture_output=True,
        )
        return _parse_arxiv_html_stdlib(html_path)

    # ---- PDF or generic URL (download first, then parse as PDF) ---------------
    if source_type in ("pdf_url", "url"):
        local_path = f"/tmp/{slug}.pdf"
        subprocess.run(
            ["curl", "-sL", input_path, "-o", local_path],
            check=True, capture_output=True,
        )
        if _HAS_RPARSERS:
            try:
                print("  Using reviewer.parsers for downloaded file.", file=sys.stderr)
                return _rparsers.parse_document(local_path)
            except Exception as e:
                print(f"  reviewer.parsers failed ({e}), using fallback.", file=sys.stderr)
        return _parse_pdf_fallback(local_path, slug)

    # ---- Local PDF file -------------------------------------------------------
    if source_type == "pdf":
        if _HAS_RPARSERS:
            try:
                print("  Using reviewer.parsers for PDF.", file=sys.stderr)
                return _rparsers.parse_document(input_path)
            except Exception as e:
                print(f"  reviewer.parsers failed ({e}), using fallback.", file=sys.stderr)
        return _parse_pdf_fallback(input_path, slug)

    # ---- Local HTML file (e.g. saved arXiv page) -----------------------------
    if source_type == "html":
        if _HAS_RPARSERS:
            try:
                from bs4 import BeautifulSoup
                html = Path(input_path).read_text(errors="replace")
                # Inject the html content into a fake URL call by monkey-patching urlopen,
                # or simpler: replicate the BS4 logic inline on local content.
                soup = BeautifulSoup(html, "lxml")
                title = ""
                title_el = soup.find(class_="ltx_title_document")
                if title_el:
                    title = title_el.get_text(strip=True)
                if not title:
                    tag = soup.find("title")
                    if tag:
                        title = tag.get_text(strip=True)
                doc_el = soup.find(class_="ltx_document") or soup.find("article") or soup.body
                if doc_el:
                    for sel in ["nav", ".ltx_bibliography", ".ltx_TOC", "header", "footer",
                                ".package-hierarchical-accordion", "#header", ".arxiv-watermark",
                                ".ltx_role_affiliationtext"]:
                        for el in doc_el.select(sel):
                            el.decompose()
                    sections = []
                    for element in doc_el.find_all(class_=re.compile(
                        r"^ltx_(para$|title_|abstract$|theorem$|proof$|caption)"
                    )):
                        text = element.get_text(" ", strip=True)
                        if not text:
                            continue
                        cls_str = " ".join(element.get("class", []))
                        if "ltx_title_document" in cls_str:
                            sections.append(f"# {text}")
                        elif "ltx_title_section" in cls_str:
                            sections.append(f"\n## {text}")
                        elif "ltx_title_subsection" in cls_str:
                            sections.append(f"\n### {text}")
                        elif "ltx_title_subsubsection" in cls_str:
                            sections.append(f"\n#### {text}")
                        elif "ltx_title_appendix" in cls_str:
                            sections.append(f"\n## {text}")
                        elif "ltx_title_abstract" in cls_str:
                            continue  # handled by ltx_abstract
                        elif cls_str.startswith("ltx_title"):
                            sections.append(f"\n**{text}**")
                        elif "ltx_abstract" in cls_str:
                            abstract_paras = element.find_all(class_="ltx_p")
                            abstract_text = ("\n\n".join(
                                p.get_text(" ", strip=True) for p in abstract_paras
                            ) if abstract_paras else text)
                            sections.append(f"\n## Abstract\n{abstract_text}")
                        else:
                            sections.append(text)
                    full_text = "\n\n".join(sections)
                    if len(full_text) >= 500:
                        if not title:
                            for line in full_text.split("\n"):
                                if line.strip():
                                    title = line.strip()[:200]
                                    break
                        print("  Parsed local HTML with BeautifulSoup.", file=sys.stderr)
                        return title, full_text
            except Exception as e:
                print(f"  BS4 parse failed ({e}), using stdlib fallback.", file=sys.stderr)
        return _parse_arxiv_html_stdlib(input_path)

    # ---- Plain text / TeX / Markdown -----------------------------------------
    text = Path(input_path).read_text(errors="replace")
    m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    title = m.group(1).strip() if m else text.split("\n")[0].strip()
    return title, text


def _parse_pdf_fallback(pdf_path: str, slug: str) -> tuple[str, str]:
    """Stdlib/pymupdf PDF fallback: used when reviewer.parsers is unavailable.

    If pymupdf text contains an arXiv ID, re-fetches as HTML for better quality.
    """
    import pymupdf
    doc = pymupdf.open(pdf_path)
    text = "\n\n".join(p.get_text() for p in doc)
    title = text.split("\n")[0].strip()
    doc.close()

    arxiv_match = (
        re.search(r"arXiv:(\d{4}\.\d{4,5})", text)
        or re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", text)
    )
    if arxiv_match:
        arxiv_id = arxiv_match.group(1)
        html_path = f"/tmp/{slug}.html"
        result = subprocess.run(
            ["curl", "-sL", f"https://arxiv.org/html/{arxiv_id}", "-o", html_path],
            capture_output=True,
        )
        if result.returncode == 0:
            content = Path(html_path).read_text(errors="replace")
            if "<article" in content or "ltx_document" in content:
                print("  Re-fetched arXiv HTML for PDF fallback.", file=sys.stderr)
                # Prefer reviewer.parsers even at this point
                if _HAS_RPARSERS:
                    try:
                        return _rparsers.parse_arxiv_html(
                            f"https://arxiv.org/html/{arxiv_id}"
                        )
                    except Exception:
                        pass
                return _parse_arxiv_html_stdlib(html_path)

    return title, text


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def split_sections(text: str, sections_dir: Path) -> list[dict]:
    """Split paper text into section files. Returns index metadata."""
    heading_re = re.compile(r"^(#{1,3}) (.+)", re.MULTILINE)
    heads = list(heading_re.finditer(text))
    sections = []

    if len(heads) >= 3:
        for i, h in enumerate(heads):
            start = h.start()
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            sec_text = text[start:end].strip()
            heading = h.group(2).strip()
            fname = re.sub(r"[^a-z0-9]+", "_", heading.lower())[:50].strip("_")
            fname = f"{i:02d}_{fname}"
            sections.append({"file": f"{fname}.md", "heading": heading, "chars": len(sec_text)})
            (sections_dir / f"{fname}.md").write_text(sec_text)
    else:
        # No headings: split into ~8000-char chunks at paragraph boundaries
        buf, chunks = "", []
        for para in text.split("\n\n"):
            if len(buf) + len(para) > 8000 and buf:
                chunks.append(buf)
                buf = para
            else:
                buf = (buf + "\n\n" + para) if buf else para
        if buf:
            chunks.append(buf)
        for i, chunk in enumerate(chunks):
            fname = f"{i:02d}_chunk"
            first = chunk.strip().split("\n")[0][:60]
            sections.append({"file": f"{fname}.md", "heading": f"Chunk {i + 1}: {first}", "chars": len(chunk)})
            (sections_dir / f"{fname}.md").write_text(chunk)

    return sections


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Prepare a deep-review workspace")
    parser.add_argument("input", help="Paper path or URL")
    parser.add_argument("--slug", help="Override slug (default: auto-detected)")
    parser.add_argument("--criteria", help="Path to criteria.md to copy into workspace")
    parser.add_argument("--output-dir", default="./review_results", help="Parent directory for the workspace (default: ./review_results)")
    args = parser.parse_args()

    source_type = detect_input_type(args.input)
    slug = args.slug or make_slug(args.input)

    review_dir = Path(args.output_dir) / f"{slug}_review"
    for d in ("sections", "comments"):
        (review_dir / d).mkdir(parents=True, exist_ok=True)

    title, text = parse_input(source_type, args.input, slug)

    # Write workspace files
    (review_dir / "full_text.md").write_text(text)
    (review_dir / "metadata.json").write_text(json.dumps({
        "title": title,
        "slug": slug,
        "total_chars": len(text),
    }, indent=2))

    if args.criteria and Path(args.criteria).exists():
        (review_dir / "criteria.md").write_text(Path(args.criteria).read_text())

    sections = split_sections(text, review_dir / "sections")
    (review_dir / "sections" / "index.json").write_text(json.dumps(sections, indent=2))

    # Summary output
    print(f"TITLE: {title}")
    print(f"SLUG: {slug}")
    print(f"REVIEW_DIR: {review_dir}")
    print(f"SECTIONS ({len(sections)}):")
    for s in sections:
        print(f"  {s['file']} -- {s['heading']} ({s['chars']} chars)")
    print(f"TOTAL: {len(text)} chars")


if __name__ == "__main__":
    main()
