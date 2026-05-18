from .models import Perturbation, PerturbationResult
from reviewer.client import chat
from reviewer.utils import _normalize_for_match, _quote_coverage

from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

_FUZZY_QUOTE_THRESHOLD = 0.75
_LLM_GATE_THRESHOLD = 0.7


def score_review(perturbations: list[Perturbation],
                 review_comments: list[dict],
                 model: str,
                 method: str = "llm",
                 threshold: int = 3,
                 substring_gate: bool = False) -> PerturbationResult:
    n_injected = len(perturbations)
    n_total_comments = len(review_comments)

    n_detected = 0
    detected = []

    for p in perturbations:
        for comment in review_comments:
            if substring_gate and not _llm_substring_gate(
                    comment.get('quote', ''), p.perturbed
                ):
                    continue
            if method == "fuzzy":
                explanation_match = _explanation_match_fuzzy(comment.get('explanation', ''), p.why_wrong)
            elif method == "llm":
                explanation_match = _explanation_match_llm(
                    comment.get('explanation', ''), p.why_wrong, model,
                    threshold=threshold,
                )
            elif method == "semantic":
                explanation_match = _explanation_match_semantic(comment.get('explanation', ''), p.why_wrong)

            if explanation_match:
                n_detected += 1
                detected.append(p.perturbation_id)
                break

    missed = []
    for p in perturbations:
        if p.perturbation_id not in detected:
            missed.append(p.perturbation_id)

    recall = n_detected / n_injected if n_injected > 0 else 0.0

    return PerturbationResult(n_injected=n_injected, n_detected=n_detected, recall=recall, n_total_comments=n_total_comments, detected=detected, missed=missed)


def _llm_substring_gate(quote: str, perturbed: str,
                        threshold: float = _LLM_GATE_THRESHOLD) -> bool:
    """Cheap pre-filter for the `llm` method: True if a meaningful chunk of
    the reviewer's quote overlaps the perturbed text.
    """
    if not quote or not perturbed:
        return False
    q = _normalize_for_match(quote)
    p = _normalize_for_match(perturbed)
    if not q or not p:
        return False
    if q in p:
        return True
    return _quote_coverage(q, p) >= threshold


PROMPT = """
Given a reference description of an injected error and a reviewer's explanation, rate how well the reviewer identified the error.

Reply with only a single integer (1-5):
1 = reviewer does not mention the perturbed element at all
2 = reviewer mentions the region but identifies a completely different problem
3 = reviewer identifies the correct element (symbol/value/operator) as suspicious or wrong
4 = reviewer identifies the correct element and states what it should be
5 = reviewer fully explains the error and its impact on the paper

Reference description: {why_wrong}
Reviewer explanation: {explanation}
"""

def _explanation_match_llm(explanation, why_wrong, model, threshold: int = 3) -> bool:
    prompt = PROMPT.format(explanation=explanation, why_wrong=why_wrong)
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=16,
    )

    try:
        score = int(response)
    except ValueError:
        return False

    return score >= threshold

def _explanation_match_fuzzy(explanation, why_wrong) -> bool:
    return fuzz.token_set_ratio(explanation, why_wrong) >= 70

def _explanation_match_semantic(explanation, why_wrong) -> bool:
    model = SentenceTransformer('all-MiniLM-L6-v2')

    emb1 = model.encode(explanation, convert_to_tensor=True) 
    emb2 = model.encode(why_wrong, convert_to_tensor=True) 
    
    sim = util.cos_sim(emb1, emb2)

    return float(sim) >= 0.60