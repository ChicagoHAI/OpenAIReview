"""Verifier-visible inputs for the PIS evaluator.

This module is the ONLY record -> input path. build_verifier_input copies
exactly the allowlisted verifier-visible fields (_FEATURE_TO_RECORD_KEY) and
refuses any feature whose record key is on the FORBIDDEN_KEYS deny-list, so
evaluation-side information cannot reach inference even by accident.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

from .leakage import FORBIDDEN_KEYS

# Allowlist: feature name -> the record/context key actually read for it.
_FEATURE_TO_RECORD_KEY = {
    "error_type": "error",
    "original": "original",
    "perturbed": "perturbed",
    "contradicts_quote": "contradicts_quote",
    "quote_source": "quote_source",
    "surrounding_context": "surrounding_context",
    "related_passages": "related_passages",
}

DEFAULT_FEATURE_SET: Tuple[str, ...] = tuple(_FEATURE_TO_RECORD_KEY)
FEATURE_SET_VERSION = "default-v1"


def record_uid(record: Mapping[str, Any]) -> str:
    """Globally unique key. perturbation_id alone is NOT unique across papers."""
    try:
        return f"{str(record['paper'])}::{str(record['perturbation_id'])}"
    except KeyError as e:
        raise ValueError(f"record missing required key: {e}") from e


@dataclass(frozen=True)
class VerifierInput:
    """Everything a PIS evaluator may see at inference time. No gold fields.

    The evaluator's public API accepts ONLY this type, so ground truth cannot
    reach it even by accident at the type level.
    """
    uid: str
    paper: str
    perturbation_id: str
    error_type: Optional[str]
    original: str
    perturbed: str
    contradicts_quote: Optional[str]
    quote_source: Optional[str]
    surrounding_context: Optional[str]
    related_passages: Tuple[str, ...]
    feature_set: str

    @property
    def quote_available(self) -> bool:
        return bool(self.contradicts_quote and self.contradicts_quote.strip())


def build_verifier_input(
    record: Mapping[str, Any],
    feature_set: Sequence[str] = DEFAULT_FEATURE_SET,
    context_provider: Optional[Mapping[str, Mapping[str, Any]]] = None,
) -> VerifierInput:
    """Copy ONLY allowlisted, verifier-visible fields from a gold-set record."""
    for feat in feature_set:
        key = _FEATURE_TO_RECORD_KEY.get(feat)
        if key is not None and key in FORBIDDEN_KEYS:
            raise ValueError(
                f"feature {feat!r} would read forbidden evaluation-side field "
                f"{key!r}; refusing to build a leaking VerifierInput")
    ctx: Mapping[str, Any] = {}
    if (("surrounding_context" in feature_set or "related_passages" in feature_set)
            and context_provider is not None):
        ctx = context_provider.get(record_uid(record), {})

    quote = record.get("contradicts_quote") if "contradicts_quote" in feature_set else None
    if quote is not None and not str(quote).strip():
        quote = None

    related: Tuple[str, ...] = ()
    if "related_passages" in feature_set:
        related = tuple(str(p) for p in (ctx.get("related_passages") or []) if str(p).strip())

    surrounding = None
    if "surrounding_context" in feature_set:
        surrounding = ctx.get("surrounding_context") or record.get("surrounding_context") or None

    error_type = None
    if "error_type" in feature_set:
        e = record.get("error")
        error_type = str(e) if e is not None else None

    quote_source = None
    if "quote_source" in feature_set and record.get("quote_source"):
        quote_source = str(record["quote_source"])

    return VerifierInput(
        uid=record_uid(record),
        paper=str(record["paper"]),
        perturbation_id=str(record["perturbation_id"]),
        error_type=error_type,
        original=str(record["original"]),
        perturbed=str(record["perturbed"]),
        contradicts_quote=(str(quote) if quote else None),
        quote_source=quote_source,
        surrounding_context=(str(surrounding) if surrounding else None),
        related_passages=related,
        feature_set=FEATURE_SET_VERSION,
    )


def load_context_file(path: str) -> Dict[str, Dict[str, Any]]:
    """Optional enrichment: JSONL with {"uid": "paper::P...", "surrounding_context": str,
    "related_passages": [str, ...]}. uid must use the composite key."""
    out: Dict[str, Dict[str, Any]] = {}
    for ln, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if "uid" not in obj:
            raise ValueError(f"{path}:{ln}: missing 'uid'")
        if obj["uid"] in out:
            raise ValueError(f"{path}:{ln}: duplicate uid {obj['uid']}")
        out[obj["uid"]] = obj
    return out