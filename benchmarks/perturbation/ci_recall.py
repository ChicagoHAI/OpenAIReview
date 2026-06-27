"""95% confidence intervals for the recall tables in the paper.

Recall here is the fraction of injected errors that a review system detects. The
intervals come from a cluster bootstrap, where the cluster is a paper: collect every
paper's (detected, injected) error counts for a given method and model, resample those
papers with replacement many times, recompute the pooled recall (total detected divided
by total injected) on each resample, and take the 2.5th and 97.5th percentiles.
Resampling whole papers makes the interval reflect how much the estimate would move if
the paper sample changed. Pass an error category to restrict a cell to one error type.

The paper sets, result directories, and tables to print live in a JSON config (--config,
defaults to ci_recall_tables.json), kept local because it names internal result
directories and model ids. The bootstrap math is covered by tests/test_ci_recall.py on
in-memory counts. Two table kinds: by_model (recall per model and method) and by_category
(recall split by error category for selected systems).

Every cell draws from one seeded random generator, consumed in config order. A table's
CIs reproduce exactly only when the whole config runs unchanged, so adding or reordering
cells shifts the intervals of later ones.
"""
import json
from pathlib import Path

import numpy as np

B = 5000
RNG = np.random.default_rng(42)


# ---- pure aggregation + bootstrap (unit-tested in tests/test_ci_recall.py) ----

def paper_rows(per_paper, category_of=None, category=None):
    """Per-paper (detected, injected) counts for one table cell.

    `per_paper` maps a paper id to its per-error-type counts, each a
    (detected, injected) pair. With `category` set, only error types whose
    `category_of[error_type]` equals it are summed, restricting the cell to one
    category (e.g. Surface). A paper is dropped when it contributes no matching
    error type or zero injected errors.
    """
    category_of = category_of or {}
    rows = []
    for counts_by_type in per_paper.values():
        detected = injected = 0
        matched = False
        for error_type, (n_detected, n_injected) in counts_by_type.items():
            if category and category_of.get(error_type) != category:
                continue
            detected += n_detected
            injected += n_injected
            matched = True
        if matched and injected > 0:
            rows.append((detected, injected))
    return rows


def boot_ci(rows):
    """Pooled recall and its 95% cluster-bootstrap CI for one cell.

    `rows` is the per-paper (detected, injected) list from paper_rows. Returns
    (point, lo, hi, detected, injected): the pooled recall
    sum(detected) / sum(injected), the 2.5/97.5 bootstrap percentiles over
    paper resamples, and the summed counts. All-nan with zeroed counts when
    `rows` is empty.
    """
    if not rows:
        return (float("nan"), float("nan"), float("nan"), 0, 0)
    det = np.array([r[0] for r in rows], float)
    inj = np.array([r[1] for r in rows], float)
    point = det.sum() / inj.sum()
    n = len(rows)
    idx = RNG.integers(0, n, size=(B, n))
    rec = det[idx].sum(axis=1) / inj[idx].sum(axis=1)
    lo, hi = np.percentile(rec, [2.5, 97.5])
    return (point, lo, hi, int(det.sum()), int(inj.sum()))


# ---- reading score files off disk ----

def base_of(domain):
    return domain.replace("full_", "").replace("_scaleup_v2", "")


def load_score(root, score, domain, model, etype, method, paper):
    if method == "reviewer3":
        p = root / f"full_{base_of(domain)}_reviewer3" / "reviewer3" / etype / "reviewer3" / paper / "score" / score / f"{paper}_score.json"
    else:
        p = root / domain / model / etype / method / paper / "score" / score / f"{paper}_score.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def load_cell(config, root, model_slug, method):
    """Read each paper's per-error-type (detected, injected) counts for a cell.

    Returns {paper_id: {error_type: (detected, injected)}} over the domains in
    the config, ready for paper_rows. Each (domain, paper) is its own cluster,
    so the same paper id under different domains stays separate.
    """
    per_paper = {}
    for dom in config["domains"]:
        domain = dom["dir"]
        for paper in dom["papers"]:
            counts = {}
            for etype in dom["error_types"]:
                s = load_score(root, config["score"], domain, model_slug, etype, method, paper)
                if s is None:
                    continue
                counts[etype] = (s["n_detected"], s["n_injected"])
            if counts:
                per_paper[f"{domain}/{paper}"] = counts
    return per_paper


def cell_ci(config, root, slug, method, category=None):
    """(boot_ci tuple, n_papers) for one (model, method[, category]) cell."""
    rows = paper_rows(load_cell(config, root, slug, method), config.get("categories"), category)
    return boot_ci(rows), len(rows)


# ---- table renderers ----

def fmt(point, lo, hi, d, i):
    if i == 0:  # no injected errors loaded: empty category or a misconfigured cell
        return f"{'NO DATA':^30}"
    return f"{point*100:5.1f}% [{lo*100:4.1f}, {hi*100:4.1f}]  ({d}/{i})"


def run_by_model(config, root, table):
    """Recall per model x method, plus any single-cell extra rows (e.g. Reviewer3)."""
    methods = table["methods"]
    for label, slug in table["models"].items():
        line = f"{label:22s}"
        for method in methods:
            ci, _ = cell_ci(config, root, slug, method)
            line += " | " + fmt(*ci)
        print(line)
    for extra in table.get("extra_rows", []):
        ci, _ = cell_ci(config, root, extra["slug"], extra["method"])
        print(f"{extra['label']:22s}| " + fmt(*ci))


def run_by_category(config, root, table):
    """Recall split by error category for selected (system) cells."""
    cats = table["categories"]
    print(f"{'cell':24s} | " + " | ".join((c or "Overall") for c in cats))
    for cell in table["cells"]:
        line = f"{cell['label']:24s}"
        for c in cats:
            (p, lo, hi, d, i), n = cell_ci(config, root, cell["slug"], cell["method"], c)
            line += " | " + ("NO DATA" if n == 0 else f"{p*100:4.1f}[{lo*100:.1f},{hi*100:.1f}]n{n}")
        print(line)


DISPATCH = {"by_model": run_by_model, "by_category": run_by_category}


if __name__ == "__main__":
    import argparse

    HERE = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", type=Path, default=HERE / "ci_recall_tables.json",
                    help="JSON defining domains, error-type categories, and tables. "
                         "Paths inside it are relative to the config's directory. "
                         "Defaults to ci_recall_tables.json.")
    args = ap.parse_args()
    config = json.loads(args.config.read_text())
    root = args.config.resolve().parent / config.get("results_dir", "results")
    for table in config["tables"]:
        kind = table["kind"]
        if kind not in DISPATCH:
            ap.error(f"unknown table kind {kind!r}; choices: {list(DISPATCH)}")
        print(f"\n=== {table['title']} ===")
        DISPATCH[kind](config, root, table)
