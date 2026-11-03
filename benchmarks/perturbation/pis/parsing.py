from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .evidence import EvidenceItem


def reject_json_constant(x: str) -> None:
    raise ValueError(f"non-finite JSON constant not allowed: {x}")


# A backslash that does NOT begin a valid JSON escape sequence
# (\" \\ \/ \b \f \n \r \t \uXXXX). LLMs echoing LaTeX routinely emit e.g.
# "$\mu$" inside JSON strings, which is invalid JSON. The only sensible
# interpretation of such a backslash is a literal one, so we double it.
# Properties (both unit-tested):
#   - identity on already-valid JSON (every backslash in valid JSON begins a
#     valid escape, so the negative lookahead never matches);
#   - only invalid sequences are touched, so the repair cannot change the
#     meaning of any output that would otherwise parse.
# Known limitation (documented, deliberately NOT repaired): a LaTeX command
# whose first letter is a JSON escape letter (e.g. \beta, \theta, \times, \nu,
# \rho, \nabla) IS a valid escape prefix, so json decodes it to a control
# character (e.g. "\beta" -> "\x08eta"). This only garbles human-readable
# audit text; numeric fields (strength/reliability) and polarity enums are
# strictly validated regardless, so interval math is unaffected.
_INVALID_ESCAPE_RE = re.compile(r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})')


def _extract_first_json_object(text: str) -> str:
    start = text.find("{")
    if start == -1:
        raise ValueError("no '{' found in model output")
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    raise ValueError("unbalanced braces in model output")


def _loads_json_repairing(text: str) -> Tuple[Optional[Any], List[str], Optional[str]]:
    """json.loads with LaTeX-backslash repair as a tracked, last-resort fix.

    Returns (obj, repairs, error). Repairs are recorded only together with a
    successful parse, so a 'repaired' status is always auditable to a specific
    note; failures are never silently imputed."""
    try:
        return json.loads(text, parse_constant=reject_json_constant), [], None
    except json.JSONDecodeError as first_err:
        repaired, n = _INVALID_ESCAPE_RE.subn(r'\\\\', text)
        if n == 0:
            return None, [], f"JSON error: {first_err}"
        try:
            obj = json.loads(repaired, parse_constant=reject_json_constant)
        except Exception as second_err:  # noqa: BLE001
            return None, [], (f"JSON error: {second_err} (after doubling {n} "
                              f"invalid backslash escape(s); original error: "
                              f"{first_err})")
        return obj, [f"JSON parse repaired: doubled {n} invalid backslash "
                     f"escape(s) (LaTeX echo) in model JSON"], None
    except ValueError as const_err:  # NaN/Infinity via parse_constant
        return None, [], f"non-finite JSON constant not allowed: {const_err}"


@dataclass
class ParseResult:
    status: str  # "ok" | "repaired" | "failed"
    payload: Optional[Dict[str, Any]] = None
    repairs: List[str] = field(default_factory=list)
    error: Optional[str] = None


def parse_pis_output(text: str) -> ParseResult:
    repairs: List[str] = []
    try:
        candidate = _extract_first_json_object(text)
    except ValueError as e:
        return ParseResult("failed", None, repairs, f"JSON error: {e}")
    obj, json_repairs, err = _loads_json_repairing(candidate)
    if obj is None:
        return ParseResult("failed", None, repairs, err)
    repairs.extend(json_repairs)
    if not isinstance(obj, dict):
        return ParseResult("failed", None, repairs, "top-level JSON is not an object")

    items_raw = obj.get("evidence_items")
    if not isinstance(items_raw, list):
        return ParseResult("failed", None, repairs, "'evidence_items' missing or not a list")
    items: List[EvidenceItem] = []
    for j, it in enumerate(items_raw):
        if not isinstance(it, dict):
            return ParseResult("failed", None, repairs, f"evidence_items[{j}] is not an object")
        try:
            item, item_repairs = EvidenceItem.from_payload(it)
        except ValueError as e:
            return ParseResult("failed", None, repairs, f"evidence_items[{j}]: {e}")
        repairs.extend(f"evidence_items[{j}]: {r}" for r in item_repairs)
        items.append(item)

    conf = obj.get("self_reported_confidence_h")
    if conf is not None:
        if isinstance(conf, bool) or not isinstance(conf, (int, float)) or not math.isfinite(conf):
            repairs.append("self_reported_confidence_h invalid; dropped")
            conf = None
        else:
            conf = float(conf)
            if not (0.0 <= conf <= 1.0):
                cl = min(1.0, max(0.0, conf))
                repairs.append(f"self_reported_confidence_h clamped {conf} -> {cl}")
                conf = cl

    return ParseResult("repaired" if repairs else "ok",
                       {"evidence_items": items, "self_reported_confidence_h": conf},
                       repairs, None)


def parse_scalar_output(text: str) -> ParseResult:
    repairs: List[str] = []
    try:
        candidate = _extract_first_json_object(text)
    except ValueError as e:
        return ParseResult("failed", None, repairs, f"JSON error: {e}")
    obj, json_repairs, err = _loads_json_repairing(candidate)
    if obj is None:
        return ParseResult("failed", None, repairs, err)
    repairs.extend(json_repairs)
    if not isinstance(obj, dict) or "p_substantive" not in obj:
        return ParseResult("failed", None, repairs, "missing key 'p_substantive'")
    v = obj["p_substantive"]
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return ParseResult("failed", None, repairs, "'p_substantive' is not a finite number")
    v = float(v)
    if not (0.0 <= v <= 1.0):
        cl = min(1.0, max(0.0, v))
        repairs.append(f"p_substantive clamped {v} -> {cl}")
        v = cl
    return ParseResult("repaired" if repairs else "ok", {"p_substantive": v}, repairs, None)