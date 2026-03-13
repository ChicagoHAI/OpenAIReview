"""Document parsers for PDF, DOCX, TEX, TXT, MD files, and arXiv HTML URLs."""

import re
from pathlib import Path


def is_url(s: str) -> bool:
    """Check if a string looks like a URL."""
    return s.startswith("http://") or s.startswith("https://")


def parse_document(file_path: str | Path) -> tuple[str, str]:
    """Parse a document file or URL and return (title, full_text).

    Supported formats: .pdf, .docx, .tex, .txt, .md
    Also supports arXiv HTML URLs (e.g. https://arxiv.org/html/2310.06825).
    """
    path_str = str(file_path)

    if is_url(path_str):
        if "arxiv.org/abs/" in path_str:
            return _parse_arxiv_abs(path_str)
        return parse_arxiv_html(path_str)

    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _parse_pdf(path)
    elif suffix == ".docx":
        return _parse_docx(path)
    elif suffix == ".tex":
        return _parse_tex(path)
    elif suffix in (".txt", ".md", ".markdown"):
        return _parse_text(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _parse_pdf(path: Path) -> tuple[str, str]:
    """Extract text from PDF. Uses Marker CLI if available (better math), else pymupdf."""
    try:
        return _parse_pdf_marker(path)
    except (ImportError, FileNotFoundError, RuntimeError) as e:
        print(f"  Marker not available ({e}), using pymupdf fallback.")
        print("  Note: pymupdf cannot extract math symbols correctly. "
              "For math-heavy PDFs, use .tex source or arXiv HTML.")
        return _parse_pdf_pymupdf(path)


def _parse_pdf_marker(path: Path) -> tuple[str, str]:
    """High-quality PDF extraction using Marker (preserves math as LaTeX).

    Tries the Python API first, then falls back to the Marker CLI.
    """
    try:
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        from marker.output import text_from_rendered

        converter = PdfConverter(artifact_dict=create_model_dict())
        rendered = converter(str(path))
        markdown, _, _ = text_from_rendered(rendered)
    except ImportError:
        # Fall back to Marker CLI (avoids openai version conflict)
        import os
        import shutil
        import subprocess
        import tempfile

        marker_bin = shutil.which("marker_single")
        if not marker_bin:
            raise FileNotFoundError("marker_single not found on PATH")

        import platform
        env = os.environ.copy()
        if platform.system() == "Darwin":
            env["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
            env["TORCH_DEVICE"] = "cpu"

        with tempfile.TemporaryDirectory() as tmpdir:
            proc = subprocess.Popen(
                [marker_bin, str(path), "--output_dir", tmpdir],
                env=env,
            )
            try:
                proc.communicate(timeout=3600)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                raise RuntimeError("marker timed out after 3600s")
            if proc.returncode != 0:
                raise RuntimeError(f"marker failed (exit code {proc.returncode})")

            # Marker outputs to a subdirectory named after the PDF
            md_files = list(Path(tmpdir).rglob("*.md"))
            if not md_files:
                raise RuntimeError("marker produced no markdown output")
            markdown = md_files[0].read_text()

    title = _extract_title_from_markdown(markdown)
    return title, markdown


def _extract_title_from_markdown(markdown: str) -> str:
    """Extract the first heading from markdown text as the title."""
    for line in markdown.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("# ").strip()
    # Fallback: first non-empty line
    for line in markdown.split("\n"):
        if line.strip():
            return line.strip()[:200]
    return ""


def _parse_pdf_pymupdf(path: Path) -> tuple[str, str]:
    """Fallback PDF extraction using pymupdf (no math support)."""
    import pymupdf

    doc = pymupdf.open(str(path))
    pages = []
    title = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append(text)

        if page_num == 0 and not title:
            blocks = page.get_text("dict")["blocks"]
            best_size = 0
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip() and span["size"] > best_size:
                            best_size = span["size"]

            if best_size > 0:
                candidates = []
                current_parts = []
                for block in blocks:
                    if "lines" not in block:
                        if current_parts:
                            candidates.append(" ".join(current_parts))
                            current_parts = []
                        continue
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span_text = span["text"].strip()
                            if not span_text:
                                continue
                            if abs(span["size"] - best_size) < 0.5:
                                current_parts.append(span_text)
                            elif current_parts:
                                candidates.append(" ".join(current_parts))
                                current_parts = []
                if current_parts:
                    candidates.append(" ".join(current_parts))
                if candidates:
                    title = max(candidates, key=len)

    doc.close()
    full_text = "\n\n".join(pages)

    if not title:
        for line in full_text.split("\n"):
            if line.strip():
                title = line.strip()[:200]
                break

    return title, full_text


def _parse_docx(path: Path) -> tuple[str, str]:
    """Extract text from DOCX using python-docx."""
    import docx

    doc = docx.Document(str(path))
    paragraphs = []
    title = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        paragraphs.append(text)
        if not title and para.style and para.style.name.startswith("Heading"):
            title = text

    full_text = "\n\n".join(paragraphs)

    if not title and paragraphs:
        title = paragraphs[0][:200]

    return title, full_text


def _parse_tex(path: Path) -> tuple[str, str]:
    """Extract text from LaTeX source."""
    text = path.read_text(encoding="utf-8", errors="replace")
    title = ""

    # Extract title from \title{...}
    title_match = re.search(r"\\title\{([^}]+)\}", text)
    if title_match:
        title = title_match.group(1).strip()
        # Clean common LaTeX artifacts from title
        title = re.sub(r"\\\\", " ", title)  # line breaks
        title = re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", title)  # \textbf{X} → X
        title = re.sub(r"[{}]", "", title)  # stray braces
        title = re.sub(r"\s+", " ", title).strip()

    if not title:
        for line in text.split("\n"):
            if line.strip():
                title = line.strip()[:200]
                break

    return title, text


def _parse_text(path: Path) -> tuple[str, str]:
    """Extract text from plain text or markdown."""
    text = path.read_text(encoding="utf-8", errors="replace")
    title = ""

    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        # Markdown heading
        if stripped.startswith("#"):
            title = stripped.lstrip("# ").strip()
        else:
            title = stripped[:200]
        break

    return title, text


def _parse_arxiv_abs(url: str) -> tuple[str, str]:
    """Parse an arXiv abs URL: try HTML first, fall back to PDF."""
    html_url = re.sub(r"arxiv\.org/abs/", "arxiv.org/html/", url)
    try:
        return parse_arxiv_html(html_url)
    except Exception as e:
        print(f"HTML version not available ({e}), falling back to PDF...")

    return _fetch_arxiv_pdf(url)


def _fetch_arxiv_pdf(url: str) -> tuple[str, str]:
    """Fetch a PDF from an arXiv abs URL and parse it.

    Converts https://arxiv.org/abs/<id> to https://arxiv.org/pdf/<id>.
    """
    import tempfile
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    pdf_url = re.sub(r"arxiv\.org/abs/", "arxiv.org/pdf/", url)
    print(f"Fetching PDF from {pdf_url}...")
    try:
        req = Request(pdf_url, headers={"User-Agent": "openaireview/0.1"})
        with urlopen(req, timeout=60) as resp:
            pdf_bytes = resp.read()
    except URLError as e:
        raise RuntimeError(f"Failed to fetch {pdf_url}: {e}") from e

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = Path(tmp.name)

    try:
        return _parse_pdf(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _tabular_to_markdown(table_el) -> str:
    """Convert a BS4 ltx_tabular element to a markdown table."""
    rows = []
    for tr in table_el.find_all("tr"):
        cells = tr.find_all(["td", "th"])
        if not cells:
            continue
        row = [
            cell.get_text(" ", strip=True).replace("|", r"\|").replace("\n", " ")
            for cell in cells
        ]
        rows.append(row)

    if not rows:
        return ""

    ncols = max(len(r) for r in rows)

    def pad(r):
        return r + [""] * (ncols - len(r))

    lines = ["| " + " | ".join(pad(rows[0])) + " |",
             "| " + " | ".join(["---"] * ncols) + " |"]
    for row in rows[1:]:
        lines.append("| " + " | ".join(pad(row)[:ncols]) + " |")
    return "\n".join(lines)


def _figure_or_table_to_markdown(fig_el, base_url: str) -> str:
    """Convert an ltx_figure or ltx_table element to markdown text.

    Tables become markdown tables (with caption above).
    Image figures become ![caption](absolute_url) links (with caption below).
    """
    from urllib.parse import urljoin

    caption_el = fig_el.find(class_="ltx_caption")
    caption = (caption_el.get_text(" ", strip=True) if caption_el else "").replace("\n", " ")

    # Table figure: contains ltx_tabular
    tabular = fig_el.find(class_="ltx_tabular")
    if tabular:
        table_md = _tabular_to_markdown(tabular)
        if not table_md:
            return f"**{caption}**" if caption else ""
        return (f"**{caption}**\n\n{table_md}" if caption else table_md)

    # Image figure: collect main graphics, skip tiny caption icons
    imgs = [
        img for img in fig_el.find_all("img", class_="ltx_graphics")
        if not (caption_el and caption_el.find(lambda t: t is img))
        and int(img.get("width", "100") or "100") >= 30
    ]
    if not imgs:
        return f"**{caption}**" if caption else ""

    lines = []
    for img in imgs:
        src = img.get("src", "")
        if not src:
            continue
        alt = img.get("alt", "") or caption
        if alt == "Refer to caption":
            alt = caption
        if not src.startswith(("http://", "https://", "//")):
            src = urljoin(base_url, src)
        lines.append(f"![{alt}]({src})")

    if not lines:
        return f"**{caption}**" if caption else ""
    result = "\n".join(lines)
    if caption:
        # Two trailing spaces = markdown line break; keeps image+caption in same paragraph
        result += f"  \n*{caption}*"
    return result


def parse_arxiv_html(url: str) -> tuple[str, str]:
    """Fetch and parse an arXiv HTML page into (title, full_text).

    Works with arXiv HTML URLs like https://arxiv.org/html/2310.06825.
    The HTML is generated by LaTeXML and uses ltx_* CSS classes.
    Tables are converted to markdown tables; figures include image links.
    """
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    from bs4 import BeautifulSoup

    print(f"Fetching {url}...")
    try:
        req = Request(url, headers={"User-Agent": "openaireview/0.1"})
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            final_url = resp.url  # URL after any redirects
    except URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

    # Base URL for resolving relative image paths (must end with /)
    base_url = final_url.rstrip("/") + "/"

    soup = BeautifulSoup(html, "lxml")

    # Extract title
    title = ""
    title_el = soup.find(class_="ltx_title_document")
    if title_el:
        title = title_el.get_text(strip=True)
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    # Find the main document body
    doc = soup.find(class_="ltx_document") or soup.find("article") or soup.body
    if not doc:
        raise RuntimeError("Could not find paper content in HTML")

    # Remove bibliography, navigation, and other non-content elements
    for sel in ["nav", ".ltx_bibliography", ".ltx_TOC", "header", "footer",
                ".package-hierarchical-accordion", "#header", ".arxiv-watermark",
                ".ltx_role_affiliationtext"]:
        for el in doc.select(sel):
            el.decompose()

    # Pre-process figures and tables: convert to markdown and replace with
    # ltx_para marker divs so they appear at the correct position in the flow.
    # Use exact class match (not substring) to avoid matching ltx_figure_panel etc.
    for fig in doc.find_all(
        class_=lambda c: c in ("ltx_figure", "ltx_table")
    ):
        md = _figure_or_table_to_markdown(fig, base_url)
        if md:
            marker = soup.new_tag("div")
            marker["class"] = "ltx_para"
            marker["data-oar-content"] = md
            fig.replace_with(marker)
        else:
            fig.decompose()

    # Extract structured text using leaf content elements only.
    # ltx_para = paragraph text, ltx_title_* = headings, ltx_abstract = abstract,
    # ltx_theorem/ltx_proof = theorems. Captions are now handled via figure pre-processing.
    # We do NOT match ltx_section/ltx_subsection (containers that include all children).
    sections = []
    for element in doc.find_all(class_=re.compile(
        r"^ltx_(para$|title_|abstract$|theorem$|proof$)"
    )):
        # Figure/table markers: use pre-computed markdown directly
        oar_content = element.get("data-oar-content")
        if oar_content is not None:
            sections.append(oar_content)
            continue

        text = element.get_text(" ", strip=True)
        if not text:
            continue

        # Format headings
        cls = element.get("class", [])
        cls_str = " ".join(cls) if isinstance(cls, list) else cls
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
            # Skip — already handled by ltx_abstract match
            continue
        elif cls_str.startswith("ltx_title"):
            # Other titles (theorem, proof, etc.)
            sections.append(f"\n**{text}**")
        elif "ltx_abstract" in cls_str:
            # Extract just paragraph text, skip the title child
            abstract_paras = element.find_all(class_="ltx_p")
            if abstract_paras:
                abstract_text = "\n\n".join(
                    p.get_text(" ", strip=True) for p in abstract_paras
                )
            else:
                abstract_text = text
            sections.append(f"\n## Abstract\n{abstract_text}")
        else:
            sections.append(text)

    full_text = "\n\n".join(sections)

    # Fallback: if structured extraction got very little, use plain text
    if len(full_text) < 500:
        full_text = doc.get_text("\n", strip=True)

    if not title:
        for line in full_text.split("\n"):
            if line.strip():
                title = line.strip()[:200]
                break

    return title, full_text
