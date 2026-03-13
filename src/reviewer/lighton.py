"""Optional LightOn OCR helpers built on onnxruntime-genai."""

from __future__ import annotations

import difflib
import re
import tempfile
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


DEFAULT_LIGHTON_PROMPT = (
    "Extract the full page as clean markdown in natural reading order. "
    "Preserve headings, lists, tables, references, and equations when legible. "
    "Return only the extracted page text."
)

_IMAGE_BOX_RE = re.compile(
    r"!\[image\]\(image_(\d+)\.png\)\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)"
)

LIGHTON_ONNX_MODEL_ALIASES = {
    "plain": "onnx-community/LightOnOCR-2-1B-ONNX",
    "plain-onnx": "onnx-community/LightOnOCR-2-1B-ONNX",
}


@dataclass(frozen=True)
class RenderedPage:
    """A rendered PDF page prepared for multimodal OCR."""

    page_index: int
    image_path: Path
    width: int
    height: int


@dataclass(frozen=True)
class LightOnOcrPage:
    """One OCR result for a rendered page."""

    page_index: int
    image_path: Path
    width: int
    height: int
    text: str
    generated_tokens: int


@dataclass(frozen=True)
class LightOnFigure:
    """One figure crop extracted from bbox-capable OCR output."""

    page_index: int
    figure_index: int
    bbox_norm: tuple[int, int, int, int]
    bbox_pixels: tuple[int, int, int, int]
    crop_path: Path


@dataclass(frozen=True)
class LightOnOcrRun:
    """OCR run metadata and page-level outputs."""

    model_dir: str
    provider: str
    prompt: str
    render_longest_dim: int
    max_length: int
    model_load_seconds: float
    render_seconds: float
    inference_seconds: float
    pages: list[LightOnOcrPage]

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text.strip())

    @property
    def title(self) -> str:
        text = self.full_text
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                return stripped.lstrip("# ").strip()
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:200]
        return ""


def _require_lighton_runtime(require_pillow: bool = False):
    """Import LightOn runtime dependencies on demand."""
    try:
        import onnxruntime_genai as og
    except ImportError as e:
        raise ImportError(
            "LightOn OCR support requires the optional dependency set. "
            "Install with: pip install 'openaireview[lighton]'"
        ) from e

    pillow_image = None
    if require_pillow:
        try:
            from PIL import Image
        except ImportError as e:
            raise ImportError(
                "Figure extraction requires Pillow. "
                "Install with: pip install 'openaireview[lighton]'"
            ) from e
        pillow_image = Image

    return og, pillow_image


def _load_model(model_dir: str | Path, provider: str = "auto"):
    """Load a LightOn ONNX model with an optional explicit provider."""
    og, _ = _require_lighton_runtime()
    provider = provider.strip().lower()
    model_dir = str(model_dir)

    if provider not in {"auto", "cpu", "cuda"}:
        raise ValueError("provider must be one of: auto, cpu, cuda")

    if provider == "auto":
        return og.Model(model_dir)

    config_cls = getattr(og, "Config", None)
    if config_cls is None:
        raise RuntimeError(
            "Explicit provider selection requires an onnxruntime-genai build "
            "with Config support."
        )

    config = config_cls(model_dir)
    if not hasattr(config, "clear_providers"):
        raise RuntimeError(
            "Explicit provider selection requires Config.clear_providers()."
        )

    config.clear_providers()
    if provider == "cuda":
        if not hasattr(config, "append_provider"):
            raise RuntimeError(
                "Explicit provider selection requires Config.append_provider()."
            )
        config.append_provider("CUDAExecutionProvider")

    return og.Model(config)


def render_pdf_pages(
    pdf_path: str | Path,
    output_dir: str | Path,
    *,
    max_pages: int | None = None,
    longest_dim: int = 1540,
) -> list[RenderedPage]:
    """Render PDF pages to PNG files sized for LightOn OCR."""
    import pymupdf

    if longest_dim <= 0:
        raise ValueError("longest_dim must be > 0")

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(str(pdf_path))
    rendered: list[RenderedPage] = []

    try:
        page_count = doc.page_count if max_pages is None else min(doc.page_count, max_pages)
        for page_index in range(page_count):
            page = doc[page_index]
            scale = longest_dim / max(page.rect.width, page.rect.height)
            matrix = pymupdf.Matrix(scale, scale)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            image_path = output_dir / f"page-{page_index + 1:04d}.png"
            pix.save(str(image_path))
            rendered.append(
                RenderedPage(
                    page_index=page_index,
                    image_path=image_path,
                    width=pix.width,
                    height=pix.height,
                )
            )
    finally:
        doc.close()

    return rendered


def run_lighton_ocr_on_pages(
    rendered_pages: list[RenderedPage],
    *,
    model_dir: str | Path,
    provider: str = "auto",
    prompt: str = DEFAULT_LIGHTON_PROMPT,
    max_length: int = 4096,
) -> tuple[list[LightOnOcrPage], float]:
    """Run LightOn OCR over a prepared list of page images."""
    og, _ = _require_lighton_runtime()
    if max_length <= 0:
        raise ValueError("max_length must be > 0")

    load_start = time.perf_counter()
    model = _load_model(model_dir, provider=provider)
    processor = model.create_multimodal_processor()
    model_load_seconds = time.perf_counter() - load_start

    ocr_pages: list[LightOnOcrPage] = []
    infer_start = time.perf_counter()
    for rendered in rendered_pages:
        text, token_count = _run_lighton_page_ocr(
            og=og,
            model=model,
            processor=processor,
            page_image=rendered.image_path,
            prompt=prompt,
            max_length=max_length,
        )
        ocr_pages.append(
            LightOnOcrPage(
                page_index=rendered.page_index,
                image_path=rendered.image_path,
                width=rendered.width,
                height=rendered.height,
                text=text,
                generated_tokens=token_count,
            )
        )
    inference_seconds = time.perf_counter() - infer_start
    return ocr_pages, model_load_seconds + inference_seconds


def run_lighton_ocr(
    pdf_path: str | Path,
    *,
    model_dir: str | Path,
    provider: str = "auto",
    max_pages: int | None = None,
    longest_dim: int = 1540,
    prompt: str = DEFAULT_LIGHTON_PROMPT,
    max_length: int = 4096,
) -> LightOnOcrRun:
    """Run LightOn OCR end-to-end on a PDF."""
    with tempfile.TemporaryDirectory() as tmpdir:
        render_start = time.perf_counter()
        rendered_pages = render_pdf_pages(
            pdf_path,
            tmpdir,
            max_pages=max_pages,
            longest_dim=longest_dim,
        )
        render_seconds = time.perf_counter() - render_start

        load_start = time.perf_counter()
        model = _load_model(model_dir, provider=provider)
        processor = model.create_multimodal_processor()
        model_load_seconds = time.perf_counter() - load_start

        og, _ = _require_lighton_runtime()
        infer_start = time.perf_counter()
        pages: list[LightOnOcrPage] = []
        for rendered in rendered_pages:
            text, token_count = _run_lighton_page_ocr(
                og=og,
                model=model,
                processor=processor,
                page_image=rendered.image_path,
                prompt=prompt,
                max_length=max_length,
            )
            pages.append(
                LightOnOcrPage(
                    page_index=rendered.page_index,
                    image_path=rendered.image_path,
                    width=rendered.width,
                    height=rendered.height,
                    text=text,
                    generated_tokens=token_count,
                )
            )
        inference_seconds = time.perf_counter() - infer_start

    return LightOnOcrRun(
        model_dir=str(model_dir),
        provider=provider,
        prompt=prompt,
        render_longest_dim=longest_dim,
        max_length=max_length,
        model_load_seconds=model_load_seconds,
        render_seconds=render_seconds,
        inference_seconds=inference_seconds,
        pages=pages,
    )


def benchmark_lighton_ocr(
    pdf_path: str | Path,
    *,
    model_dir: str | Path,
    provider: str = "cpu",
    max_pages: int | None = None,
    longest_dim: int = 1540,
    prompt: str = DEFAULT_LIGHTON_PROMPT,
    max_length: int = 4096,
    warmup_pages: int = 1,
) -> dict:
    """Benchmark LightOn OCR throughput on rendered page images."""
    with tempfile.TemporaryDirectory() as tmpdir:
        render_start = time.perf_counter()
        rendered_pages = render_pdf_pages(
            pdf_path,
            tmpdir,
            max_pages=max_pages,
            longest_dim=longest_dim,
        )
        render_seconds = time.perf_counter() - render_start

        if not rendered_pages:
            raise RuntimeError("No pages rendered from the PDF")

        load_start = time.perf_counter()
        model = _load_model(model_dir, provider=provider)
        processor = model.create_multimodal_processor()
        model_load_seconds = time.perf_counter() - load_start

        og, _ = _require_lighton_runtime()

        warmup_subset = rendered_pages[:max(0, warmup_pages)]
        warmup_seconds = 0.0
        if warmup_subset:
            warmup_start = time.perf_counter()
            for rendered in warmup_subset:
                _run_lighton_page_ocr(
                    og=og,
                    model=model,
                    processor=processor,
                    page_image=rendered.image_path,
                    prompt=prompt,
                    max_length=max_length,
                )
            warmup_seconds = time.perf_counter() - warmup_start

        token_count = 0
        inference_start = time.perf_counter()
        for rendered in rendered_pages:
            _, generated_tokens = _run_lighton_page_ocr(
                og=og,
                model=model,
                processor=processor,
                page_image=rendered.image_path,
                prompt=prompt,
                max_length=max_length,
            )
            token_count += generated_tokens
        inference_seconds = time.perf_counter() - inference_start

    page_count = len(rendered_pages)
    end_to_end_seconds = model_load_seconds + render_seconds + inference_seconds

    return {
        "pdf_path": str(pdf_path),
        "model_dir": str(model_dir),
        "provider": provider,
        "page_count": page_count,
        "render_longest_dim": longest_dim,
        "max_length": max_length,
        "warmup_pages": len(warmup_subset),
        "generated_tokens": token_count,
        "model_load_seconds": round(model_load_seconds, 4),
        "render_seconds": round(render_seconds, 4),
        "warmup_seconds": round(warmup_seconds, 4),
        "inference_seconds": round(inference_seconds, 4),
        "end_to_end_seconds": round(end_to_end_seconds, 4),
        "seconds_per_page_inference": round(inference_seconds / page_count, 4),
        "pages_per_second_inference": round(page_count / inference_seconds, 4),
        "pages_per_second_render_plus_inference": round(
            page_count / (render_seconds + inference_seconds), 4
        ),
    }


def benchmark_lighton_ocr_models(
    pdf_path: str | Path,
    *,
    models: list[tuple[str, str | Path]],
    provider: str = "cpu",
    max_pages: int | None = None,
    longest_dim: int = 1540,
    prompt: str = DEFAULT_LIGHTON_PROMPT,
    max_length: int = 4096,
    warmup_pages: int = 1,
    reference_text: str | None = None,
    include_pymupdf_baseline: bool = True,
) -> dict:
    """Benchmark multiple LightOn OCR models on a shared set of rendered pages."""
    if not models:
        raise ValueError("models must contain at least one (label, model_dir) entry")

    reference_metrics_enabled = reference_text is not None and max_pages is None

    with tempfile.TemporaryDirectory() as tmpdir:
        render_start = time.perf_counter()
        rendered_pages = render_pdf_pages(
            pdf_path,
            tmpdir,
            max_pages=max_pages,
            longest_dim=longest_dim,
        )
        render_seconds = time.perf_counter() - render_start

        if not rendered_pages:
            raise RuntimeError("No pages rendered from the PDF")

        runs: list[dict] = []
        for label, model_dir in models:
            load_start = time.perf_counter()
            model = _load_model(model_dir, provider=provider)
            processor = model.create_multimodal_processor()
            model_load_seconds = time.perf_counter() - load_start

            og, _ = _require_lighton_runtime()
            warmup_subset = rendered_pages[:max(0, warmup_pages)]
            warmup_seconds = 0.0
            if warmup_subset:
                warmup_start = time.perf_counter()
                for rendered in warmup_subset:
                    _run_lighton_page_ocr(
                        og=og,
                        model=model,
                        processor=processor,
                        page_image=rendered.image_path,
                        prompt=prompt,
                        max_length=max_length,
                    )
                warmup_seconds = time.perf_counter() - warmup_start

            token_count = 0
            ocr_pages: list[LightOnOcrPage] = []
            inference_start = time.perf_counter()
            for rendered in rendered_pages:
                text, generated_tokens = _run_lighton_page_ocr(
                    og=og,
                    model=model,
                    processor=processor,
                    page_image=rendered.image_path,
                    prompt=prompt,
                    max_length=max_length,
                )
                token_count += generated_tokens
                ocr_pages.append(
                    LightOnOcrPage(
                        page_index=rendered.page_index,
                        image_path=rendered.image_path,
                        width=rendered.width,
                        height=rendered.height,
                        text=text,
                        generated_tokens=generated_tokens,
                    )
                )
            inference_seconds = time.perf_counter() - inference_start

            full_text = "\n\n".join(page.text for page in ocr_pages if page.text.strip())
            image_box_count = sum(len(extract_image_boxes(page.text)) for page in ocr_pages)

            run = {
                "label": label,
                "model_dir": str(model_dir),
                "page_count": len(ocr_pages),
                "generated_tokens": token_count,
                "image_box_count": image_box_count,
                "model_load_seconds": round(model_load_seconds, 4),
                "warmup_seconds": round(warmup_seconds, 4),
                "inference_seconds": round(inference_seconds, 4),
                "seconds_per_page_inference": round(inference_seconds / len(ocr_pages), 4),
                "pages_per_second_inference": round(len(ocr_pages) / inference_seconds, 4),
                "pages_per_second_render_plus_inference": round(
                    len(ocr_pages) / (render_seconds + inference_seconds), 4
                ),
                "text_preview": full_text[:1000],
            }
            if reference_metrics_enabled:
                run["reference_metrics"] = compute_text_similarity(reference_text, full_text)
            runs.append(run)

    baseline_runs = benchmark_parser_baselines(
        pdf_path,
        reference_text=reference_text,
        include_pymupdf=include_pymupdf_baseline,
    )

    all_runs = baseline_runs + runs
    summary: dict[str, str | None] = {
        "fastest_inference": max(runs, key=lambda r: r["pages_per_second_inference"])["label"],
        "most_image_boxes": max(runs, key=lambda r: r["image_box_count"])["label"],
        "fastest_overall_extractor": max(
            all_runs,
            key=lambda r: r.get("pages_per_second_inference", r.get("pages_per_second", 0.0)),
        )["label"],
    }
    if reference_metrics_enabled:
        summary["best_reference_token_f1"] = max(
            all_runs,
            key=lambda r: r["reference_metrics"]["token_f1"],
        )["label"]
        summary["best_reference_sequence_ratio"] = max(
            all_runs,
            key=lambda r: r["reference_metrics"]["sequence_ratio"],
        )["label"]
    else:
        summary["best_reference_token_f1"] = None
        summary["best_reference_sequence_ratio"] = None

    return {
        "pdf_path": str(pdf_path),
        "provider": provider,
        "page_count": len(rendered_pages),
        "render_longest_dim": longest_dim,
        "max_length": max_length,
        "warmup_pages": max(0, warmup_pages),
        "render_seconds_shared": round(render_seconds, 4),
        "reference_metrics_enabled": reference_metrics_enabled,
        "reference_metrics_reason": (
            "enabled"
            if reference_metrics_enabled
            else "reference text missing or max_pages requested without page-aligned reference"
        ),
        "baseline_runs": baseline_runs,
        "summary": summary,
        "runs": runs,
    }


def extract_image_boxes(text: str) -> list[tuple[int, int, int, int]]:
    """Parse LightOn bbox-soup image markers from OCR text."""
    boxes: list[tuple[int, int, int, int]] = []
    for match in _IMAGE_BOX_RE.finditer(text):
        x1, y1, x2, y2 = (int(match.group(i)) for i in range(2, 6))
        boxes.append((x1, y1, x2, y2))
    return boxes


def normalized_bbox_to_pixels(
    bbox_norm: tuple[int, int, int, int],
    *,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    """Convert LightOn's [0,1000] bbox coordinates into pixel coordinates."""
    x1, y1, x2, y2 = bbox_norm
    x1_px = max(0, min(width, round(x1 * width / 1000)))
    y1_px = max(0, min(height, round(y1 * height / 1000)))
    x2_px = max(0, min(width, round(x2 * width / 1000)))
    y2_px = max(0, min(height, round(y2 * height / 1000)))
    return x1_px, y1_px, x2_px, y2_px


def normalize_ocr_text(text: str) -> str:
    """Normalize OCR text for similarity scoring."""
    text = _IMAGE_BOX_RE.sub(" ", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def benchmark_parser_baselines(
    pdf_path: str | Path,
    *,
    reference_text: str | None = None,
    include_pymupdf: bool = True,
    max_pages: int | None = None,
) -> list[dict]:
    """Benchmark built-in text extraction baselines against optional reference text."""
    baseline_runs: list[dict] = []
    pdf_path = Path(pdf_path)

    if include_pymupdf:
        import pymupdf

        from .parsers import _extract_page_text

        doc = pymupdf.open(str(pdf_path))
        try:
            page_count = doc.page_count if max_pages is None else min(doc.page_count, max_pages)

            start = time.perf_counter()
            pages = [_extract_page_text(doc[page_index]) for page_index in range(page_count)]
            text = "\n\n".join(pages)
            elapsed = time.perf_counter() - start
        finally:
            doc.close()

        run = {
            "label": "pymupdf",
            "page_count": page_count,
            "parse_seconds": round(elapsed, 4),
            "seconds_per_page": round(elapsed / page_count, 4) if page_count else None,
            "pages_per_second": round(page_count / elapsed, 4) if elapsed > 0 else None,
            "text_preview": text[:1000],
        }
        if reference_text is not None:
            run["reference_metrics"] = compute_text_similarity(reference_text, text)
        baseline_runs.append(run)

    return baseline_runs


def resolve_lighton_onnx_repo(alias_or_repo_id: str) -> str:
    """Resolve a friendly alias to a concrete Hugging Face repo id."""
    value = alias_or_repo_id.strip()
    return LIGHTON_ONNX_MODEL_ALIASES.get(value, value)


def download_lighton_onnx_model(
    alias_or_repo_id: str,
    *,
    output_dir: str | Path | None = None,
    revision: str | None = None,
) -> str:
    """Download a LightOn ONNX model snapshot from Hugging Face."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise ImportError(
            "Downloading LightOn ONNX models requires huggingface_hub. "
            "Install with: pip install 'openaireview[lighton]'"
        ) from e

    repo_id = resolve_lighton_onnx_repo(alias_or_repo_id)
    kwargs = {
        "repo_id": repo_id,
    }
    if output_dir is not None:
        kwargs["local_dir"] = str(output_dir)
        kwargs["local_dir_use_symlinks"] = False
    if revision is not None:
        kwargs["revision"] = revision

    path = snapshot_download(**kwargs)
    return str(path)


def compute_text_similarity(reference_text: str, candidate_text: str) -> dict:
    """Compute lightweight text similarity metrics for OCR comparisons."""
    ref_norm = normalize_ocr_text(reference_text)
    cand_norm = normalize_ocr_text(candidate_text)

    ref_tokens = re.findall(r"[a-z0-9]+", ref_norm)
    cand_tokens = re.findall(r"[a-z0-9]+", cand_norm)
    ref_counts = Counter(ref_tokens)
    cand_counts = Counter(cand_tokens)
    overlap = sum((ref_counts & cand_counts).values())

    precision = overlap / sum(cand_counts.values()) if cand_counts else 0.0
    recall = overlap / sum(ref_counts.values()) if ref_counts else 0.0
    if precision + recall:
        token_f1 = 2 * precision * recall / (precision + recall)
    else:
        token_f1 = 0.0

    sequence_ratio = difflib.SequenceMatcher(
        None,
        ref_norm,
        cand_norm,
        autojunk=False,
    ).ratio()

    return {
        "reference_chars": len(ref_norm),
        "candidate_chars": len(cand_norm),
        "reference_tokens": len(ref_tokens),
        "candidate_tokens": len(cand_tokens),
        "token_precision": round(precision, 4),
        "token_recall": round(recall, 4),
        "token_f1": round(token_f1, 4),
        "sequence_ratio": round(sequence_ratio, 4),
    }


def extract_figures_from_pdf(
    pdf_path: str | Path,
    *,
    model_dir: str | Path,
    output_dir: str | Path,
    provider: str = "cpu",
    max_pages: int | None = None,
    longest_dim: int = 1540,
    prompt: str = DEFAULT_LIGHTON_PROMPT,
    max_length: int = 4096,
) -> tuple[list[LightOnFigure], list[LightOnOcrPage]]:
    """Extract figure crops from bbox-capable LightOn OCR output."""
    _, Image = _require_lighton_runtime(require_pillow=True)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        rendered_pages = render_pdf_pages(
            pdf_path,
            tmpdir,
            max_pages=max_pages,
            longest_dim=longest_dim,
        )

        load_start = time.perf_counter()
        model = _load_model(model_dir, provider=provider)
        processor = model.create_multimodal_processor()
        _ = time.perf_counter() - load_start

        og, _ = _require_lighton_runtime()
        ocr_pages: list[LightOnOcrPage] = []
        figures: list[LightOnFigure] = []
        for rendered in rendered_pages:
            text, token_count = _run_lighton_page_ocr(
                og=og,
                model=model,
                processor=processor,
                page_image=rendered.image_path,
                prompt=prompt,
                max_length=max_length,
            )
            ocr_pages.append(
                LightOnOcrPage(
                    page_index=rendered.page_index,
                    image_path=rendered.image_path,
                    width=rendered.width,
                    height=rendered.height,
                    text=text,
                    generated_tokens=token_count,
                )
            )

            boxes = extract_image_boxes(text)
            if not boxes:
                continue

            with Image.open(rendered.image_path) as page_image:
                for figure_index, bbox_norm in enumerate(boxes, start=1):
                    bbox_pixels = normalized_bbox_to_pixels(
                        bbox_norm,
                        width=rendered.width,
                        height=rendered.height,
                    )
                    x1, y1, x2, y2 = bbox_pixels
                    if x2 <= x1 or y2 <= y1:
                        continue
                    crop = page_image.crop((x1, y1, x2, y2))
                    crop_path = output_dir / (
                        f"page-{rendered.page_index + 1:04d}-figure-{figure_index:02d}.png"
                    )
                    crop.save(crop_path)
                    figures.append(
                        LightOnFigure(
                            page_index=rendered.page_index,
                            figure_index=figure_index,
                            bbox_norm=bbox_norm,
                            bbox_pixels=bbox_pixels,
                            crop_path=crop_path,
                        )
                    )

    return figures, ocr_pages


def _run_lighton_page_ocr(
    *,
    og,
    model,
    processor,
    page_image: Path,
    prompt: str,
    max_length: int,
) -> tuple[str, int]:
    """Run one image through the model and decode the generated text."""
    images = og.Images.open(str(page_image))
    inputs = processor(prompt=prompt, images=images)
    params = og.GeneratorParams(model)
    params.set_inputs(inputs)
    params.set_search_options(max_length=max_length)

    generator = og.Generator(model, params)
    tokens: list[int] = []
    while not generator.is_done():
        generator.compute_logits()
        generator.generate_next_token()
        next_tokens = generator.get_next_tokens()
        if len(next_tokens):
            tokens.append(int(next_tokens[0]))

    if hasattr(processor, "decode"):
        return processor.decode(tokens).strip(), len(tokens)
    if hasattr(model, "decode"):
        return model.decode(tokens).strip(), len(tokens)
    raise RuntimeError("Unable to decode output tokens from onnxruntime-genai processor")
