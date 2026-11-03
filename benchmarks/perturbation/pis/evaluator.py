from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .backends import LLMBackend
from .evidence import EvidenceItem, aggregate_evidence
from .inputs import VerifierInput
from .parsing import parse_pis_output, parse_scalar_output
from .prompts import (PROMPT_VERSION, SCALAR_PROMPT_VERSION, build_pis_prompt,
                      build_scalar_confidence_prompt)

RETRY_SUFFIX = (
    "\n\nYour previous response could not be parsed (error: {err}). "
    "Respond again with ONLY the JSON object matching the schema exactly. "
    "All numbers must be finite decimals in [0,1]. No markdown fences, no extra text.")


@dataclass
class PISResult:
    uid: str
    status: str  # ok | repaired | failed
    attempts: int
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    interval: Optional[Any] = None
    self_reported_confidence: Optional[float] = None
    repairs: List[str] = field(default_factory=list)
    raw_outputs: List[str] = field(default_factory=list)
    model_id: str = ""
    prompt_version: str = PROMPT_VERSION
    feature_set: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status, "attempts": self.attempts,
            "evidence_items": [dataclasses.asdict(it) for it in self.evidence_items],
            "interval": self.interval.to_dict() if self.interval is not None else None,
            "self_reported_confidence_h": self.self_reported_confidence,
            "repairs": list(self.repairs), "raw_outputs": list(self.raw_outputs),
            "model_id": self.model_id, "prompt_version": self.prompt_version,
            "feature_set": self.feature_set,
        }


@dataclass
class ScalarResult:
    uid: str
    status: str
    attempts: int
    value: Optional[float] = None
    repairs: List[str] = field(default_factory=list)
    raw_outputs: List[str] = field(default_factory=list)
    model_id: str = ""
    prompt_version: str = SCALAR_PROMPT_VERSION
    feature_set: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status, "attempts": self.attempts, "value": self.value,
                "repairs": list(self.repairs), "raw_outputs": list(self.raw_outputs),
                "model_id": self.model_id, "prompt_version": self.prompt_version,
                "feature_set": self.feature_set}


class PISEvaluator:
    """Computes a PIS interval per VerifierInput.

    The interval is DERIVED from the itemized evidence (positive / negative /
    unresolved) via `aggregate_evidence`; it is never a self-reported scalar.
    The model's self-reported confidence is recorded only as an auxiliary
    baseline signal and does not enter the interval.
    """

    def __init__(self, backend: LLMBackend, max_retries: int = 2):
        self.backend = backend
        self.max_retries = max_retries

    def evaluate_batch(self, inputs: Sequence[VerifierInput],
                       max_new_tokens: int = 768) -> List[PISResult]:
        prompts = [build_pis_prompt(v) for v in inputs]
        outputs = self.backend.generate(prompts, max_new_tokens)
        state: List[Dict[str, Any]] = []
        for vin, out in zip(inputs, outputs):
            pr = parse_pis_output(out)
            state.append({"vin": vin, "raws": [out], "payload": pr.payload,
                          "status": pr.status, "repairs": list(pr.repairs),
                          "error": pr.error, "attempts": 1})
        for _ in range(self.max_retries):
            idx = [i for i, s in enumerate(state) if s["payload"] is None]
            if not idx:
                break
            retry_prompts = [build_pis_prompt(inputs[i])
                             + RETRY_SUFFIX.format(err=state[i]["error"]) for i in idx]
            outs = self.backend.generate(retry_prompts, max_new_tokens)
            for i, out in zip(idx, outs):
                s = state[i]
                s["raws"].append(out)
                s["attempts"] += 1
                pr = parse_pis_output(out)
                s["repairs"] = s["repairs"] + list(pr.repairs)
                if pr.payload is not None:
                    s.update(payload=pr.payload, status=pr.status, error=None)
                else:
                    s["error"] = pr.error

        results: List[PISResult] = []
        for s in state:
            vin: VerifierInput = s["vin"]
            base = dict(model_id=self.backend.model_id, prompt_version=PROMPT_VERSION,
                        feature_set=vin.feature_set, raw_outputs=s["raws"],
                        attempts=s["attempts"], repairs=s["repairs"])
            if s["payload"] is None:
                results.append(PISResult(uid=vin.uid, status="failed",
                                          evidence_items=[], interval=None,
                                          self_reported_confidence=None, **base))
                continue
            items: List[EvidenceItem] = s["payload"]["evidence_items"]
            conf = s["payload"].get("self_reported_confidence_h")
            results.append(PISResult(
                uid=vin.uid, status=s["status"], evidence_items=items,
                interval=aggregate_evidence(items),
                self_reported_confidence=(float(conf)
                                          if isinstance(conf, (int, float)) else None),
                **base))
        return results


class ScalarConfidenceEvaluator:
    """Deliberately minimal scalar-confidence baseline (the 'strawman' PIS is
    compared against). Same inputs, no evidence decomposition."""

    def __init__(self, backend: LLMBackend, max_retries: int = 2):
        self.backend = backend
        self.max_retries = max_retries

    def evaluate_batch(self, inputs: Sequence[VerifierInput],
                       max_new_tokens: int = 128) -> List[ScalarResult]:
        prompts = [build_scalar_confidence_prompt(v) for v in inputs]
        outputs = self.backend.generate(prompts, max_new_tokens)
        state = []
        for vin, out in zip(inputs, outputs):
            pr = parse_scalar_output(out)
            state.append({"vin": vin, "raws": [out], "payload": pr.payload,
                          "status": pr.status, "repairs": list(pr.repairs),
                          "error": pr.error, "attempts": 1})
        for _ in range(self.max_retries):
            idx = [i for i, s in enumerate(state) if s["payload"] is None]
            if not idx:
                break
            outs = self.backend.generate(
                [build_scalar_confidence_prompt(inputs[i])
                 + RETRY_SUFFIX.format(err=state[i]["error"]) for i in idx], max_new_tokens)
            for i, out in zip(idx, outs):
                s = state[i]
                s["raws"].append(out); s["attempts"] += 1
                pr = parse_scalar_output(out)
                s["repairs"] = s["repairs"] + list(pr.repairs)
                if pr.payload is not None:
                    s.update(payload=pr.payload, status=pr.status, error=None)
                else:
                    s["error"] = pr.error
        results = []
        for s in state:
            vin = s["vin"]
            val = s["payload"]["p_substantive"] if s["payload"] else None
            results.append(ScalarResult(
                uid=vin.uid, status=s["status"], value=val,
                model_id=self.backend.model_id, feature_set=vin.feature_set,
                raw_outputs=s["raws"], attempts=s["attempts"], repairs=s["repairs"]))
        return results