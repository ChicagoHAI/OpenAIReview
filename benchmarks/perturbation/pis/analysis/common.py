from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..gold_io import load_gold_set
from ..inputs import record_uid
from ..interval import PISInterval


def _reject_constant(x): raise ValueError(f"non-finite JSON constant: {x}")


def read_jsonl(path: str) -> List[dict]:
    out, seen = [], set()
    for ln, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line, parse_constant=_reject_constant)
        except Exception as e:
            raise ValueError(f"{path}:{ln}: invalid JSON: {e}")
        uid = obj.get("uid")
        if uid is None:
            raise ValueError(f"{path}:{ln}: missing 'uid'")
        if uid in seen:
            raise ValueError(f"{path}:{ln}: duplicate uid {uid}")
        seen.add(uid)
        out.append(obj)
    return out


def normalize_label(s: str) -> str:
    return s.strip().lower().replace("_", "-").replace(" ", "-")


def write_json(path, obj) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


@dataclass
class Row:
    uid: str; paper: str; perturbation_id: str
    pred_label: str; gold_label: str; correct: bool
    width: float; L: float; U: float; midpoint: float; ambiguity: float
    self_conf: Optional[float]
    error_type: Optional[str]; quote_source: Optional[str]; quote_available: bool
    n_items: int; n_support: int; n_against: int; n_unresolved: int
    status: str


def build_rows(pis_path: str, predictions_path: str, gold_set_path: str
               ) -> Tuple[List[Row], Dict[str, List[str]]]:
    """Evaluation-stage join. This is the ONLY place where gold labels meet
    verifier predictions; correct = (pred_label == gold_label) is computed
    here and nowhere else."""
    gold_records, _ = load_gold_set(gold_set_path)
    gold_by = {record_uid(r): r for r in gold_records}
    pis_by = {l["uid"]: l for l in read_jsonl(pis_path)}
    pred_by = {l["uid"]: l for l in read_jsonl(predictions_path)}
    exclusions: Dict[str, List[str]] = {"no_pis": [], "pis_failed_or_no_interval": [],
                                         "no_prediction": []}
    rows: List[Row] = []
    for uid, g in gold_by.items():
        pl = pis_by.get(uid)
        if pl is None:
            exclusions["no_pis"].append(uid); continue
        if pl.get("status") == "failed" or not pl.get("interval"):
            exclusions["pis_failed_or_no_interval"].append(uid); continue
        pr = pred_by.get(uid)
        if pr is None or not str(pr.get("pred_label", "")).strip():
            exclusions["no_prediction"].append(uid); continue
        iv = PISInterval.from_dict(pl["interval"])
        items = pl.get("evidence_items") or []
        conf = pl.get("self_reported_confidence_h")
        rows.append(Row(
            uid=uid, paper=str(g["paper"]), perturbation_id=str(g["perturbation_id"]),
            pred_label=normalize_label(str(pr["pred_label"])),
            gold_label=normalize_label(str(g["gold_label"])),
            correct=(normalize_label(str(pr["pred_label"])) == normalize_label(str(g["gold_label"]))),
            width=iv.width, L=iv.L, U=iv.U, midpoint=iv.midpoint, ambiguity=iv.ambiguity,
            self_conf=(float(conf) if isinstance(conf, (int, float)) else None),
            error_type=(g.get("error") or None),
            quote_source=(g.get("quote_source") or None),
            quote_available=bool((g.get("contradicts_quote") or "").strip()),
            n_items=len(items),
            n_support=sum(1 for it in items if it.get("polarity") == "supports_H"),
            n_against=sum(1 for it in items if it.get("polarity") == "against_H"),
            n_unresolved=sum(1 for it in items if it.get("polarity") == "unresolved"),
            status=str(pl.get("status", "unknown"))))
    return rows, exclusions


# ---------------- statistics ----------------

def average_ranks(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    order = np.argsort(x, kind="mergesort")
    ranks = np.empty(len(x), float)
    sx = x[order]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and sx[j + 1] == sx[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def auroc(scores, labels) -> Optional[float]:
    """AUC for higher score -> label 1 (Mann-Whitney form, tie-aware)."""
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return None
    r = average_ranks(s)
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0))


def bootstrap_auroc_ci(scores, labels, B: int = 2000, seed: int = 0, alpha: float = 0.05):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    rng = np.random.default_rng(seed)
    n = len(s)
    aucs, skipped = [], 0
    for _ in range(B):
        idx = rng.integers(0, n, size=n)
        a = auroc(s[idx], y[idx])
        if a is None:
            skipped += 1
        else:
            aucs.append(a)
    if not aucs:
        return None, None, skipped
    lo, hi = np.percentile(aucs, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(lo), float(hi), skipped


def _phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def mann_whitney_u(x, y):
    """Two-sided Mann-Whitney U (normal approximation, tie-corrected, with
    continuity correction)."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    n1, n2 = len(x), len(y)
    if n1 == 0 or n2 == 0:
        return None, None, None
    allv = np.concatenate([x, y])
    r = average_ranks(allv)
    R1 = r[:n1].sum()
    U1 = R1 - n1 * (n1 + 1) / 2.0
    U = max(U1, n1 * n2 - U1)
    mu = n1 * n2 / 2.0
    _, counts = np.unique(allv, return_counts=True)
    tie = float((counts ** 3 - counts).sum())
    N = n1 + n2
    sigma_sq = (n1 * n2 / 12.0) * ((N + 1) - tie / (N * (N - 1))) if N > 1 else 0.0
    if sigma_sq <= 0:
        return float(U), None, None
    z = (U - 0.5 - mu) / math.sqrt(sigma_sq)
    return float(U), float(z), float(2 * (1 - _phi(abs(z))))


def wilson_ci(k: int, n: int, z: float = 1.959963984540054):
    if n == 0:
        return (None, None)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def spearman(x, y) -> Optional[float]:
    x = np.asarray(x, float); y = np.asarray(y, float)
    if len(x) < 2 or np.all(x == x[0]) or np.all(y == y[0]):
        return None
    return float(np.corrcoef(average_ranks(x), average_ranks(y))[0, 1])


def roc_curve(scores, labels):
    s = np.asarray(scores, float); y = np.asarray(labels, int)
    order = np.argsort(-s, kind="mergesort")
    labs = y[order]
    n1, n0 = int(y.sum()), int((1 - y).sum())
    if n1 == 0 or n0 == 0:
        return None, None
    tpr = np.concatenate([[0], np.cumsum(labs)]) / n1
    fpr = np.concatenate([[0], np.cumsum(1 - labs)]) / n0
    return fpr, tpr


def quantile_bins(values, n_bins: int = 4, min_size: int = 5):
    """Deterministic quantile binning with a minimum bin size; falls back to
    fewer bins, then unique-value bins, then a single bin."""
    v = np.asarray(values, float)
    if len(v) < 2 * min_size or len(np.unique(v)) <= 1:
        return [-math.inf, math.inf], 1
    while n_bins >= 2:
        qs = np.quantile(v, np.linspace(0, 1, n_bins + 1))
        inner = sorted(set(float(round(q, 12)) for q in qs[1:-1]))
        counts = np.digitize(v, np.array(inner, float))
        if min(np.bincount(counts, minlength=len(inner) + 1)) >= min_size:
            return [-math.inf] + inner + [math.inf], len(inner) + 1
        n_bins -= 1
    uniq = np.unique(v)
    if len(uniq) <= 6:
        inner = [float(u) for u in uniq[:-1]]
        counts = np.digitize(v, np.array(inner, float))
        if min(np.bincount(counts, minlength=len(inner) + 1)) >= min_size:
            return [-math.inf] + inner + [math.inf], len(inner) + 1
    return [-math.inf, math.inf], 1


def binned_stats(values, flags, edges):
    v = np.asarray(values, float); f = np.asarray(flags, int)
    inner = np.array([e for e in edges[1:-1]], float)
    idx = np.digitize(v, inner) if len(inner) else np.zeros(len(v), int)
    out = []
    for b in range(len(inner) + 1):
        m = idx == b
        n, k = int(m.sum()), int(f[m].sum())
        lo, hi = wilson_ci(k, n)
        out.append({"bin": b,
                    "lo": (None if edges[b] == -math.inf else edges[b]),
                    "hi": (None if edges[b + 1] == math.inf else edges[b + 1]),
                    "n": n, "n_error": k,
                    "error_rate": (k / n if n else None),
                    "error_rate_ci95_wilson": [lo, hi] if n else None})
    return out


def stats_of(v) -> dict:
    v = np.asarray(v, float)
    if v.size == 0:
        return {"n": 0}
    q25, q75 = np.percentile(v, [25, 75])
    return {"n": int(v.size), "mean": float(v.mean()), "median": float(np.median(v)),
            "std": (float(v.std(ddof=1)) if v.size > 1 else 0.0),
            "iqr": [float(q25), float(q75)],
            "min": float(v.min()), "max": float(v.max())}


def save_fig(fig, path) -> None:
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=150, bbox_inches="tight")
    finally:
        import matplotlib.pyplot as plt
        plt.close(fig)