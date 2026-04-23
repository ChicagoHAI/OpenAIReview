"""Download OpenReview PDFs for benchmark papers (local files for openaireview review).

OpenReview PDF URLs are not handled by ``parse_document`` like arXiv; this script
fetches PDFs using the shared session helper in ``openreview_http``.

PDFs are written to ``benchmarks/openreview_benchmark/data/openreview_pdfs/`` by default (gitignored).
If OpenReview returns HTTP 429, rerun for the missing ``--forum-ids`` with a larger ``--delay``.

Usage:
    python benchmarks/openreview_benchmark/scripts/download_openreview_pdfs.py
    python benchmarks/openreview_benchmark/scripts/download_openreview_pdfs.py --forum-ids jj7b3p5kLY,kOJf7Dklyv
"""

import argparse
import json
import sys
import time
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_TRACK_ROOT = _SCRIPT_DIR.parent
_DATA_DIR = _TRACK_ROOT / "data"
DEFAULT_BENCHMARK = _DATA_DIR / "openreview_benchmark.jsonl"
DEFAULT_OUT = _DATA_DIR / "openreview_pdfs"

if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from openreview_http import create_openreview_session, pdf_download_url


def download_pdf(session, forum_id: str, out_path: Path) -> bool:
    url = pdf_download_url(forum_id)
    resp = session.get(url, timeout=120)
    if resp.status_code != 200:
        print(f"  ERROR {resp.status_code} for {forum_id}")
        return False
    ct = resp.headers.get("Content-Type", "")
    if "pdf" not in ct.lower() and resp.content[:4] != b"%PDF":
        print(f"  WARN {forum_id}: response may not be PDF (Content-Type: {ct})")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    print(f"  Saved {out_path} ({len(resp.content)} bytes)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Download OpenReview PDFs for benchmark papers")
    parser.add_argument(
        "--benchmark",
        type=Path,
        default=DEFAULT_BENCHMARK,
        help=f"JSONL with paper_id field (default: {DEFAULT_BENCHMARK})",
    )
    parser.add_argument(
        "--forum-ids",
        type=str,
        default=None,
        help="Comma-separated forum ids (overrides --benchmark)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUT,
        help=f"Directory for PDF files (default: {DEFAULT_OUT})",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=3.0,
        help="Seconds between downloads (default: 3; increase if you see HTTP 429)",
    )
    args = parser.parse_args()

    if args.forum_ids:
        ids = [x.strip() for x in args.forum_ids.split(",") if x.strip()]
    else:
        if not args.benchmark.exists():
            print(f"Missing {args.benchmark}", file=sys.stderr)
            sys.exit(1)
        ids = []
        with open(args.benchmark, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                ids.append(json.loads(line)["paper_id"])

    print(f"Downloading {len(ids)} PDFs to {args.output_dir}\n")
    session = create_openreview_session(mode="pdf", warmup_timeout=60.0)
    ok = 0
    for i, fid in enumerate(ids):
        out = args.output_dir / f"{fid}.pdf"
        if download_pdf(session, fid, out):
            ok += 1
        if i < len(ids) - 1:
            time.sleep(args.delay)
    print(f"\nDone: {ok}/{len(ids)} OK")


if __name__ == "__main__":
    main()
