"""Sample OpenAIReview (GPT-5.5) comments for manual severity validation.

For each of the 4 quality proxies, pick one low-quality and one high-quality
paper from the frontier subset, and sample 5 comments from each (spread across
severity tiers where possible) = 40 comments. Writes samples.md (checklist) and
samples.json into this directory.
"""
import json, random, collections
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent              # conference_study
MANIFEST = BASE / "manifests" / "v2_frontier" / "combined.json"
RESULTS = BASE / "results" / "frontier_subset_progressive"
MKEY = "progressive__gpt-5.5"
OUT = Path(__file__).resolve().parent
SEED, PER_PAPER = 42, 5
PAIR_NAME = {1: "Community-level", 2: "Conference-level", 3: "Reviewer-level", 4: "Composite"}


def comments_for(slug):
    p = RESULTS / f"{slug}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text())
    return d.get("methods", {}).get(MKEY, {}).get("comments", [])


def pick_paper(cands, rng):
    """First candidate (shuffled) with >= PER_PAPER comments, else the most-commented."""
    rng.shuffle(cands)
    ok = [c for c in cands if len(comments_for(c["slug"])) >= PER_PAPER]
    if ok:
        return ok[0]
    return max(cands, key=lambda c: len(comments_for(c["slug"])))


def pick_comments(cmts, rng):
    """5 comments, covering each present severity tier at least once, then fill."""
    cmts = list(cmts); rng.shuffle(cmts)
    by_sev = collections.defaultdict(list)
    for c in cmts:
        by_sev[c.get("severity", "?")].append(c)
    sel, used = [], set()
    for sev in sorted(by_sev):                      # one per tier present
        c = by_sev[sev][0]
        sel.append(c); used.add(c["id"])
    for c in cmts:                                   # fill
        if len(sel) >= PER_PAPER:
            break
        if c["id"] not in used:
            sel.append(c); used.add(c["id"])
    return sel[:PER_PAPER]


def main():
    rng = random.Random(SEED)
    papers = json.loads(MANIFEST.read_text())["papers"]
    # pair -> side -> [papers]
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for p in papers:
        for m in p["pair_memberships"]:
            groups[m["pair"]][m["side"]].append(p)

    flat, md = [], []
    md.append("# Comment severity validation sample\n")
    md.append("40 OpenAIReview (GPT-5.5) comments: 1 low + 1 high paper per quality proxy, "
              "5 comments each (spread across severity tiers where available).\n")
    md.append("For each comment, the model's **LLM severity** is shown; mark **your severity** "
              "and whether it's substantive **signal** or **cosmetic**.\n")

    idx = 0
    for pair in sorted(groups):
        md.append(f"\n---\n\n## {PAIR_NAME.get(pair, f'Pair {pair}')} proxy\n")
        for side, tag in (("low", "WEAK / low-quality"), ("high", "STRONG / high-quality")):
            paper = pick_paper(list(groups[pair][side]), rng)
            cmts = pick_comments(comments_for(paper["slug"]), rng)
            md.append(f"### {tag} — {paper['title']}")
            md.append(f"`{paper['slug']}` · decision: {paper.get('normalized_decision')} · "
                      f"review score avg: {paper.get('review_score_avg')} · "
                      f"cites/yr: {paper.get('cites_per_year')}\n")
            for c in cmts:
                idx += 1
                flat.append({"idx": idx, "proxy": PAIR_NAME.get(pair), "group": side,
                             "paper_slug": paper["slug"], "paper_title": paper["title"],
                             **{k: c.get(k) for k in
                                ("id", "title", "quote", "explanation", "comment_type",
                                 "paragraph_index", "severity")}})
                md.append(f"**{idx}. [{c.get('severity', '?').upper()}] {c.get('title', '')}**  "
                          f"_(type: {c.get('comment_type')}, ¶{c.get('paragraph_index')})_")
                if (c.get("quote") or "").strip():
                    md.append(f"> Quote: {c['quote']}")
                md.append(f"{c.get('explanation', '')}\n")
                md.append("Your severity: ( ) major  ( ) moderate  ( ) minor    |    "
                          "( ) signal  ( ) cosmetic")
                md.append("Notes: \n")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "samples.json").write_text(json.dumps(flat, indent=2))
    (OUT / "samples.md").write_text("\n".join(md))

    # coverage report
    print(f"total comments: {len(flat)}")
    sev = collections.Counter(x["severity"] for x in flat)
    print("LLM severity mix:", dict(sev))
    print("papers:", len({x["paper_slug"] for x in flat}),
          "| proxies:", len({x["proxy"] for x in flat}))
    print(f"wrote {OUT/'samples.md'} and {OUT/'samples.json'}")


if __name__ == "__main__":
    main()
