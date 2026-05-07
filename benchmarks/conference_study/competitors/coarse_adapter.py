"""Adapter for `coarse` (https://pypi.org/project/coarse-ink/).

coarse lives in its own venv (default: /data/dangnguyen/openaireview_project/coarse/.venv)
because its dep set (litellm, instructor, docling, ...) is large and version-sensitive
enough that keeping it out of openaireview's venv avoids accidental breakage in either
direction. The adapter subprocess-calls a small runner (_coarse_runner.py) inside that
venv and reads back a JSON payload.

Required config fields (configs/coarse.yaml):
    venv_python: path to the coarse venv's python executable
    coarse_options:
        skip_cost_gate: bool (default: true)

Required env:
    OPENROUTER_API_KEY — all three manifest models resolve via OpenRouter.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from .base import CompetitorAdapter, NormalizedComment, NormalizedReview
from .helpers import model_short

_RUNNER = Path(__file__).resolve().parent / "_coarse_runner.py"


def _to_openrouter_model(model: str) -> str:
    """Prefix OpenRouter's litellm route. openaireview manifest holds bare IDs
    like 'z-ai/glm-4.6'; litellm needs 'openrouter/z-ai/glm-4.6' to pick the
    right transport."""
    return model if model.startswith("openrouter/") else f"openrouter/{model}"


def _format_overall_feedback(fb: dict) -> str:
    """Flatten coarse's OverviewFeedback dict into the plain-string field
    openaireview's JSON schema expects."""
    parts: list[str] = []
    if fb.get("summary"):
        parts.append(fb["summary"].strip())
    if fb.get("assessment"):
        parts.append(fb["assessment"].strip())
    if fb.get("issues"):
        parts.append("Overview issues:")
        for issue in fb["issues"]:
            parts.append(f"- {issue['title']}: {issue['body'].strip()}")
    if fb.get("recommendation"):
        parts.append(f"Recommendation: {fb['recommendation'].strip()}")
    if fb.get("revision_targets"):
        parts.append("Revision targets:")
        for t in fb["revision_targets"]:
            parts.append(f"- {t}")
    return "\n\n".join(parts)


class CoarseAdapter(CompetitorAdapter):
    name = "coarse"
    required_env = ("OPENROUTER_API_KEY",)

    def method_key(self, model: str) -> str:
        return f"coarse__{model_short(model)}"

    def review(self, pdf: Path, model: str, cfg: dict) -> NormalizedReview:
        venv_python = cfg.get("venv_python")
        if not venv_python:
            raise RuntimeError(
                "coarse adapter requires `venv_python` in config "
                "(path to the coarse venv's python executable)"
            )
        venv_python = str(Path(venv_python).expanduser())
        if not Path(venv_python).exists():
            raise RuntimeError(f"coarse venv python not found: {venv_python}")

        coarse_opts = cfg.get("coarse_options", {}) or {}
        resolved_model = _to_openrouter_model(model)
        timeout_sec = int(cfg.get("timeout_sec", 1800))
        max_pages = cfg.get("max_pages")

        # Temp file shuttles the structured payload back from the subprocess
        # so coarse's own stdout logging doesn't have to be parsed.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False,
            prefix=f"coarse_{pdf.stem}_",
        ) as f:
            out_path = Path(f.name)
        # If max_pages is set, hand coarse a truncated copy of the PDF so
        # its review only covers the first N pages (matches the metric used
        # by openaireview's runs).
        truncated_pdf: Path | None = None
        pdf_for_coarse = pdf
        if max_pages:
            import fitz
            src = fitz.open(pdf)
            n_keep = min(int(max_pages), len(src))
            if n_keep < len(src):
                dst = fitz.open()
                dst.insert_pdf(src, from_page=0, to_page=n_keep - 1)
                with tempfile.NamedTemporaryFile(
                    suffix=".pdf", delete=False,
                    prefix=f"coarse_{pdf.stem}_first{n_keep}p_",
                ) as f:
                    truncated_pdf = Path(f.name)
                dst.save(truncated_pdf)
                dst.close()
                pdf_for_coarse = truncated_pdf
            src.close()
        try:
            cmd = [
                venv_python, str(_RUNNER),
                str(pdf_for_coarse), resolved_model,
                json.dumps({
                    "skip_cost_gate": coarse_opts.get("skip_cost_gate", True),
                    "gemini_internal_model": coarse_opts.get("gemini_internal_model"),
                }),
                str(out_path),
            ]
            # Inherit env (OPENROUTER_API_KEY etc.); stream subprocess output
            # to stderr so run_competitors.py's console log gets coarse's
            # progress bars and any tracebacks.
            result = subprocess.run(
                cmd,
                timeout=timeout_sec,
                stdout=sys.stderr, stderr=sys.stderr,
                env=os.environ.copy(),
                check=False,
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"coarse runner exited {result.returncode} "
                    f"(see stderr for traceback)"
                )
            if not out_path.exists() or out_path.stat().st_size == 0:
                raise RuntimeError("coarse runner did not write output JSON")

            payload = json.loads(out_path.read_text())
        finally:
            out_path.unlink(missing_ok=True)
            if truncated_pdf is not None:
                truncated_pdf.unlink(missing_ok=True)

        comments: list[NormalizedComment] = []
        for c in payload.get("comments", []):
            comments.append(
                NormalizedComment(
                    title=c["title"],
                    quote=c["quote"],
                    explanation=c["feedback"],
                    # coarse doesn't split technical/logical — default to
                    # "technical" so downstream filters don't drop these.
                    comment_type="technical",
                    extra={
                        "severity": c.get("severity"),
                        "confidence": c.get("confidence"),
                        "status": c.get("status"),
                        "coarse_number": c.get("number"),
                    },
                )
            )

        return NormalizedReview(
            comments=comments,
            overall_feedback=_format_overall_feedback(payload.get("overall_feedback", {})),
            cost_usd=payload.get("cost_usd"),
            cost_method=payload.get("cost_method", "estimated"),
            prompt_tokens=None,
            completion_tokens=None,
            model=payload.get("model", resolved_model),
        )
