#!/usr/bin/env python3
"""Prepare a deep-review workspace: parse paper, split into sections, write files.

Usage:
    python3 ~/.claude/commands/openaireview/scripts/prepare_workspace.py <input> [--slug SLUG] [--criteria PATH]

The script auto-detects input type (PDF, arXiv URL, .tex/.txt/.md), downloads if
needed, parses the paper, splits into sections, and writes a structured workspace
to /tmp/<slug>_review/.

Workspace layout:
    /tmp/<slug>_review/
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
# ArXiv HTML parser (stdlib only — no BeautifulSoup required)
# ---------------------------------------------------------------------------

SKIP_CLASSES = (
    "ltx_bibliography", "ltx_bibnotes", "ltx_TOC",
    "ltx_authors", "ltx_dates", "ltx_role_affiliations",
    "ltx_page_footer", "ltx_pagination",
)


class ArxivExtractor(HTMLParser):
    """Extract clean markdown-ish text from arXiv LaTeXML HTML."""

    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        cls = dict(attrs).get("class", "")
        if tag == "nav" or any(k in cls for k in SKIP_CLASSES):
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


def parse_arxiv_html_file(html_path: str) -> tuple[str, str]:
    """Parse a downloaded arXiv HTML file into (title, text)."""
    html = Path(html_path).read_text(errors="replace")
    ext = ArxivExtractor()
    ext.feed(html)
    text = re.sub(r"\n{3,}", "\n\n", "".join(ext.parts)).strip()
    m = re.search(r"^# ", text, re.MULTILINE)
    if m:
        text = text[m.start():]
    title = text.split("\n")[0].lstrip("# ").strip()
    return title, text


# ---------------------------------------------------------------------------
# PDF parsing (reuses reviewer.parsers when available)
# ---------------------------------------------------------------------------

def parse_pdf(pdf_path: str, slug: str) -> tuple[str, str]:
    """Parse a PDF file. Falls back to pymupdf if reviewer.parsers fails.

    If pymupdf extraction finds an arXiv ID, re-fetches as HTML for better quality.
    """
    try:
        from reviewer.parsers import parse_document
        return parse_document(pdf_path)
    except Exception:
        pass

    import pymupdf
    doc = pymupdf.open(pdf_path)
    text = "\n\n".join(p.get_text() for p in doc)
    title = text.split("\n")[0].strip()
    doc.close()

    # If pymupdf output contains an arXiv ID, re-fetch as HTML
    arxiv_match = re.search(r"arXiv:(\d{4}\.\d{4,5})", text) or \
                  re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5})", text)
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
                print(f"  Re-fetched as arXiv HTML for better quality.", file=sys.stderr)
                return parse_arxiv_html_file(html_path)

    return title, text


# ---------------------------------------------------------------------------
# Top-level parse dispatcher
# ---------------------------------------------------------------------------

def parse_input(source_type: str, input_path: str, slug: str) -> tuple[str, str]:
    """Parse any supported input type and return (title, full_text)."""
    if source_type == "arxiv_abs":
        arxiv_id = re.search(r"(\d{4}\.\d{4,5}(?:v\d+)?)", input_path).group(1)
        html_path = f"/tmp/{slug}.html"
        subprocess.run(
            ["curl", "-sL", f"https://arxiv.org/html/{arxiv_id}", "-o", html_path],
            check=True, capture_output=True,
        )
        content = Path(html_path).read_text(errors="replace")
        if "<article" in content or "ltx_document" in content:
            return parse_arxiv_html_file(html_path)
        # Fall back to PDF
        print("  HTML not available, falling back to PDF...", file=sys.stderr)
        pdf_path = f"/tmp/{slug}.pdf"
        subprocess.run(
            ["curl", "-sL", f"https://arxiv.org/pdf/{arxiv_id}", "-o", pdf_path],
            check=True, capture_output=True,
        )
        return parse_pdf(pdf_path, slug)

    if source_type == "arxiv_html":
        html_path = f"/tmp/{slug}.html"
        subprocess.run(
            ["curl", "-sL", input_path, "-o", html_path],
            check=True, capture_output=True,
        )
        return parse_arxiv_html_file(html_path)

    if source_type in ("pdf_url", "url"):
        pdf_path = f"/tmp/{slug}.pdf"
        subprocess.run(
            ["curl", "-sL", input_path, "-o", pdf_path],
            check=True, capture_output=True,
        )
        return parse_pdf(pdf_path, slug)

    if source_type == "pdf":
        return parse_pdf(input_path, slug)

    if source_type == "html":
        return parse_arxiv_html_file(input_path)

    # text, tex, md
    text = Path(input_path).read_text(errors="replace")
    m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    title = m.group(1).strip() if m else text.split("\n")[0].strip()
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
    args = parser.parse_args()

    source_type = detect_input_type(args.input)
    slug = args.slug or make_slug(args.input)

    review_dir = Path(f"/tmp/{slug}_review")
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
