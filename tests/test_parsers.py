"""Unit tests for parser helpers."""

from reviewer.parsers import _extract_title_from_pdf_page, _normalize_pdf_text


class _FakePage:
    def __init__(self, blocks):
        self._blocks = blocks

    def get_text(self, kind, sort=False):
        assert kind == "dict"
        return {"blocks": self._blocks}


def _text_block(y0, size, *lines):
    return {
        "bbox": [0, y0, 100, y0 + 20],
        "lines": [
            {
                "spans": [{"text": line, "size": size}],
            }
            for line in lines
        ],
    }


def test_extract_title_from_pdf_page_skips_arxiv_metadata():
    page = _FakePage([
        _text_block(20, 9.0, "arXiv:2602.18458v1 [cs.CY] 5 Feb 2026"),
        _text_block(
            50,
            14.3,
            "The Story is Not the Science:",
            "Execution-Grounded Evaluation of Mechanistic Interpretability Research",
        ),
        _text_block(90, 10.0, "Xiaoyan Bai", "Alexander Baumgartner"),
        _text_block(130, 12.0, "Abstract"),
    ])

    title = _extract_title_from_pdf_page(page)

    assert title == (
        "The Story is Not the Science: "
        "Execution-Grounded Evaluation of Mechanistic Interpretability Research"
    )


def test_normalize_pdf_text_merges_wrapped_lines_and_dehyphenates():
    raw = (
        "Peer review has long treated the paper narrative as the pri-\n"
        "mary object of evaluation.\n"
        "This may suffice for theoretical work.\n"
        "\n"
        "1. Introduction\n"
        "Agentic workflows add more challenges.\n"
    )

    cleaned = _normalize_pdf_text(raw)

    assert "primary object of evaluation." in cleaned
    assert "pri-\nmary" not in cleaned
    assert "1. Introduction" in cleaned
