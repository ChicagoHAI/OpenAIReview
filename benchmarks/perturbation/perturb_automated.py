#!/usr/bin/env python3
"""Automated perturbation pipeline using the arXiv API.

Searches arXiv for papers matching a domain, downloads their LaTeX source,
and runs the perturbation pipeline until a target number of papers have been
successfully perturbed (i.e. n_injected >= n_total).

Usage:
    python perturb_automated.py --domain "mathematics" --arxiv-category "math.*" --category theoretical --error-type logic --target 10 --n-total 10 --min-year 2010
"""

import argparse
import json
import shutil
import subprocess
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ARXIV_API = "http://export.arxiv.org/api/query"
ARXIV_SRC = "https://arxiv.org/src/{}"

RESULTS_DIR = Path(__file__).parent / "results" / "perturbations"


# ---------------------------------------------------------------------------
# arXiv helpers
# ---------------------------------------------------------------------------

def search_arxiv(domain: str, arxiv_category: str | None, start: int, batch_size: int, min_year: int | None = None) -> list[dict]:
    """Return a list of {arxiv_id, title} dicts from the arXiv API."""
    query_parts = [f"all:{urllib.parse.quote(domain)}"]
    if arxiv_category:
        query_parts.append(f"cat:{arxiv_category}")
    if min_year:
        query_parts.append(f"submittedDate:[{min_year}0101+TO+*]")
    query = "+AND+".join(query_parts)

    url = (
        f"{ARXIV_API}?search_query={query}"
        f"&start={start}&max_results={batch_size}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )

    req = urllib.request.Request(url, headers={"User-Agent": "openaireview-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    papers = []
    for entry in root.findall("atom:entry", ns):
        id_text = entry.find("atom:id", ns).text or ""
        arxiv_id = id_text.split("/abs/")[-1].strip()
        title_el = entry.find("atom:title", ns)
        title = (title_el.text or "").strip().replace("\n", " ")
        if arxiv_id:
            papers.append({"arxiv_id": arxiv_id, "title": title})

    return papers


def download_latex_source(arxiv_id: str, dest_dir: Path) -> Path | None:
    """Download and extract the LaTeX source for an arXiv paper.

    Returns the path to the main .tex file, or None on failure.
    """
    src_url = ARXIV_SRC.format(arxiv_id)
    safe_id = arxiv_id.replace("/", "_")
    tarball = dest_dir / f"{safe_id}.tar.gz"

    try:
        req = urllib.request.Request(src_url, headers={"User-Agent": "openaireview-research/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            tarball.write_bytes(resp.read())
    except Exception as e:
        print(f"    Download failed: {e}")
        return None

    extract_dir = dest_dir / safe_id
    extract_dir.mkdir(exist_ok=True)

    try:
        with tarfile.open(tarball) as tf:
            tf.extractall(extract_dir)
    except Exception as e:
        print(f"    Extraction failed: {e}")
        return None

    return _find_main_tex(extract_dir)


def _find_main_tex(directory: Path) -> Path | None:
    """Find the main .tex file in an extracted arXiv source directory."""
    tex_files = list(directory.rglob("*.tex"))
    if not tex_files:
        return None

    # Keep only files that contain \documentclass (i.e. are root files)
    main_files = []
    for f in tex_files:
        try:
            content = f.read_text(errors="ignore")
            if r"\documentclass" in content:
                main_files.append(f)
        except Exception:
            continue

    candidates = main_files if main_files else tex_files

    # Prefer common names, then fall back to the largest file
    for preferred in ("main.tex", "paper.tex", "manuscript.tex", "article.tex"):
        for f in candidates:
            if f.name.lower() == preferred:
                return f

    return max(candidates, key=lambda f: f.stat().st_size)


# ---------------------------------------------------------------------------
# Perturbation runner
# ---------------------------------------------------------------------------

def run_perturb(
    tex_path: Path,
    category: str,
    error_type: str,
    n_total: int,
    model: str,
    output_dir: Path,
) -> int:
    """Run `openaireview perturb` and return n_injected (0 on any failure)."""
    cmd = [
        "openaireview", "perturb", str(tex_path),
        "--category", category,
        "--error-type", error_type,
        "--n-total", str(n_total),
        "--model", model,
        "--output-dir", str(output_dir),
    ]

    print(f"    $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    manifests = list(output_dir.glob("*_perturbations.json"))
    if not manifests:
        if result.returncode != 0:
            print(result.stdout + result.stderr)
        return 0

    manifest_path = max(manifests, key=lambda p: p.stat().st_mtime)
    try:
        manifest = json.loads(manifest_path.read_text())
        n_injected = manifest.get("n_injected", 0)
    except Exception:
        n_injected = 0

    if n_injected >= 0:  # always stash output for caller to decide
        result._n_injected = n_injected
    return n_injected


def _already_done(paper_output_dir: Path, n_total: int) -> bool:
    """Return True if this paper already has a successful perturbation run."""
    manifests = list(paper_output_dir.glob("*_perturbations.json"))
    for m in manifests:
        try:
            if json.loads(m.read_text()).get("n_injected", 0) >= n_total:
                return True
        except Exception:
            continue
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated arXiv perturbation pipeline",
    )
    parser.add_argument(
        "--domain", required=True,
        help="Search term for arXiv (e.g. 'combinatorics', 'stochastic processes')",
    )
    parser.add_argument(
        "--arxiv-category", default=None,
        help="arXiv category to restrict search (e.g. math.CO, cs.LG, stat.ML)",
    )
    parser.add_argument(
        "--category", choices=["theoretical", "experimental"], required=True,
        help="Paper category for the perturbation pipeline",
    )
    parser.add_argument(
        "--error-type",
        choices=["all", "surface", "claim_theoretical", "logic",
                 "statement_empirical", "experimental"],
        default="all",
        help="Error type to generate (default: all)",
    )
    parser.add_argument(
        "--target", type=int, required=True,
        help="Number of successfully perturbed papers to collect",
    )
    parser.add_argument(
        "--n-total", type=int, default=20,
        help="Minimum perturbations required for a paper to count (default: 20)",
    )
    parser.add_argument(
        "--model", default="anthropic/claude-opus-4-6",
        help="Model for perturbation generation (default: anthropic/claude-opus-4-6)",
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Root output directory (default: results/perturbations/<domain>)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=10,
        help="Papers to fetch per arXiv API call (default: 10)",
    )
    parser.add_argument(
        "--delay", type=float, default=3.0,
        help="Seconds to wait between papers (default: 3.0)",
    )
    parser.add_argument(
        "--min-year", type=int, default=None,
        help="Only include papers submitted on or after this year (e.g. 2010)",
    )
    args = parser.parse_args()

    output_root = (
        Path(args.output_dir)
        if args.output_dir
        else RESULTS_DIR / args.domain.replace(" ", "_")
    )
    output_root.mkdir(parents=True, exist_ok=True)

    print(f"Domain:         {args.domain}")
    print(f"arXiv category: {args.arxiv_category or 'any'}")
    print(f"Category:       {args.category}")
    print(f"Error type:     {args.error_type}")
    print(f"Target:         {args.target} papers")
    print(f"n_total:        {args.n_total} perturbations/paper")
    print(f"Model:          {args.model}")
    print(f"Min year:       {args.min_year or 'any'}")
    print(f"Output:         {output_root}")

    successful = 0
    attempted: set[str] = set()
    arxiv_start = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        while successful < args.target:
            print(f"\n--- arXiv results {arxiv_start}–{arxiv_start + args.batch_size - 1} ---")
            try:
                papers = search_arxiv(
                    args.domain, args.arxiv_category,
                    arxiv_start, args.batch_size,
                    min_year=args.min_year,
                )
            except Exception as e:
                print(f"arXiv API error: {e}")
                break

            if not papers:
                print("No more arXiv results.")
                break

            for paper in papers:
                if successful >= args.target:
                    break

                arxiv_id = paper["arxiv_id"]
                if arxiv_id in attempted:
                    continue
                attempted.add(arxiv_id)

                print(f"\n[{successful}/{args.target}] {arxiv_id}: {paper['title'][:70]}")

                paper_output_dir = output_root / arxiv_id.replace("/", "_")

                if _already_done(paper_output_dir, args.n_total):
                    print(f"  Already done, counting.")
                    successful += 1
                    continue

                print(f"  Downloading LaTeX source...")
                tex_path = download_latex_source(arxiv_id, tmp_path)
                if tex_path is None:
                    print(f"  Skipping: could not obtain LaTeX source.")
                    time.sleep(args.delay)
                    continue

                print(f"  Main file: {tex_path.name} ({tex_path.stat().st_size:,} bytes)")
                staging_dir = tmp_path / f"staging_{arxiv_id.replace('/', '_')}"
                staging_dir.mkdir(exist_ok=True)

                n_injected = run_perturb(
                    tex_path, args.category, args.error_type,
                    args.n_total, args.model, staging_dir,
                )

                if n_injected >= args.n_total:
                    paper_output_dir.mkdir(parents=True, exist_ok=True)
                    for f in staging_dir.iterdir():
                        shutil.move(str(f), str(paper_output_dir / f.name))
                    successful += 1
                    print(f"  SUCCESS: {n_injected} injected. [{successful}/{args.target}]")
                else:
                    print(f"  SKIP: only {n_injected}/{args.n_total} injected.")

                time.sleep(args.delay)

            arxiv_start += args.batch_size

    print(f"\n{'='*55}")
    print(f"Done. {successful}/{args.target} papers successfully perturbed.")
    print(f"Results: {output_root}")


if __name__ == "__main__":
    main()
