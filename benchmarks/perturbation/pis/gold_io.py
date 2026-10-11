from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .inputs import record_uid

KNOWN_GOLD_LABELS = ("substantive", "typo-shaped", "not-an-error")
KNOWN_ERROR_TYPES = ("index_or_subscript", "numeric_parameter",
                     "operator_or_sign", "symbol_binding")


def _reject_constant(x: str) -> None:
    raise ValueError(f"non-finite JSON constant not allowed: {x}")


def _parse_jsonl(text: str, path: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for ln, line in enumerate(text.splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line, parse_constant=_reject_constant))
        except json.JSONDecodeError as e:
            raise ValueError(f"{path}:{ln}: invalid JSON: {e.msg} (col {e.colno})") from e
    return records


def _parse_gold_text(text: str, path: str) -> List[Dict[str, Any]]:
    """Parse the gold set file.

    Accepted formats, in priority order:
      (a) a single JSON object {"examples": [...]}
      (b) a bare JSON array [...]
      (c) JSONL: one JSON object per line

    A JSONL file whose first record is an object ALSO starts with '{', so the
    single-document parse is attempted first and per-line parsing is the
    documented fallback when that fails (e.g. 'Extra data'). Parse errors from
    the fallback propagate with file:line context.
    """
    stripped = text.lstrip()
    if not stripped:
        raise ValueError(f"{path}: empty file")
    if stripped[0] not in "[{":
        records = _parse_jsonl(text, path)
        if not records:
            raise ValueError(f"{path}: no non-empty JSON lines")
        return records
    try:
        obj = json.loads(text, parse_constant=_reject_constant)
    except json.JSONDecodeError as whole_err:
        records = _parse_jsonl(text, path)
        if not records:
            raise ValueError(
                f"{path}: not a valid single JSON document ({whole_err.msg} at "
                f"line {whole_err.lineno}, col {whole_err.colno}) and contains "
                "no non-empty JSON lines") from whole_err
        return records
    if isinstance(obj, dict):
        records = obj.get("examples")
        if not isinstance(records, list):
            raise ValueError(
                'gold set JSON object has no "examples" list (a single-record '
                'file is ambiguous; wrap it as {"examples": [...]})')
        return records
    if isinstance(obj, list):
        return obj
    raise ValueError("gold set must be a JSON object with 'examples' or a JSON array")


@dataclass
class GoldSetReport:
    n_examples: int = 0
    duplicate_uids: List[str] = field(default_factory=list)
    unknown_error_types: Dict[str, int] = field(default_factory=dict)
    unknown_gold_labels: Dict[str, int] = field(default_factory=dict)
    label_counts: Dict[str, int] = field(default_factory=dict)
    error_type_counts: Dict[str, int] = field(default_factory=dict)
    quote_source_counts: Dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_gold_set(path: str) -> Tuple[List[Dict[str, Any]], GoldSetReport]:
    """Load + validate the verifier gold set (formats: see _parse_gold_text).

    Duplicates FAIL LOUDLY (never silently dropped: a silent drop could bias
    every downstream join)."""
    text = Path(path).read_text(encoding="utf-8")
    records = _parse_gold_text(text, str(path))
    if not isinstance(records, list) or not records:
        raise ValueError("gold set is empty or not a list")

    report = GoldSetReport(n_examples=len(records))
    seen = set()
    out: List[Dict[str, Any]] = []
    for i, rec in enumerate(records):
        if not isinstance(rec, dict):
            raise ValueError(f"record {i} is not an object")
        for key in ("paper", "perturbation_id", "original", "perturbed", "gold_label"):
            v = rec.get(key)
            if v is None or (isinstance(v, str) and not v.strip()):
                raise ValueError(f"record {i}: missing/empty required key {key!r}")
        uid = record_uid(rec)
        if uid in seen:
            raise ValueError(
                f"duplicate uid {uid!r} (paper+perturbation_id) in gold set; "
                "join integrity requires unique keys")
        seen.add(uid)

        rec = dict(rec)
        if not str(rec.get("contradicts_quote") or "").strip():
            rec["contradicts_quote"] = None

        lab = str(rec["gold_label"]).strip().lower().replace("_", "-")
        report.label_counts[lab] = report.label_counts.get(lab, 0) + 1
        if lab not in KNOWN_GOLD_LABELS:
            report.unknown_gold_labels[lab] = report.unknown_gold_labels.get(lab, 0) + 1
        err = str(rec.get("error")) if rec.get("error") else "unknown"
        report.error_type_counts[err] = report.error_type_counts.get(err, 0) + 1
        if err not in KNOWN_ERROR_TYPES:
            report.unknown_error_types[err] = report.unknown_error_types.get(err, 0) + 1
        qsrc = str(rec.get("quote_source")) if rec.get("quote_source") else "none-given"
        report.quote_source_counts[qsrc] = report.quote_source_counts.get(qsrc, 0) + 1
        out.append(rec)
    return out, report