"""Canonical severity tiers and per-system normalization.

The perturbation benchmark, the conference study analyses, and the viz layer
all want to compare comment severities across review systems. Each system uses
its own native vocabulary, so before any cross-system comparison the raw value
must be mapped to the canonical 3-tier scale used by openaireview itself:

    major     - Undermines a key claim/methodology; affects conclusions.
    moderate  - Real error or gap that is localized and fixable.
    minor     - Framing concern, mild overclaim, or resolvable ambiguity.

Per-system maps:

  * openaireview: identity. Output is already in {major, moderate, minor}.
  * coarse:       {critical, major, minor} -> {major, moderate, minor}
                  (shift down one tier; same mapping that the conference-study
                  scripts in benchmarks/conference_study/analyses/ use).
  * reviewer3:    integer 1..4 per their OpenAPI spec, where
                  1=Critical, 2=Major, 3=Minor, 4=Editorial.
                  Compressed to the 3-tier scale by collapsing R3 Minor and
                  Editorial into `minor`, since in practice R3 tags substantive
                  -but-lower-importance findings as Editorial rather than style
                  notes. Confirm with the vendor if the label is later clarified.

The conference_study analyses currently inline `COARSE_SEVERITY_MAP` (see
`benchmarks/conference_study/analyses/compute_auc.py` and `report_scaleup.py`).
Once those analyses are co-resident with this module they should import
`COARSE_SEVERITY_MAP` and `normalize_severity` from here instead.
"""

from __future__ import annotations


TIERS: tuple[str, ...] = ("major", "moderate", "minor")


# openaireview methods emit canonical tier strings directly.
OPENAIREVIEW_SEVERITY_MAP: dict[str, str] = {t: t for t in TIERS}

# coarse uses {minor, major, critical}. Shift down one level.
COARSE_SEVERITY_MAP: dict[str, str] = {
    "critical": "major",
    "major": "moderate",
    "minor": "minor",
}

# Reviewer 3 spec: 1=Critical, 2=Major, 3=Minor, 4=Editorial.
# Compress to 3 tiers; Editorial collapses with Minor (see module docstring).
REVIEWER3_SEVERITY_MAP: dict[int, str] = {
    1: "major",
    2: "moderate",
    3: "minor",
    4: "minor",
}


def normalize_severity(system: str, raw: object) -> str | None:
    """Map a system-native severity value to the canonical 3-tier scale.

    Returns None for unrecognized values so callers can decide whether to drop
    the comment, default it, or warn.

    `system` is the registry key matching `benchmarks/perturbation/systems/`:
    'openaireview', 'coarse', or 'reviewer3'.
    """
    if raw is None:
        return None
    sysn = system.lower()
    if sysn == "reviewer3":
        if isinstance(raw, int):
            return REVIEWER3_SEVERITY_MAP.get(raw)
        if isinstance(raw, str) and raw.lower() in TIERS:
            return raw.lower()  # JSONs may already store canonical strings
        # tolerate the str-form for hand-written test fixtures
        try:
            return REVIEWER3_SEVERITY_MAP.get(int(raw))
        except (TypeError, ValueError):
            return None
    if not isinstance(raw, str):
        return None
    s = raw.lower()
    if sysn == "coarse":
        return COARSE_SEVERITY_MAP.get(s)
    if sysn == "openaireview":
        return OPENAIREVIEW_SEVERITY_MAP.get(s)
    # unknown system -> pass through if already canonical
    return s if s in TIERS else None
