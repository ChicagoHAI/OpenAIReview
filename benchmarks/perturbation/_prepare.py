"""Input-staging logic used by run_benchmark.py.

Inputs (produced by the upstream perturbation generator + verifier + reinject
pipeline; see `analyses/verify_existing.py` and `reinject_existing.py`):

    <input_dir>/<paper_id>/<error_type>/<slug>_recorrupted.md
    <input_dir>/<paper_id>/<error_type>/<slug>_kept_perturbations.json

Outputs (the layout `run_benchmark.py`'s review and score stages walk):

    <results_dir>/perturb/<error_type>/paper_NNN/paper_NNN_corrupted.md
    <results_dir>/perturb/<error_type>/paper_NNN/paper_NNN_perturbations.json
    <results_dir>/paper_index.json     (paper_NNN -> real paper_id)

This module owns three things:

  1. Discovery — walk the input tree and assign stable `paper_NNN` labels.
  2. Truncation — clip each corrupted markdown to `max_tokens` tokens (so the
     review LLM call fits its context).
  3. Reachability filter — when truncation cuts mid-paper, drop perturbations
     whose `perturbed` text no longer appears in the truncated content (else
     the score stage would never find them and inflate the false-negative
     rate). Heuristic: substring match on a normalized form; a perturbation
     mentioned earlier in the kept text would pass even if its real location
     was cut, but in practice perturbations are spread across the paper and
     this rarely fires.

Re-running prepare on an existing `<results_dir>` re-stages from source
every time, so config changes (`max_tokens`, `min_perturbations`) always
take effect. Staged files are overwritten, never read for their content.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from reviewer.utils import _normalize_for_match, count_tokens, truncate_text


@dataclass(frozen=True)
class Unit:
    paper_label: str           # paper_001
    paper_id: str              # 2604.17935v1
    error_type: str            # surface | logic | claim_theoretical
    src_corrupted: Path        # original *_recorrupted.md
    src_manifest: Path         # original *_kept_perturbations.json
    staged_corrupted: Path     # <results>/perturb/<err>/paper_NNN/paper_NNN_corrupted.md
    staged_manifest: Path      # <results>/perturb/<err>/paper_NNN/paper_NNN_perturbations.json


def discover_units(input_dir: Path, results_dir: Path) -> list[Unit]:
    """Walk input_dir/<paper>/<err>/ and assign paper_NNN labels in sorted order."""
    paper_ids = sorted(p.name for p in input_dir.iterdir() if p.is_dir())
    units: list[Unit] = []
    for idx, paper_id in enumerate(paper_ids, start=1):
        paper_dir = input_dir / paper_id
        paper_label = f"paper_{idx:03d}"
        for err_dir in sorted(paper_dir.iterdir()):
            if not err_dir.is_dir():
                continue
            corrupted = next(iter(sorted(err_dir.glob("*_recorrupted.md"))), None)
            manifest = next(iter(sorted(err_dir.glob("*_kept_perturbations.json"))), None)
            if not corrupted or not manifest:
                continue
            stage_dir = results_dir / "perturb" / err_dir.name / paper_label
            units.append(Unit(
                paper_label=paper_label,
                paper_id=paper_id,
                error_type=err_dir.name,
                src_corrupted=corrupted,
                src_manifest=manifest,
                staged_corrupted=stage_dir / f"{paper_label}_corrupted.md",
                staged_manifest=stage_dir / f"{paper_label}_perturbations.json",
            ))
    return units


def _filter_reachable(perturbations: list[dict], normalized_text: str) -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    dropped: list[str] = []
    for p in perturbations:
        norm = _normalize_for_match(p.get("perturbed", ""))
        if norm and norm in normalized_text:
            kept.append(p)
        else:
            dropped.append(p.get("perturbation_id", "?"))
    return kept, dropped


def prepare_units(units: list[Unit], results_dir: Path, max_tokens: int,
                  min_perturbations: int = 0) -> tuple[list[Unit], dict]:
    """Stage corrupted.md (truncated) and filtered manifest into results_dir.

    Always re-stages from source: existing staged files are overwritten so
    `max_tokens` and `min_perturbations` changes always take effect. Units
    with fewer than `min_perturbations` reachable perturbations after
    truncation are excluded — any stale staged files for them are removed
    so a downstream walk sees a clean state. Returns (kept_units, report).
    """
    report: dict = {"max_tokens": max_tokens, "min_perturbations": min_perturbations, "units": []}
    kept_units: list[Unit] = []
    for u in units:
        u.staged_corrupted.parent.mkdir(parents=True, exist_ok=True)

        raw = u.src_corrupted.read_text()
        tokens_in = count_tokens(raw)
        truncated = truncate_text(raw, max_tokens) if tokens_in > max_tokens else raw
        tokens_out = count_tokens(truncated)

        manifest = json.loads(u.src_manifest.read_text())
        perturbations = manifest.get("perturbations", [])
        normalized_text = _normalize_for_match(truncated)
        kept, dropped = _filter_reachable(perturbations, normalized_text)

        row = {
            "paper_label": u.paper_label,
            "paper_id": u.paper_id,
            "error_type": u.error_type,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "perturbations_in": len(perturbations),
            "perturbations_out": len(kept),
            "perturbations_dropped": len(dropped),
        }

        if len(kept) < min_perturbations:
            row["excluded_by_min_perturbations"] = True
            # Remove any stale staged files from a prior run with looser thresholds.
            u.staged_corrupted.unlink(missing_ok=True)
            u.staged_manifest.unlink(missing_ok=True)
            report["units"].append(row)
            continue

        u.staged_corrupted.write_text(truncated)
        out_manifest = {
            **{k: v for k, v in manifest.items() if k != "perturbations"},
            "n_kept_after_truncation": len(kept),
            "n_dropped_after_truncation": len(dropped),
            "dropped_after_truncation": dropped,
            "perturbations": kept,
        }
        u.staged_manifest.write_text(json.dumps(out_manifest, indent=2))
        kept_units.append(u)
        report["units"].append(row)

    return kept_units, report


def write_paper_index(units: list[Unit], results_dir: Path) -> None:
    index = {u.paper_label: u.paper_id for u in units}
    (results_dir / "paper_index.json").write_text(json.dumps(index, indent=2, sort_keys=True))
