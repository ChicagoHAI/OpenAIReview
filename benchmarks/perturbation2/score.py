from .models import Perturbation, PerturbationResult
from reviewer.client import chat

from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer, util

def score_review(perturbations: list[Perturbation], 
                 review_comments: list[dict], 
                 model: str, method: str = "llm") -> PerturbationResult:
    n_injected = len(perturbations)
    n_total_comments = len(review_comments)

    n_detected = 0
    detected = []

    for p in perturbations:
        for comment in review_comments:
            if not _substring_match(comment.get('quote', ''), p.perturbed):
                continue 

            if method == "llm":
                explanation_match = _explanation_match_llm(comment.get('explanation', ''), p.why_wrong, model)
            elif method == "fuzzy":
                explanation_match = _explanation_match_fuzzy(comment.get('explanation', ''), p.why_wrong)
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


def _substring_match(quote, perturbed) -> bool:
    return perturbed.lower() in quote.lower()


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

def _explanation_match_llm(explanation, why_wrong, model) -> bool:
    prompt = PROMPT.format(explanation=explanation, why_wrong=why_wrong)
    response, usage = chat(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=8192,
    )

    try:
        score = int(response)
    except ValueError:
        return False

    return score >= 3

def _explanation_match_fuzzy(explanation, why_wrong) -> bool:
    return fuzz.token_set_ratio(explanation, why_wrong) >= 70

def _explanation_match_semantic(explanation, why_wrong) -> bool:
    model = SentenceTransformer('all-MiniLM-L6-v2')

    emb1 = model.encode(explanation, convert_to_tensor=True) 
    emb2 = model.encode(why_wrong, convert_to_tensor=True) 
    
    sim = util.cos_sim(emb1, emb2)

    return float(sim) >= 0.80 