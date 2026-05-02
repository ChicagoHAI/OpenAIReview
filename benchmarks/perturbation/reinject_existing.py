"""Re-inject perturbed papers using only the perturbations the new verifier
classifies as 'substantive'.

For each `_perturbations.json` in `--input-root` that has a matching
`_verdicts.json` in `--verdicts-root`, this script:

  1. Loads `_clean.md`.
  2. Loads the perturbation manifest.
  3. Loads the verdict file and filters to perturbations whose verdict is
     'substantive'.
  4. Re-extracts candidates from `_clean.md` to recover each surviving
     perturbation's offset (the manifest does not store offsets).
  5. Calls `inject_perturbations` to produce a re-corrupted paper containing
     only the surviving perturbations.
  6. Writes `<slug>_recorrupted.md` and `<slug>_kept_perturbations.json`
     alongside the verdict file under `--output-root`.

Resumable: skips inputs whose recorrupted output already exists, unless
`--force` is set. Pass paths positionally to scope to specific files.

Usage:
    python -m benchmarks.perturbation.reinject_existing
    python -m benchmarks.perturbation.reinject_existing --limit 5
    python -m benchmarks.perturbation.reinject_existing path/to/_perturbations.json --force
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .extract import extract_candidates
from .inject import inject_perturbations
from .models import Error, Perturbation


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "data" / "perturbations"
DEFAULT_VERDICTS_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "results" / "error_verification"
DEFAULT_OUTPUT_ROOT = DEFAULT_VERDICTS_ROOT


def _paper_category_for(error_type_dir: str) -> str:
    if error_type_dir in ("statement_empirical", "experimental"):
        return "empirical"
    return "theoretical"


def _reconstruct(perts_json: list[dict], offsets_by_span: dict[str, int]) -> list[Perturbation]:
    """Build Perturbation objects, looking up offsets via span_id."""
    out: list[Perturbation] = []
    missing: list[str] = []
    for p in perts_json:
        span_id = p["span_id"]
        offset = offsets_by_span.get(span_id)
        if offset is None:
            missing.append(p["perturbation_id"])
            continue
        out.append(Perturbation(
            perturbation_id=p["perturbation_id"],
            span_id=span_id,
            error=Error(p["error"]),
            original=p["original"],
            offset=offset,
            perturbed=p["perturbed"],
            why_wrong=p.get("why_wrong", ""),
            contradicts_quote=p.get("contradicts_quote", ""),
        ))
    return out, missing


def _reinject_one_file(
    perts_path: Path,
    input_root: Path,
    verdicts_root: Path,
    output_root: Path,
    force: bool,
) -> str:
    """Process one _perturbations.json. Returns a status string."""
    rel = perts_path.relative_to(input_root)
    slug = perts_path.name.replace("_perturbations.json", "")
    out_dir = output_root / rel.parent
    out_corrupted = out_dir / f"{slug}_recorrupted.md"
    out_kept = out_dir / f"{slug}_kept_perturbations.json"
    verdicts_path = verdicts_root / rel.parent / f"{slug}_verdicts.json"

    if out_corrupted.exists() and not force:
        return f"SKIP (exists): {rel}"

    if not verdicts_path.exists():
        return f"SKIP (no verdicts file): {rel}"

    clean_md = perts_path.with_name(f"{slug}_clean.md")
    if not clean_md.exists():
        return f"SKIP (no _clean.md): {rel}"

    try:
        manifest = json.loads(perts_path.read_text())
        verdict_data = json.loads(verdicts_path.read_text())
    except json.JSONDecodeError as e:
        return f"SKIP (bad JSON): {rel}: {e}"

    perts_all = manifest.get("perturbations", [])
    verdicts = verdict_data.get("verdicts", {})

    # Filter to substantive only.
    keep = [p for p in perts_all if verdicts.get(p["perturbation_id"], {}).get("verdict") == "substantive"]
    n_total = len(perts_all)
    n_keep = len(keep)
    n_drop = n_total - n_keep

    text = clean_md.read_text()

    # Re-extract candidates so we can recover offsets via span_id.
    error_type_run = perts_path.parent.name
    paper_category = _paper_category_for(error_type_run)
    candidates = extract_candidates(paper_category, error_type_run, text)
    offsets_by_span = {c.span_id: c.offset for c in candidates}

    perturbations, missing = _reconstruct(keep, offsets_by_span)

    if missing:
        # Recover via text.find as a last-resort fallback for spans the
        # extractor no longer surfaces (e.g. extractor changes since generation).
        recovered = []
        for p in keep:
            if p["perturbation_id"] not in {x.perturbation_id for x in perturbations} and p["perturbation_id"] in missing:
                offset = text.find(p["original"])
                if offset >= 0:
                    recovered.append(Perturbation(
                        perturbation_id=p["perturbation_id"],
                        span_id=p["span_id"],
                        error=Error(p["error"]),
                        original=p["original"],
                        offset=offset,
                        perturbed=p["perturbed"],
                        why_wrong=p.get("why_wrong", ""),
                        contradicts_quote=p.get("contradicts_quote", ""),
                    ))
        perturbations = perturbations + recovered

    if len(perturbations) != n_keep:
        return f"ERROR: only resolved {len(perturbations)}/{n_keep} kept perturbations: {rel}"

    corrupted, applied = inject_perturbations(text, perturbations)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_corrupted.write_text(corrupted)

    kept_payload = {
        "paper_title": manifest.get("paper_title", ""),
        "paper_slug": manifest.get("paper_slug", slug),
        "source_perturbations": str(rel),
        "source_verdicts": str(verdicts_path.relative_to(verdicts_root)),
        "n_total": n_total,
        "n_kept": len(applied),
        "n_dropped": n_drop,
        "perturbations": [
            {
                "perturbation_id": p.perturbation_id,
                "span_id": p.span_id,
                "error": p.error.value,
                "original": p.original,
                "perturbed": p.perturbed,
                "why_wrong": p.why_wrong,
                "verdict": "substantive",
                **{k: verdicts.get(p.perturbation_id, {}).get(k, "")
                   for k in ("i1", "i2", "i3", "i4", "quote", "reason")},
            }
            for p in applied
        ],
    }
    out_kept.write_text(json.dumps(kept_payload, indent=2))

    return f"OK (kept {len(applied)}/{n_total}, dropped {n_drop}): {rel}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="*", type=Path,
                    help="One or more _perturbations.json files (overrides --input-root walking).")
    ap.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT,
                    help=f"Root containing _perturbations.json + _clean.md (default: {DEFAULT_INPUT_ROOT})")
    ap.add_argument("--verdicts-root", type=Path, default=DEFAULT_VERDICTS_ROOT,
                    help=f"Root containing _verdicts.json mirrors (default: {DEFAULT_VERDICTS_ROOT})")
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT,
                    help=f"Where _recorrupted.md and _kept_perturbations.json are written (default: {DEFAULT_OUTPUT_ROOT})")
    ap.add_argument("--limit", type=int, default=None,
                    help="Process at most N input files.")
    ap.add_argument("--force", action="store_true",
                    help="Re-process files that already have a recorrupted output.")
    args = ap.parse_args()

    input_root = args.input_root.resolve()
    verdicts_root = args.verdicts_root.resolve()
    output_root = args.output_root.resolve()

    if args.path:
        files = [p.resolve() for p in args.path]
        for p in files:
            try:
                p.relative_to(input_root)
            except ValueError:
                input_root = p.parent
    else:
        files = sorted(input_root.rglob("*_perturbations.json"))

    if args.limit:
        files = files[:args.limit]

    print(f"Re-injecting {len(files)} file(s) → {output_root}")
    t0 = time.time()
    counts = {"OK": 0, "SKIP": 0, "ERROR": 0}
    for i, f in enumerate(files, 1):
        try:
            status = _reinject_one_file(f, input_root, verdicts_root, output_root, args.force)
        except KeyboardInterrupt:
            print("\nInterrupted.", file=sys.stderr)
            break
        except Exception as e:
            status = f"ERROR: {f.relative_to(input_root)}: {type(e).__name__}: {e}"
        bucket = "OK" if status.startswith("OK") else ("ERROR" if status.startswith("ERROR") else "SKIP")
        counts[bucket] = counts.get(bucket, 0) + 1
        elapsed = time.time() - t0
        print(f"[{i}/{len(files)}] ({elapsed:.0f}s) {status}")

    print(f"\nDone: {counts}")


if __name__ == "__main__":
    main()
