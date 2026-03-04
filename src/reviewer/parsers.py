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
    """Extract text from PDF using pymupdf."""
    import pymupdf

    doc = pymupdf.open(str(path))
    pages = []
    title = ""

    for page_num, page in enumerate(doc):
        text = page.get_text()
        pages.append(text)

        if page_num == 0 and not title:
            # Try to find title from largest font text on first page
            blocks = page.get_text("dict")["blocks"]
            best_size = 0
            for block in blocks:
                if "lines" not in block:
                    continue
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["size"] > best_size and span["text"].strip():
                            best_size = span["size"]
                            title = span["text"].strip()

    doc.close()
    full_text = "\n\n".join(pages)

    if not title:
        # Fallback: first non-empty line
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


def parse_arxiv_html(url: str) -> tuple[str, str]:
    """Fetch and parse an arXiv HTML page into (title, full_text).

    Works with arXiv HTML URLs like https://arxiv.org/html/2310.06825.
    The HTML is generated by LaTeXML and uses ltx_* CSS classes.
    """
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    from bs4 import BeautifulSoup

    print(f"Fetching {url}...")
    try:
        req = Request(url, headers={"User-Agent": "openaireview/0.1"})
        with urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}") from e

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

    # Extract structured text using leaf content elements only.
    # ltx_para = paragraph text, ltx_title_* = headings, ltx_abstract = abstract,
    # ltx_theorem/ltx_proof = theorems, ltx_caption = figure captions.
    # We do NOT match ltx_section/ltx_subsection (containers that include all children).
    sections = []
    for element in doc.find_all(class_=re.compile(
        r"^ltx_(para$|title_|abstract$|theorem$|proof$|caption)"
    )):
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
            # Other titles (theorem, proof, caption, etc.)
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
