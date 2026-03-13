"""Unit tests for optional LightOn OCR helpers."""

from reviewer.lighton import (
    compute_text_similarity,
    benchmark_parser_baselines,
    extract_image_boxes,
    normalize_ocr_text,
    normalized_bbox_to_pixels,
    resolve_lighton_onnx_repo,
)


def test_extract_image_boxes_parses_bbox_soup_markers():
    text = (
        "Some text\n"
        "![image](image_0.png)120,45,900,700\n"
        "More text\n"
        "![image](image_1.png) 10, 20, 30, 40"
    )

    boxes = extract_image_boxes(text)

    assert boxes == [(120, 45, 900, 700), (10, 20, 30, 40)]


def test_normalized_bbox_to_pixels_clamps_to_bounds():
    bbox = (-20, 50, 1200, 1100)

    pixels = normalized_bbox_to_pixels(bbox, width=1540, height=1000)

    assert pixels == (0, 50, 1540, 1000)


def test_normalize_ocr_text_strips_figure_markers():
    text = "Hello\n![image](image_0.png)120,45,900,700\nWorld"

    normalized = normalize_ocr_text(text)

    assert normalized == "hello world"


def test_compute_text_similarity_returns_high_score_for_close_text():
    metrics = compute_text_similarity(
        "The quick brown fox jumps over the lazy dog",
        "The quick brown fox jumps over a lazy dog",
    )

    assert metrics["token_f1"] > 0.8
    assert metrics["sequence_ratio"] > 0.8


def test_resolve_lighton_onnx_repo_supports_aliases():
    assert resolve_lighton_onnx_repo("plain") == "onnx-community/LightOnOCR-2-1B-ONNX"
    assert resolve_lighton_onnx_repo("custom/repo") == "custom/repo"


def test_benchmark_parser_baselines_honors_max_pages(tmp_path):
    import pymupdf

    pdf_path = tmp_path / "sample.pdf"
    doc = pymupdf.open()
    for page_number in range(3):
        page = doc.new_page()
        page.insert_text((72, 72), f"Page {page_number + 1}")
    doc.save(pdf_path)
    doc.close()

    runs = benchmark_parser_baselines(pdf_path, include_pymupdf=True, max_pages=2)

    assert runs[0]["page_count"] == 2
    assert "Page 3" not in runs[0]["text_preview"]
