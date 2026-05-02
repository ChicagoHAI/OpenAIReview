"""Re-run the batched verifier on already-perturbed papers without regeneration.

Walks `--input-root` for `*_perturbations.json` files, reconstructs
`Perturbation` objects from each, re-extracts candidates from the matching
`_clean.md` (so `verifier_related_passages` and `span.context` are populated),
and runs `verify_perturbations_batched`. Writes per-paper verdict files to
`--output-root`, mirroring the input directory structure.

Output schema (`{slug}_verdicts.json`):
    {
      "paper_title": "...",
      "paper_slug": "...",
      "source_perturbations": "<relative path>",
      "verifier_model": "...",
      "stats": { "n_input": ..., "substantive": ..., ... },
      "verdicts": {
        "<perturbation_id>": {
          "error_type": "...",
          "verdict": "substantive" | "typo-shaped" | "not-an-error" | "parse-error",
          "reason": "...",
          "i1": "Y", "i2": "Y", "i3": "Y", "i4": "N",
          "original": "...",
          "perturbed": "...",
        },
        ...
      }
    }

Resumable: skips inputs whose output `_verdicts.json` already exists, unless
`--force` is set. A single `_perturbations.json` path can be passed instead of
`--input-root` to verify just that file.

Usage:
    python -m benchmarks.perturbation.analyses.verify_existing
    python -m benchmarks.perturbation.analyses.verify_existing --limit 5
    python -m benchmarks.perturbation.analyses.verify_existing path/to/_perturbations.json --force
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from threading import Lock

from ..extract import attach_verifier_related_passages, extract_candidates
from ..models import Error, Perturbation
from ..verify import DEFAULT_VERIFIER_MODEL, verify_perturbations_batched


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INPUT_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "data" / "perturbations"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "benchmarks" / "perturbation" / "results" / "error_verification"


def _paper_category_for(error_type_dir: str) -> str:
    """extract_candidates routes by paper category, not arxiv category."""
    if error_type_dir in ("statement_empirical", "experimental"):
        return "empirical"
    return "theoretical"


def _reconstruct(perts_json: list[dict]) -> list[Perturbation]:
    out: list[Perturbation] = []
    for p in perts_json:
        out.append(Perturbation(
            perturbation_id=p["perturbation_id"],
            span_id=p["span_id"],
            error=Error(p["error"]),
            original=p["original"],
            offset=p.get("offset", 0),
            perturbed=p["perturbed"],
            why_wrong=p.get("why_wrong", ""),
            contradicts_quote=p.get("contradicts_quote", ""),
        ))
    return out


def _verify_one_file(
    perts_path: Path,
    input_root: Path,
    output_root: Path,
    model: str,
    reasoning_effort: str | None,
    force: bool,
) -> str:
    """Process one _perturbations.json. Returns a status string for logging."""
    rel = perts_path.relative_to(input_root)
    out_dir = output_root / rel.parent
    slug = perts_path.name.replace("_perturbations.json", "")
    out_path = out_dir / f"{slug}_verdicts.json"

    if out_path.exists() and not force:
        return f"SKIP (exists): {rel}"

    clean_md = perts_path.with_name(f"{slug}_clean.md")
    if not clean_md.exists():
        return f"SKIP (no _clean.md): {rel}"

    try:
        data = json.loads(perts_path.read_text())
    except json.JSONDecodeError as e:
        return f"SKIP (bad JSON): {rel}: {e}"

    perts_json = data.get("perturbations", [])
    if not perts_json:
        return f"SKIP (empty): {rel}"

    paper_title = data.get("paper_title", "")
    paper_slug = data.get("paper_slug", slug)
    text = clean_md.read_text()

    # The error_type used for the run is the directory name immediately
    # containing the _perturbations.json file.
    error_type_run = perts_path.parent.name
    paper_category = _paper_category_for(error_type_run)

    candidates = extract_candidates(paper_category, error_type_run, text)
    attach_verifier_related_passages(candidates, text)

    perturbations = _reconstruct(perts_json)

    accepted, rejected, stats, verdict_map = verify_perturbations_batched(
        perturbations, candidates,
        paper_title=paper_title,
        model=model,
        reasoning_effort=reasoning_effort,
    )

    pert_by_pid = {p.perturbation_id: p for p in perturbations}
    verdicts_payload: dict[str, dict] = {}
    for pid, v in verdict_map.items():
        p = pert_by_pid.get(pid)
        verdicts_payload[pid] = {
            "error_type": p.error.value if p else "",
            "verdict": v.verdict,
            **v.items,
            "quote": v.quote,
            "reason": v.reason,
            "original": p.original if p else "",
            "perturbed": p.perturbed if p else "",
        }

    output = {
        "paper_title": paper_title,
        "paper_slug": paper_slug,
        "source_perturbations": str(rel),
        "verifier_model": model,
        "stats": stats,
        "verdicts": verdicts_payload,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    return f"OK ({stats['substantive']}/{stats['n_input']} substantive): {rel}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="*", type=Path,
                    help="One or more _perturbations.json files (overrides --input-root walking).")
    ap.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT,
                    help=f"Root to walk for _perturbations.json (default: {DEFAULT_INPUT_ROOT})")
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT,
                    help=f"Where verdict files are written (default: {DEFAULT_OUTPUT_ROOT})")
    ap.add_argument("--model", default=DEFAULT_VERIFIER_MODEL,
                    help=f"Verifier model (default: {DEFAULT_VERIFIER_MODEL})")
    ap.add_argument("--reasoning", default=None, choices=[None, "low", "medium", "high"],
                    help="Reasoning effort (default: none)")
    ap.add_argument("--limit", type=int, default=None,
                    help="Process at most N input files.")
    ap.add_argument("--force", action="store_true",
                    help="Re-process files that already have a verdict output.")
    ap.add_argument("--workers", type=int, default=1,
                    help="Number of parallel verification workers (1 = sequential).")
    args = ap.parse_args()

    input_root = args.input_root.resolve()
    output_root = args.output_root.resolve()

    if args.path:
        files = [p.resolve() for p in args.path]
        # Verify each is reachable under input_root; fall back to per-file parent
        # only if all paths share no common root with input_root.
        for p in files:
            try:
                p.relative_to(input_root)
            except ValueError:
                input_root = p.parent  # crude fallback for the last mismatch
    else:
        files = sorted(input_root.rglob("*_perturbations.json"))

    if args.limit:
        files = files[:args.limit]

    print(f"Verifying {len(files)} file(s) → {output_root} "
          f"(workers={args.workers})")
    t0 = time.time()
    counts = {"OK": 0, "SKIP": 0, "ERROR": 0}
    print_lock = Lock()
    progress = {"i": 0}

    def _process(f: Path) -> str:
        try:
            return _verify_one_file(f, input_root, output_root,
                                     args.model, args.reasoning, args.force)
        except Exception as e:
            return f"ERROR: {f.relative_to(input_root)}: {type(e).__name__}: {e}"

    if args.workers <= 1:
        for f in files:
            try:
                status = _process(f)
            except KeyboardInterrupt:
                print("\nInterrupted.", file=sys.stderr)
                break
            progress["i"] += 1
            bucket = "OK" if status.startswith("OK") else ("ERROR" if status.startswith("ERROR") else "SKIP")
            counts[bucket] = counts.get(bucket, 0) + 1
            elapsed = time.time() - t0
            print(f"[{progress['i']}/{len(files)}] ({elapsed:.0f}s) {status}")
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(_process, f): f for f in files}
            try:
                for fut in as_completed(futures):
                    status = fut.result()
                    with print_lock:
                        progress["i"] += 1
                        bucket = "OK" if status.startswith("OK") else ("ERROR" if status.startswith("ERROR") else "SKIP")
                        counts[bucket] = counts.get(bucket, 0) + 1
                        elapsed = time.time() - t0
                        print(f"[{progress['i']}/{len(files)}] ({elapsed:.0f}s) {status}")
            except KeyboardInterrupt:
                print("\nInterrupted; waiting for in-flight tasks…", file=sys.stderr)

    print(f"\nDone: {counts}")


if __name__ == "__main__":
    main()
