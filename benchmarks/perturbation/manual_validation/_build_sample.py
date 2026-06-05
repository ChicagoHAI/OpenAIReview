"""Sample injected perturbations for manual quality validation.

Samples 10 perturbations per top-level TYPE (Surface, Claim, Logic, Experimental)
= 40 total, guaranteeing each SUBTYPE appears at least once and spreading across
papers. Reads the kept (verified, substantive) perturbations under
data/perturbations_filtered/. Writes samples.md (human-readable checklist) and
samples.json (raw records) into this directory.
"""
import json, glob, os, random, collections
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent          # .../perturbation
FILT = BASE / "data" / "perturbations_filtered"
OUT  = Path(__file__).resolve().parent                 # .../manual_validation
SEED = 42
PER_TYPE = 10
MAX_PER_PAPER = 3                                       # diversity cap (relaxed if needed)

SUBTYPE_TO_TYPE = {
    "numeric_parameter": "Surface", "operator_or_sign": "Surface",
    "index_or_subscript": "Surface", "computation": "Surface", "symbol_binding": "Surface",
    "incorrect_claim_theoretical": "Claim", "incorrect_statement_empirical": "Claim",
    "missing_case": "Logic", "induction": "Logic",
    "circular_reasoning": "Logic", "invalid_implication": "Logic",
    "misinterp": "Experimental", "causal_reversed": "Experimental", "p_hacking": "Experimental",
}
TYPE_ORDER = ["Surface", "Claim", "Logic", "Experimental"]
SUBTYPE_LABEL = {
    "numeric_parameter": "Numeric", "operator_or_sign": "Operator / Sign",
    "index_or_subscript": "Index / Subscript", "computation": "Computation",
    "symbol_binding": "Symbol binding (deprecated)",
    "incorrect_claim_theoretical": "False theoretical claim",
    "incorrect_statement_empirical": "False empirical claim",
    "missing_case": "Missing case", "induction": "Induction error",
    "circular_reasoning": "Circular reasoning", "invalid_implication": "Invalid implication",
    "misinterp": "Misinterpretation of results", "causal_reversed": "Reversed causality",
    "p_hacking": "P-hacking",
}


def load_all():
    cands = []
    for f in glob.glob(str(FILT / "*/all/*/*/*kept_perturbations.json")):
        rel = Path(f).relative_to(FILT)
        domain = rel.parts[0]
        paper = rel.parts[2]
        d = json.load(open(f))
        for p in d.get("perturbations", []):
            sub = p.get("error")
            typ = SUBTYPE_TO_TYPE.get(sub)
            if typ is None:
                continue
            cands.append({
                "uid": len(cands),  # globally unique (perturbation_id repeats across papers)
                "type": typ, "subtype": sub, "domain": domain, "paper": paper,
                "paper_title": d.get("paper_title", ""),
                "perturbation_id": p.get("perturbation_id"),
                "original": p.get("original", ""), "perturbed": p.get("perturbed", ""),
                "why_wrong": p.get("why_wrong", ""), "quote": p.get("quote", ""),
                "reason": p.get("reason", ""),
            })
    return cands


def select(by_type, rng):
    """Pick PER_TYPE per type while guaranteeing (a) every subtype appears >=1,
    (b) every domain appears >=1 globally, and spreading across domains/papers.

    Shared global counters let the fill steps balance domains and papers across
    all types at once.
    """
    selected = {t: [] for t in TYPE_ORDER}
    used = set()
    dom_ct, paper_ct = collections.Counter(), collections.Counter()
    pools = {t: list(by_type[t]) for t in TYPE_ORDER}
    for t in TYPE_ORDER:
        rng.shuffle(pools[t])
    all_domains = sorted({c["domain"] for t in TYPE_ORDER for c in pools[t]})

    def take(c):
        selected[c["type"]].append(c); used.add(c["uid"])
        dom_ct[c["domain"]] += 1; paper_ct[c["paper"]] += 1

    def avail(t):  # candidates of type t not yet used, if type has a free slot
        if len(selected[t]) >= PER_TYPE:
            return []
        return [c for c in pools[t] if c["uid"] not in used]

    # 1) subtype coverage (prefer least-used domain, then paper)
    for t in TYPE_ORDER:
        by_sub = collections.defaultdict(list)
        for c in pools[t]:
            by_sub[c["subtype"]].append(c)
        for sub in sorted(by_sub):
            if len(selected[t]) >= PER_TYPE:
                break
            cand = min(by_sub[sub], key=lambda c: (dom_ct[c["domain"]], paper_ct[c["paper"]]))
            if cand["uid"] not in used:
                take(cand)

    # 2) domain coverage: for each uncovered domain, place one (in any type w/ a free slot)
    for d in all_domains:
        if dom_ct[d] > 0:
            continue
        cands = [c for t in TYPE_ORDER for c in avail(t) if c["domain"] == d]
        if cands:
            take(min(cands, key=lambda c: paper_ct[c["paper"]]))

    # 3) fill each type to PER_TYPE, always taking the least-used domain then paper
    for t in TYPE_ORDER:
        while len(selected[t]) < PER_TYPE:
            pool = avail(t)
            if not pool:
                break
            take(min(pool, key=lambda c: (dom_ct[c["domain"]], paper_ct[c["paper"]])))
    return selected


def md_block(text):
    """Render possibly-LaTeX verbatim text as a fenced code block."""
    text = (text or "").rstrip()
    return f"```\n{text}\n```"


def main():
    rng = random.Random(SEED)
    cands = load_all()
    by_type = collections.defaultdict(list)
    for c in cands:
        by_type[c["type"]].append(c)

    chosen = select(by_type, rng)

    OUT.mkdir(parents=True, exist_ok=True)
    # raw json
    flat = [{"idx": i + 1, **c} for i, c in enumerate(
        [c for typ in TYPE_ORDER for c in chosen[typ]])]
    (OUT / "samples.json").write_text(json.dumps(flat, indent=2))

    # markdown checklist
    lines = []
    lines.append("# Injected-perturbation validation sample\n")
    lines.append(f"40 perturbations: {PER_TYPE} per type (Surface, Claim, Logic, Experimental), "
                 "each subtype covered ≥ once, drawn from the verified/kept set "
                 "(`data/perturbations_filtered/`).\n")
    lines.append("For each: **Passage** = original text, **Perturbation** = injected replacement, "
                 "**Why it errs** = why it breaks internal consistency, "
                 "**Contradicting evidence** = the passage elsewhere it conflicts with.\n")
    # coverage summary
    lines.append("## Coverage\n")
    for typ in TYPE_ORDER:
        subs = collections.Counter(c["subtype"] for c in chosen[typ])
        summ = ", ".join(f"{SUBTYPE_LABEL[s]} ({n})" for s, n in sorted(subs.items()))
        lines.append(f"- **{typ}** ({len(chosen[typ])}): {summ}")
    lines.append("")

    idx = 0
    for typ in TYPE_ORDER:
        lines.append(f"\n---\n\n## {typ}\n")
        for c in chosen[typ]:
            idx += 1
            lines.append(f"### {idx}. {typ} — {SUBTYPE_LABEL.get(c['subtype'], c['subtype'])}")
            lines.append(f"`{c['domain']}` / `{c['paper']}` / `{c['perturbation_id']}`\n")
            lines.append("**Passage (original):**")
            lines.append(md_block(c["original"]))
            lines.append("**Perturbation (injected):**")
            lines.append(md_block(c["perturbed"]))
            lines.append(f"**Why it causes an error:** {c['why_wrong']}\n")
            if c["quote"].strip():
                lines.append("**Contradicting evidence (quote):**")
                lines.append(md_block(c["quote"]))
            if c["reason"].strip():
                lines.append(f"**Verifier note:** {c['reason']}\n")
            lines.append("**Your assessment:** ( ) valid error  ( ) not an error  ( ) unsure")
            lines.append("**Notes:** \n")
    (OUT / "samples.md").write_text("\n".join(lines))

    print(f"candidates loaded: {len(cands)}")
    for typ in TYPE_ORDER:
        print(f"  {typ}: pool={len(by_type[typ])}, sampled={len(chosen[typ])}, "
              f"papers={len(set(c['paper'] for c in chosen[typ]))}")
    print(f"wrote {OUT/'samples.md'} and {OUT/'samples.json'}")


if __name__ == "__main__":
    main()
