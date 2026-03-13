"""Optional LightOn OCR helpers using the official Transformers runtime."""

from __future__ import annotations

import tempfile
import time
from itertools import islice
from pathlib import Path

from .lighton import (
    RenderedPage,
    benchmark_parser_baselines,
    compute_text_similarity,
    extract_image_boxes,
)


LIGHTON_TRANSFORMERS_MODEL_ALIASES = {
    "plain": "lightonai/LightOnOCR-2-1B",
    "bbox": "lightonai/LightOnOCR-2-1B-bbox",
    "bbox-soup": "lightonai/LightOnOCR-2-1B-bbox-soup",
}

LIGHTON_TRANSFORMERS_SCALE_FACTOR = 2.77


def resolve_lighton_transformers_model(alias_or_repo_id: str) -> str:
    """Resolve a friendly alias to a LightOn Transformers model id."""
    value = alias_or_repo_id.strip()
    return LIGHTON_TRANSFORMERS_MODEL_ALIASES.get(value, value)


def download_lighton_transformers_model(
    alias_or_repo_id: str,
    *,
    output_dir: str | Path | None = None,
    revision: str | None = None,
) -> str:
    """Download a LightOn Transformers model snapshot from Hugging Face."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise ImportError(
            "Downloading LightOn Transformers models requires huggingface_hub. "
            "Install transformers or huggingface_hub first."
        ) from e

    repo_id = resolve_lighton_transformers_model(alias_or_repo_id)
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


def clean_lighton_output(text: str) -> str:
    """Remove the assistant prefix emitted by the chat template."""
    lines = text.splitlines()
    while lines and lines[0].strip().lower() in {"", "system", "user", "assistant"}:
        lines = lines[1:]
    return "\n".join(lines).strip()


def compute_pdfium_render_scale(
    width: float,
    height: float,
    *,
    longest_dim: int = 1540,
    scale_factor: float = LIGHTON_TRANSFORMERS_SCALE_FACTOR,
) -> float:
    """Match LightOn's published PDF render sizing logic."""
    if width <= 0 or height <= 0:
        raise ValueError("page width and height must be > 0")
    if longest_dim <= 0:
        raise ValueError("longest_dim must be > 0")
    if scale_factor <= 0:
        raise ValueError("scale_factor must be > 0")

    pixel_width = width * scale_factor
    pixel_height = height * scale_factor
    resize_factor = min(1.0, longest_dim / pixel_width, longest_dim / pixel_height)
    return scale_factor * resize_factor


def decode_generated_text(processor, output_ids, *, prompt_tokens: int) -> tuple[str, int]:
    """Decode only the generated continuation, excluding prompt tokens."""
    generated_ids = output_ids[prompt_tokens:]
    token_count = int(generated_ids.shape[-1] if hasattr(generated_ids, "shape") else len(generated_ids))
    text = processor.decode(generated_ids, skip_special_tokens=True)
    return clean_lighton_output(text), token_count


def chunked(values, batch_size: int):
    """Yield fixed-size chunks from an in-memory sequence."""
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")
    iterator = iter(values)
    while True:
        batch = list(islice(iterator, batch_size))
        if not batch:
            return
        yield batch


def _require_transformers_runtime():
    """Import the optional runtime pieces on demand."""
    try:
        import pypdfium2
        import torch
        from transformers import LightOnOcrForConditionalGeneration, LightOnOcrProcessor
    except ImportError as e:
        raise ImportError(
            "LightOn Transformers benchmarking requires the optional dependency set. "
            "Install with: pip install 'openaireview[lighton-transformers]' "
            "and install torch separately for your platform."
        ) from e

    return pypdfium2, torch, LightOnOcrForConditionalGeneration, LightOnOcrProcessor


def _resolve_device(torch_module, device: str) -> str:
    """Resolve auto/cpu/cuda/mps to an available device string."""
    device = device.strip().lower()
    if device not in {"auto", "cpu", "cuda", "mps"}:
        raise ValueError("device must be one of: auto, cpu, cuda, mps")

    if device == "auto":
        if torch_module.cuda.is_available():
            return "cuda"
        if hasattr(torch_module.backends, "mps") and torch_module.backends.mps.is_available():
            return "mps"
        return "cpu"

    if device == "cuda" and not torch_module.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    if device == "mps":
        if not hasattr(torch_module.backends, "mps") or not torch_module.backends.mps.is_available():
            raise RuntimeError("MPS requested but torch.backends.mps.is_available() is false")
    return device


def _resolve_dtype(torch_module, device: str, dtype: str):
    """Choose a practical dtype for the selected device."""
    dtype = dtype.strip().lower()
    if dtype not in {"auto", "float32", "float16", "bfloat16"}:
        raise ValueError("dtype must be one of: auto, float32, float16, bfloat16")

    if dtype == "auto":
        if device == "cuda":
            return torch_module.bfloat16, "bfloat16"
        if device == "mps":
            return torch_module.float16, "float16"
        return torch_module.float32, "float32"

    mapping = {
        "float32": torch_module.float32,
        "float16": torch_module.float16,
        "bfloat16": torch_module.bfloat16,
    }
    return mapping[dtype], dtype


def _resolve_attn_implementation(torch_module, device: str) -> str:
    """Pick a practical attention backend matching LightOn's demo defaults."""
    if device == "cuda":
        return "sdpa"
    return "eager"


def render_pdf_pages_pdfium(
    pdf_path: str | Path,
    output_dir: str | Path,
    *,
    max_pages: int | None = None,
    longest_dim: int = 1540,
    scale_factor: float = LIGHTON_TRANSFORMERS_SCALE_FACTOR,
) -> list[RenderedPage]:
    """Render pages with pypdfium2 following LightOn's published settings."""
    pypdfium2, _, _, _ = _require_transformers_runtime()

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf = pypdfium2.PdfDocument(str(pdf_path))
    page_count = len(pdf) if max_pages is None else min(len(pdf), max_pages)
    rendered: list[RenderedPage] = []

    for page_index in range(page_count):
        page = pdf[page_index]
        width, height = page.get_size()
        render_scale = compute_pdfium_render_scale(
            width,
            height,
            longest_dim=longest_dim,
            scale_factor=scale_factor,
        )
        pil_image = page.render(scale=render_scale).to_pil()
        image_path = output_dir / f"page-{page_index + 1:04d}.png"
        pil_image.save(image_path)
        rendered.append(
            RenderedPage(
                page_index=page_index,
                image_path=image_path,
                width=pil_image.width,
                height=pil_image.height,
            )
        )
        page.close()

    pdf.close()
    return rendered


def _load_transformers_model(
    model_id: str,
    *,
    device: str,
    dtype: str,
):
    """Load the official LightOn Transformers model and processor."""
    _, torch_module, model_cls, processor_cls = _require_transformers_runtime()
    resolved_device = _resolve_device(torch_module, device)
    torch_dtype, dtype_name = _resolve_dtype(torch_module, resolved_device, dtype)
    attn_implementation = _resolve_attn_implementation(torch_module, resolved_device)

    processor = processor_cls.from_pretrained(
        model_id,
        trust_remote_code=True,
    )
    model = model_cls.from_pretrained(
        model_id,
        attn_implementation=attn_implementation,
        torch_dtype=torch_dtype,
        trust_remote_code=True,
    )
    model.to(resolved_device)
    model.eval()
    for field in ("temperature", "top_p", "top_k"):
        if hasattr(model.generation_config, field):
            setattr(model.generation_config, field, None)
    return processor, model, resolved_device, dtype_name


def _move_inputs_to_device(inputs, *, device: str, torch_dtype):
    """Move only tensor values to the target device, casting floating tensors."""
    moved = {}
    for key, value in inputs.items():
        if hasattr(value, "to"):
            if getattr(value, "is_floating_point", None) and value.is_floating_point():
                moved[key] = value.to(device=device, dtype=torch_dtype)
            else:
                moved[key] = value.to(device=device)
        else:
            moved[key] = value
    return moved


def _synchronize_device(torch_module, device: str) -> None:
    """Synchronize the active accelerator before timing boundaries."""
    if device == "cuda" and torch_module.cuda.is_available():
        torch_module.cuda.synchronize()
    elif (
        device == "mps"
        and hasattr(torch_module, "mps")
        and hasattr(torch_module.mps, "synchronize")
    ):
        torch_module.mps.synchronize()


def _run_transformers_page_ocr(
    *,
    processor,
    model,
    rendered_page: RenderedPage,
    device: str,
    torch_dtype,
    max_new_tokens: int,
) -> tuple[str, int]:
    """Run OCR on a single rendered page."""
    from PIL import Image

    with Image.open(rendered_page.image_path) as page_image:
        image = page_image.convert("RGB")
    messages = [
        {
            "role": "user",
            "content": [{"type": "image", "url": image}],
        }
    ]
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    )
    inputs = _move_inputs_to_device(inputs, device=device, torch_dtype=torch_dtype)

    prompt_tokens = inputs["input_ids"].shape[-1] if "input_ids" in inputs else 0

    import torch

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
        )

    output_ids = outputs[0]
    return decode_generated_text(
        processor,
        output_ids,
        prompt_tokens=prompt_tokens,
    )


def _run_transformers_batch_ocr(
    *,
    processor,
    model,
    rendered_pages: list[RenderedPage],
    device: str,
    torch_dtype,
    max_new_tokens: int,
) -> list[tuple[str, int]]:
    """Run OCR on a batch of rendered pages."""
    from PIL import Image
    import torch

    images = []
    try:
        for rendered_page in rendered_pages:
            with Image.open(rendered_page.image_path) as page_image:
                images.append(page_image.convert("RGB"))

        messages = [
            [
                {
                    "role": "user",
                    "content": [{"type": "image", "url": image}],
                }
            ]
            for image in images
        ]
        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
            padding=True,
        )
    finally:
        for image in images:
            image.close()

    inputs = _move_inputs_to_device(inputs, device=device, torch_dtype=torch_dtype)
    prompt_tokens = inputs["input_ids"].shape[-1] if "input_ids" in inputs else 0

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            use_cache=True,
        )

    return [
        decode_generated_text(
            processor,
            output_ids,
            prompt_tokens=prompt_tokens,
        )
        for output_ids in outputs
    ]


def benchmark_lighton_transformers_models(
    pdf_path: str | Path,
    *,
    models: list[tuple[str, str]],
    device: str = "auto",
    dtype: str = "auto",
    max_pages: int | None = None,
    longest_dim: int = 1540,
    max_new_tokens: int = 4096,
    warmup_pages: int = 1,
    batch_size: int = 1,
    reference_text: str | None = None,
    include_pymupdf_baseline: bool = True,
    torch_num_threads: int | None = None,
) -> dict:
    """Benchmark one or more LightOn Transformers models on the same PDF."""
    if not models:
        raise ValueError("models must contain at least one (label, model_id) entry")

    _, torch_module, _, _ = _require_transformers_runtime()
    if torch_num_threads is not None and torch_num_threads > 0:
        torch_module.set_num_threads(torch_num_threads)
    if batch_size <= 0:
        raise ValueError("batch_size must be > 0")

    reference_metrics_enabled = reference_text is not None and max_pages is None

    with tempfile.TemporaryDirectory() as tmpdir:
        render_start = time.perf_counter()
        rendered_pages = render_pdf_pages_pdfium(
            pdf_path,
            tmpdir,
            max_pages=max_pages,
            longest_dim=longest_dim,
        )
        render_seconds = time.perf_counter() - render_start

        if not rendered_pages:
            raise RuntimeError("No pages rendered from the PDF")

        runs: list[dict] = []
        for label, model_spec in models:
            model_id = resolve_lighton_transformers_model(model_spec)

            load_start = time.perf_counter()
            processor, model, resolved_device, dtype_name = _load_transformers_model(
                model_id,
                device=device,
                dtype=dtype,
            )
            model_load_seconds = time.perf_counter() - load_start

            torch_dtype = next(model.parameters()).dtype
            warmup_subset = rendered_pages[:max(0, warmup_pages)]
            warmup_seconds = 0.0
            if warmup_subset:
                _synchronize_device(torch_module, resolved_device)
                warmup_start = time.perf_counter()
                for rendered_batch in chunked(warmup_subset, batch_size):
                    _run_transformers_batch_ocr(
                        processor=processor,
                        model=model,
                        rendered_pages=rendered_batch,
                        device=resolved_device,
                        torch_dtype=torch_dtype,
                        max_new_tokens=max_new_tokens,
                    )
                _synchronize_device(torch_module, resolved_device)
                warmup_seconds = time.perf_counter() - warmup_start

            token_count = 0
            page_texts: list[str] = []
            image_box_count = 0
            _synchronize_device(torch_module, resolved_device)
            inference_start = time.perf_counter()
            for rendered_batch in chunked(rendered_pages, batch_size):
                results = _run_transformers_batch_ocr(
                    processor=processor,
                    model=model,
                    rendered_pages=rendered_batch,
                    device=resolved_device,
                    torch_dtype=torch_dtype,
                    max_new_tokens=max_new_tokens,
                )
                for text, generated_tokens in results:
                    token_count += generated_tokens
                    page_texts.append(text)
                    image_box_count += len(extract_image_boxes(text))
            _synchronize_device(torch_module, resolved_device)
            inference_seconds = time.perf_counter() - inference_start

            full_text = "\n\n".join(text for text in page_texts if text.strip())
            run = {
                "label": label,
                "model_id": model_id,
                "page_count": len(rendered_pages),
                "device": resolved_device,
                "dtype": dtype_name,
                "batch_size": batch_size,
                "generated_tokens": token_count,
                "image_box_count": image_box_count,
                "model_load_seconds": round(model_load_seconds, 4),
                "warmup_seconds": round(warmup_seconds, 4),
                "inference_seconds": round(inference_seconds, 4),
                "seconds_per_page_inference": round(inference_seconds / len(rendered_pages), 4),
                "pages_per_second_inference": round(
                    len(rendered_pages) / inference_seconds, 4
                ),
                "pages_per_second_render_plus_inference": round(
                    len(rendered_pages) / (render_seconds + inference_seconds), 4
                ),
                "text_preview": full_text[:1000],
            }
            if reference_metrics_enabled:
                run["reference_metrics"] = compute_text_similarity(reference_text, full_text)
            runs.append(run)

            del model

    baseline_runs = benchmark_parser_baselines(
        pdf_path,
        reference_text=reference_text if reference_metrics_enabled else None,
        include_pymupdf=include_pymupdf_baseline,
        max_pages=max_pages,
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
        "runtime": "transformers",
        "page_count": len(rendered_pages),
        "render_longest_dim": longest_dim,
        "max_new_tokens": max_new_tokens,
        "warmup_pages": max(0, warmup_pages),
        "batch_size": batch_size,
        "render_seconds_shared": round(render_seconds, 4),
        "reference_metrics_enabled": reference_metrics_enabled,
        "reference_metrics_reason": (
            "enabled"
            if reference_metrics_enabled
            else "reference text missing or max_pages requested without page-aligned reference"
        ),
        "torch_num_threads": torch_num_threads,
        "baseline_runs": baseline_runs,
        "summary": summary,
        "runs": runs,
    }
