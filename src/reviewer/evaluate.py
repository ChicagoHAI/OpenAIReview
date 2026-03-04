"""Evaluation metrics for paper review methods."""

import json
from difflib import SequenceMatcher
from pathlib import Path

from .client import chat
from .models import Comment, ReviewResult

# Cost per 1M tokens (USD) - OpenRouter pricing as of early 2026
COST_PER_1M = {
    "anthropic/claude-opus-4-6": {"prompt": 5.0, "completion": 25.0},
    "anthropic/claude-opus-4-5": {"prompt": 5.0, "completion": 25.0},
    "google/gemini-3.1-pro-preview": {"prompt": 2.0, "completion": 12.0},
    "z-ai/glm-5": {"prompt": 0.80, "completion": 2.56},
    "moonshotai/kimi-k2.5": {"prompt": 0.45, "completion": 2.20},
    "openai/gpt-5.2-pro": {"prompt": 21.0, "completion": 168.0},
}
DEFAULT_COST = {"prompt": 5.0, "completion": 25.0}

SIMILARITY_THRESHOLD = 0.35
LOCATION_WINDOW = 3  # ±3 paragraphs counts as same location

JUDGE_MODEL = "anthropic/claude-haiku-4-5"

JUDGE_PROMPT = """\
You are evaluating whether a predicted reviewer comment identifies the same issue as a \
ground-truth comment from an expert reviewer.

They do NOT need to use the same wording. They match if they point to the same underlying \
error or problem in the paper, even if described differently or quoting a nearby passage.

Ground-truth comment:
  Title: {gt_title}
  Quote: {gt_quote}
  Explanation: {gt_explanation}

Predicted comment:
  Title: {pred_title}
  Quote: {pred_quote}
  Explanation: {pred_explanation}

Do these refer to the same issue? Reply with exactly one word: YES or NO."""


def compute_cost(result: ReviewResult) -> float:
    """Estimate USD cost of a review."""
    pricing = None
    for key in COST_PER_1M:
        if key in result.model:
            pricing = COST_PER_1M[key]
            break
    if pricing is None:
        pricing = DEFAULT_COST

    if "+" in result.model:
        parts = result.model.split("+")
        costs = []
        for part in parts:
            p = next((v for k, v in COST_PER_1M.items() if k in part), DEFAULT_COST)
            costs.append(p)
        pricing = {
            "prompt": 0.3 * costs[0]["prompt"] + 0.7 * costs[1]["prompt"],
            "completion": 0.3 * costs[0]["completion"] + 0.7 * costs[1]["completion"],
        }

    return (
        result.total_prompt_tokens / 1_000_000 * pricing["prompt"]
        + result.total_completion_tokens / 1_000_000 * pricing["completion"]
    )


# ---------------------------------------------------------------------------
# Similarity-based matching
# ---------------------------------------------------------------------------

def quote_similarity(a: str, b: str) -> float:
    a, b = a.lower().strip(), b.lower().strip()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a[:500], b[:500]).ratio()


def _sim_match(pred: Comment, gt: dict) -> bool:
    sim = max(
        quote_similarity(pred.quote, gt.get("quote", "")),
        quote_similarity(pred.quote, gt.get("paragraph", "")),
        quote_similarity(pred.explanation, gt.get("message", "")),
    )
    return sim >= SIMILARITY_THRESHOLD


# ---------------------------------------------------------------------------
# LLM-as-a-judge matching
# ---------------------------------------------------------------------------

def llm_judge_is_match(pred: Comment, gt: dict, model: str = JUDGE_MODEL) -> bool:
    """Ask an LLM whether pred and gt refer to the same issue."""
    prompt = JUDGE_PROMPT.format(
        gt_title=gt.get("title", ""),
        gt_quote=gt.get("quote", gt.get("paragraph", ""))[:400],
        gt_explanation=gt.get("message", "")[:400],
        pred_title=pred.title,
        pred_quote=pred.quote[:400],
        pred_explanation=pred.explanation[:400],
    )
    response, _ = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.0,
        max_tokens=4,
    )
    return response.strip().upper().startswith("YES")


def _recall_for_subset(
    gt_subset: list[dict],
    predicted: list[Comment],
    use_llm_judge: bool,
    judge_model: str,
) -> float:
    if not gt_subset:
        return 0.0
    recalled = 0
    for gt in gt_subset:
        for pred in predicted:
            if use_llm_judge:
                matched = _location_match(pred, gt) and llm_judge_is_match(pred, gt, model=judge_model)
            else:
                matched = _sim_match(pred, gt)
            if matched:
                recalled += 1
                break
    return recalled / len(gt_subset)


# ---------------------------------------------------------------------------
# Location-based matching
# ---------------------------------------------------------------------------

def _location_match(pred: Comment, gt: dict, window: int = LOCATION_WINDOW) -> bool:
    """Check if pred and gt are within ±window paragraphs of each other."""
    pred_idx = pred.paragraph_index
    gt_idx = gt.get("paragraph_index")
    if pred_idx is None or gt_idx is None:
        return False
    return abs(pred_idx - gt_idx) <= window


def _location_recall(
    gt_list: list[dict],
    predicted: list[Comment],
    window: int = LOCATION_WINDOW,
) -> float:
    """Recall based purely on paragraph location proximity."""
    if not gt_list:
        return 0.0
    recalled = 0
    for gt in gt_list:
        for pred in predicted:
            if _location_match(pred, gt, window):
                recalled += 1
                break
    return recalled / len(gt_list)


# ---------------------------------------------------------------------------
# Main evaluate function
# ---------------------------------------------------------------------------

def evaluate(
    result: ReviewResult,
    ground_truth: list[dict],
    use_llm_judge: bool = False,
    judge_model: str = JUDGE_MODEL,
    location_window: int = LOCATION_WINDOW,
) -> dict:
    """Evaluate a review result against ground truth.

    Returns a metrics dict. If use_llm_judge=True, recall/precision are computed
    using an LLM judge instead of string similarity; both sets of metrics are
    returned with a 'llm_judge' suffix alongside the similarity-based ones.

    Also computes multi-window location recall (±3, ±5, ±10) and optionally
    an ungated LLM judge recall (no location pre-filter).
    """
    predicted = result.comments
    n_gt = len(ground_truth)
    n_pred = len(predicted)

    # --- similarity-based ---
    sim_pred_matched = sum(
        1 for pred in predicted if any(_sim_match(pred, gt) for gt in ground_truth)
    )
    sim_recalled = sum(
        1 for gt in ground_truth if any(_sim_match(pred, gt) for pred in predicted)
    )
    sim_recall = sim_recalled / n_gt if n_gt > 0 else 0.0
    sim_precision = sim_pred_matched / n_pred if n_pred > 0 else 0.0
    sim_f1 = _f1(sim_recall, sim_precision)

    technical_gt = [g for g in ground_truth if g.get("comment_type") == "technical"]
    logical_gt = [g for g in ground_truth if g.get("comment_type") == "logical"]

    metrics = {
        "num_predicted": n_pred,
        "num_ground_truth": n_gt,
        "num_recalled": sim_recalled,
        "recall": round(sim_recall, 3),
        "precision": round(sim_precision, 3),
        "f1": round(sim_f1, 3),
        "technical_recall": round(
            _recall_for_subset(technical_gt, predicted, False, judge_model), 3
        ),
        "logical_recall": round(
            _recall_for_subset(logical_gt, predicted, False, judge_model), 3
        ),
        "cost_usd": round(compute_cost(result), 4),
        "prompt_tokens": result.total_prompt_tokens,
        "completion_tokens": result.total_completion_tokens,
        "location_recall": round(_location_recall(ground_truth, predicted, window=location_window), 3),
        "location_recall_5": round(_location_recall(ground_truth, predicted, window=5), 3),
        "location_recall_10": round(_location_recall(ground_truth, predicted, window=10), 3),
        "technical_location_recall": round(
            _location_recall(technical_gt, predicted, window=location_window), 3
        ),
        "logical_location_recall": round(
            _location_recall(logical_gt, predicted, window=location_window), 3
        ),
    }

    # --- LLM-judge-based (pre-filtered by paragraph proximity) ---
    if use_llm_judge:
        llm_pred_matched = sum(
            1 for pred in predicted
            if any(
                _location_match(pred, gt, window=location_window) and llm_judge_is_match(pred, gt, model=judge_model)
                for gt in ground_truth
            )
        )
        llm_recalled = sum(
            1 for gt in ground_truth
            if any(
                _location_match(pred, gt, window=location_window) and llm_judge_is_match(pred, gt, model=judge_model)
                for pred in predicted
            )
        )
        llm_recall = llm_recalled / n_gt if n_gt > 0 else 0.0
        llm_precision = llm_pred_matched / n_pred if n_pred > 0 else 0.0
        llm_f1 = _f1(llm_recall, llm_precision)

        # Wide-gate LLM judge (±10 paragraphs) — much faster than ungated
        wide_window = 10
        wide_recalled = sum(
            1 for gt in ground_truth
            if any(
                _location_match(pred, gt, window=wide_window) and llm_judge_is_match(pred, gt, model=judge_model)
                for pred in predicted
            )
        )
        wide_pred_matched = sum(
            1 for pred in predicted
            if any(
                _location_match(pred, gt, window=wide_window) and llm_judge_is_match(pred, gt, model=judge_model)
                for gt in ground_truth
            )
        )
        wide_recall = wide_recalled / n_gt if n_gt > 0 else 0.0
        wide_precision = wide_pred_matched / n_pred if n_pred > 0 else 0.0

        metrics.update({
            "num_recalled_llm": llm_recalled,
            "recall_llm": round(llm_recall, 3),
            "precision_llm": round(llm_precision, 3),
            "f1_llm": round(llm_f1, 3),
            "technical_recall_llm": round(
                _recall_for_subset(technical_gt, predicted, True, judge_model), 3
            ),
            "logical_recall_llm": round(
                _recall_for_subset(logical_gt, predicted, True, judge_model), 3
            ),
            "num_recalled_llm_wide": wide_recalled,
            "recall_llm_wide": round(wide_recall, 3),
            "precision_llm_wide": round(wide_precision, 3),
            "f1_llm_wide": round(_f1(wide_recall, wide_precision), 3),
        })

    return metrics


def _f1(recall: float, precision: float) -> float:
    return (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0 else 0.0
    )


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_benchmark(benchmark_file: Path) -> list[dict]:
    papers = []
    with open(benchmark_file) as f:
        for line in f:
            papers.append(json.loads(line))
    return papers


def print_report(results: list[tuple[str, str, dict]]) -> None:
    """Print a formatted evaluation report.

    results: list of (method, paper_slug, metrics_dict)
    """
    has_llm = any("recall_llm" in m for _, _, m in results)

    print("\n" + "=" * 80)
    print("EVALUATION REPORT")
    if has_llm:
        print("(showing similarity-based and LLM-judge recall)")
    print("=" * 80)

    methods: dict[str, list[dict]] = {}
    for method, slug, metrics in results:
        methods.setdefault(method, []).append(metrics)

    for method, all_metrics in methods.items():
        print(f"\nMethod: {method.upper()}")
        print("-" * 60)
        total_pred = sum(m["num_predicted"] for m in all_metrics)
        total_gt = sum(m["num_ground_truth"] for m in all_metrics)
        total_recalled = sum(m["num_recalled"] for m in all_metrics)
        avg_recall = total_recalled / total_gt if total_gt > 0 else 0
        avg_prec = (
            sum(m["precision"] * m["num_predicted"] for m in all_metrics) / total_pred
            if total_pred > 0 else 0
        )
        total_cost = sum(m["cost_usd"] for m in all_metrics)

        avg_loc_recall = (
            sum(m.get("location_recall", 0) * m["num_ground_truth"] for m in all_metrics)
            / total_gt if total_gt > 0 else 0
        )

        print(f"  Comments found:        {total_pred}")
        print(f"  Ground truth:          {total_gt}")
        print(f"  Recall  (similarity):  {total_recalled}/{total_gt} ({avg_recall:.1%})")
        print(f"  Recall  (location):    {avg_loc_recall:.1%}")

        if has_llm and "recall_llm" in all_metrics[0]:
            total_recalled_llm = sum(m.get("num_recalled_llm", 0) for m in all_metrics)
            avg_recall_llm = total_recalled_llm / total_gt if total_gt > 0 else 0
            print(f"  Recall  (LLM judge):  {total_recalled_llm}/{total_gt} ({avg_recall_llm:.1%})")

        print(f"  Total cost:            ${total_cost:.4f}")

        print("\n  Per-paper breakdown:")
        for (m, slug, _), md in zip(
            [(m, s, x) for m, s, x in results if m == method], all_metrics
        ):
            llm_str = (
                f" | llm_recall={md['recall_llm']:.2f}"
                if "recall_llm" in md else ""
            )
            loc_str = f" | loc_recall={md.get('location_recall', 0):.2f}"
            print(
                f"    {slug[:42]:<42} "
                f"sim_recall={md['recall']:.2f}{loc_str}{llm_str} "
                f"pred={md['num_predicted']:3d} gt={md['num_ground_truth']:3d} "
                f"cost=${md['cost_usd']:.4f}"
            )

    print("\n" + "=" * 80)
