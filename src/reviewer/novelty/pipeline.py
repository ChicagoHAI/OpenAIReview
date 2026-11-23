"""End-to-end novelty assessment.

    submission ──► extract claims ──► search queries ──► arXiv / S2 / OpenAlex
                                                               │
                         dedupe · drop self & post-dated work ◄┘
                                          │
                     chunk (title+abstract, optional full text)
                                          │
                  ┌──────────── BM25 index ◄──┴──► embed ──► ANN / exact index
                  │                                              │
       per claim: top-N lexical                     top-N dense (cosine)
                  └──────────► Reciprocal Rank Fusion ◄──────────┘
                                          │
                     top-k evidence per claim (≤ 2 chunks per paper)
                                          │
                  optional LLM judge: anticipated / partial / novel
                                          │
                     NoveltyReport (JSON + Markdown)
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path

import numpy as np

from .ann import build_index
from .bm25 import BM25, STOPWORDS, tokenize
from .chunking import chunk_document, extract_claims
from .embeddings import Embedder, get_embedder
from .fusion import reciprocal_rank_fusion
from .sources import (
    arxiv_id_cutoff, dedupe_candidates, extract_arxiv_id, filter_candidates,
    infer_cutoff, search_all,
)
from .types import CandidatePaper, Chunk, ClaimAssessment, Hit, NoveltyReport

VERDICT_WEIGHT = {"anticipated": 0.0, "partial": 0.5, "novel": 1.0}

_GENERIC = STOPWORDS | {
    "paper", "work", "study", "propose", "proposed", "present", "introduce", "first",
    "novel", "new", "approach", "method", "framework", "model", "results", "show",
    "demonstrate", "achieve", "significantly", "outperform", "state", "art",
    "experiments", "extensive", "existing", "prior", "previous", "best", "knowledge",
    "contribution", "contributions", "main", "able", "effective", "efficient",
    "examine", "examines", "investigate", "investigates", "whether", "study", "studies",
    "find", "finds", "found", "evidence", "suggest", "suggests", "using", "approximately",
}


@dataclass
class NoveltyConfig:
    sources: list[str] = field(default_factory=lambda: ["arxiv", "semantic_scholar", "openalex"])
    per_query: int = 25
    max_queries: int = 8
    llm_queries: bool = False
    max_claims: int = 12
    before: str | None = None          # ISO date; ignore work published after this
    self_arxiv_id: str = ""
    embedder: str = "auto"
    ann: str = "auto"
    exact_threshold: int = 5000
    chunk_tokens: int = 200
    pool: int = 100                     # candidates per retriever before fusion
    top_k: int = 5                      # evidence chunks kept per claim
    max_per_paper: int = 2
    rrf_k: int = 60
    bm25_weight: float = 1.0
    dense_weight: float = 1.0
    full_text: int = 0                  # fetch arXiv HTML full text for top-N papers
    judge: bool = True
    judge_top: int = 3                  # excerpts shown to the judge per claim
    model: str = "anthropic/claude-opus-4-6"
    reasoning_effort: str | None = None
    cache_dir: str | None = "~/.cache/openaireview/novelty"
    corpus_dir: str | None = None


# ---------------------------------------------------------------------------
# Query generation
# ---------------------------------------------------------------------------

def _keywords(text: str, n: int = 7) -> list[str]:
    body = text.split("\n", 1)[-1]  # drop the contextual header
    words = re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", body)
    out, seen = [], set()
    for w in words:
        lw = w.lower()
        if lw in _GENERIC or lw in seen:
            continue
        seen.add(lw)
        out.append(w)
        if len(out) >= n:
            break
    return out


def build_queries(title: str, claims: list[Chunk], max_queries: int = 8) -> list[str]:
    """Heuristic queries: the title, then keyword distillations of each claim."""
    queries: list[str] = []
    clean_title = re.sub(r"\s*\[[A-Z]+\]\s*$", "", title or "").strip()
    if clean_title:
        queries.append(clean_title)
    for c in claims:
        kw = _keywords(c.text)
        if len(kw) >= 3:
            q = " ".join(kw)
            if q.lower() not in {x.lower() for x in queries}:
                queries.append(q)
        if len(queries) >= max_queries:
            break
    return queries


def llm_expand_queries(title: str, claims: list[Chunk], cfg: NoveltyConfig, n: int = 5):
    """Ask the LLM for extra queries, especially older/alternative terminology --
    the classic way lexical search misses prior work."""
    from ..client import chat
    from ..prompts import NOVELTY_QUERY_PROMPT

    prompt = NOVELTY_QUERY_PROMPT.format(
        n=n, title=title, claims="\n".join(f"- {c.text.split(chr(10), 1)[-1][:500]}" for c in claims[:6]))
    text, usage = chat([{"role": "user", "content": prompt}], model=cfg.model,
                       max_tokens=1024, reasoning_effort=cfg.reasoning_effort)
    m = re.search(r"\[.*\]", text, re.DOTALL)
    try:
        qs = [q.strip() for q in json.loads(m.group(0)) if isinstance(q, str) and q.strip()] if m else []
    except json.JSONDecodeError:
        qs = []
    return qs[:n], usage


# ---------------------------------------------------------------------------
# Persistent corpus (where ANN pays off)
# ---------------------------------------------------------------------------

class CorpusStore:
    """Append-only local library of candidate papers, chunks and vectors.

    Layout: ``papers.jsonl``, ``chunks.jsonl``, ``vectors.npy``, ``meta.json``.
    Vectors are only reused when produced by the same embedder.
    """

    def __init__(self, path: str | Path, embedder_name: str):
        self.path = Path(path).expanduser()
        self.embedder_name = embedder_name
        self.papers: dict[str, CandidatePaper] = {}
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None
        self._load()

    def _load(self) -> None:
        meta_f = self.path / "meta.json"
        if not meta_f.exists():
            return
        meta = json.loads(meta_f.read_text())
        for line in (self.path / "papers.jsonl").read_text().splitlines():
            if line.strip():
                p = CandidatePaper(**json.loads(line))
                self.papers[p.paper_id] = p
        self.chunks = [Chunk(**json.loads(l))
                       for l in (self.path / "chunks.jsonl").read_text().splitlines() if l.strip()]
        vec_f = self.path / "vectors.npy"
        if meta.get("embedder") == self.embedder_name and vec_f.exists():
            vecs = np.load(vec_f)
            if vecs.shape[0] == len(self.chunks):
                self.vectors = vecs

    def add(self, papers: list[CandidatePaper], chunks: list[Chunk], embedder: Embedder) -> None:
        for p in papers:
            self.papers.setdefault(p.paper_id, p)
        known = {c.chunk_id for c in self.chunks}
        new = [c for c in chunks if c.chunk_id not in known]
        if self.vectors is None:
            self.chunks.extend(new)
            self.vectors = embedder.embed([c.text for c in self.chunks], kind="passage")
        elif new:
            self.chunks.extend(new)
            self.vectors = np.vstack([self.vectors, embedder.embed([c.text for c in new], kind="passage")])

    def save(self) -> None:
        self.path.mkdir(parents=True, exist_ok=True)
        (self.path / "papers.jsonl").write_text(
            "\n".join(json.dumps(p.to_dict(include_text=False)) for p in self.papers.values()) + "\n")
        (self.path / "chunks.jsonl").write_text(
            "\n".join(json.dumps(c.to_dict()) for c in self.chunks) + "\n")
        if self.vectors is not None:
            np.save(self.path / "vectors.npy", self.vectors)
        (self.path / "meta.json").write_text(json.dumps(
            {"embedder": self.embedder_name, "n_chunks": len(self.chunks),
             "n_papers": len(self.papers)}, indent=2))


# ---------------------------------------------------------------------------
# Hybrid retrieval
# ---------------------------------------------------------------------------

class HybridRetriever:
    def __init__(self, chunks: list[Chunk], vectors: np.ndarray, cfg: NoveltyConfig):
        self.chunks = chunks
        self.vectors = vectors
        self.cfg = cfg
        self.bm25 = BM25.from_texts([c.text for c in chunks])
        self.index = build_index(vectors, backend=cfg.ann, exact_threshold=cfg.exact_threshold)

    def search(self, query_text: str, query_vec: np.ndarray) -> tuple[list[Hit], float | None]:
        cfg = self.cfg
        pool = min(cfg.pool, len(self.chunks))
        if pool == 0:
            return [], None
        lexical = self.bm25.top_k(tokenize(query_text.split("\n", 1)[-1]), pool)
        ids, sims = self.index.search(query_vec[None, :], pool)
        # faiss pads with -1 when it finds fewer than k neighbours; drop those.
        pairs = [(i, s) for i, s in zip(ids[0].tolist(), sims[0].tolist()) if i >= 0]
        dense_ids, dense_sims = [i for i, _ in pairs], [s for _, s in pairs]

        bm25_rank = {d: r for r, (d, _) in enumerate(lexical, 1)}
        bm25_score = dict(lexical)
        dense_rank = {d: r for r, d in enumerate(dense_ids, 1)}
        fused = reciprocal_rank_fusion(
            [[d for d, _ in lexical], dense_ids], k=cfg.rrf_k,
            weights=[cfg.bm25_weight, cfg.dense_weight])

        hits: list[Hit] = []
        per_paper: dict[str, int] = defaultdict(int)
        for doc, score in fused:
            ch = self.chunks[doc]
            if per_paper[ch.doc_id] >= cfg.max_per_paper:
                continue
            per_paper[ch.doc_id] += 1
            hits.append(Hit(
                chunk=ch, fused_score=score,
                dense_score=float(self.vectors[doc] @ query_vec),  # exact cosine, even for BM25-only hits
                bm25_score=bm25_score.get(doc), dense_rank=dense_rank.get(doc),
                bm25_rank=bm25_rank.get(doc)))
            if len(hits) >= cfg.top_k:
                break

        z = None
        if len(dense_sims) >= 5:
            rest = np.asarray(dense_sims[1:], dtype=np.float64)
            sd = rest.std()
            z = float((dense_sims[0] - rest.mean()) / sd) if sd > 1e-9 else None
        return hits, z


# ---------------------------------------------------------------------------
# LLM judge
# ---------------------------------------------------------------------------

def judge_claim(assessment: ClaimAssessment, papers: dict[str, CandidatePaper],
                cfg: NoveltyConfig) -> dict:
    from ..client import chat
    from ..prompts import NOVELTY_JUDGE_PROMPT

    shown = assessment.hits[: cfg.judge_top]
    evidence = []
    for i, h in enumerate(shown, 1):
        p = papers.get(h.chunk.doc_id)
        meta = f"{p.title} ({p.year or 'n.d.'})" if p else h.chunk.doc_id
        evidence.append(f"[{i}] {meta}\n{h.chunk.text.split(chr(10), 1)[-1][:1500]}")
    prompt = NOVELTY_JUDGE_PROMPT.format(
        current_date=date.today().isoformat(),
        claim=assessment.claim.text.split("\n", 1)[-1],
        evidence="\n\n".join(evidence) or "(none retrieved)")
    text, usage = chat([{"role": "user", "content": prompt}], model=cfg.model,
                       max_tokens=2048, reasoning_effort=cfg.reasoning_effort)
    parsed = parse_judge_response(text)
    idx = parsed.get("evidence_index")
    if isinstance(idx, int) and 1 <= idx <= len(shown):
        assessment.evidence_chunk_id = shown[idx - 1].chunk.chunk_id
    assessment.verdict = parsed.get("verdict")
    assessment.explanation = parsed.get("explanation", "")
    assessment.key_difference = parsed.get("key_difference", "")
    return usage


def parse_judge_response(text: str) -> dict:
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    data: dict = {}
    if m:
        try:
            data = json.loads(m.group(0))
        except json.JSONDecodeError:
            data = {}
    verdict = str(data.get("verdict", "")).strip().lower()
    if verdict not in VERDICT_WEIGHT:
        verdict = None
    idx = data.get("evidence_index")
    try:
        idx = int(idx) if idx is not None else None
    except (TypeError, ValueError):
        idx = None
    return {"verdict": verdict, "evidence_index": idx,
            "explanation": str(data.get("explanation", "") or ""),
            "key_difference": str(data.get("key_difference", "") or "")}


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def candidate_chunks(p: CandidatePaper, max_tokens: int) -> list[Chunk]:
    chunks = chunk_document(f"## Abstract\n\n{p.abstract}", doc_id=p.paper_id,
                            title=p.title, max_tokens=max_tokens)
    for c in chunks:
        c.kind = "abstract"
        c.chunk_id = f"{p.paper_id}#abs{c.position}"
    if p.full_text:
        body = chunk_document(p.full_text, doc_id=p.paper_id, title=p.title, max_tokens=max_tokens)
        for c in body:
            c.chunk_id = f"{p.paper_id}#body{c.position}"
        chunks.extend(body)
    return chunks


def _fetch_full_text(p: CandidatePaper) -> str:
    from ..parsers import parse_arxiv_html
    try:
        _title, text = parse_arxiv_html(f"https://arxiv.org/html/{p.arxiv_id}")
        return text
    except Exception as e:  # many older papers have no HTML version
        print(f"  (no full text for {p.arxiv_id}: {e})")
        return ""


def _aggregate_papers(claims: list[ClaimAssessment], papers: dict[str, CandidatePaper],
                      limit: int = 15) -> list[dict]:
    score: dict[str, float] = defaultdict(float)
    best_sim: dict[str, float] = defaultdict(lambda: -1.0)
    n_claims: dict[str, set] = defaultdict(set)
    for ci, ca in enumerate(claims):
        for h in ca.hits:
            pid = h.chunk.doc_id
            score[pid] += h.fused_score
            best_sim[pid] = max(best_sim[pid], h.dense_score or -1.0)
            n_claims[pid].add(ci)
    out = []
    for pid, s in sorted(score.items(), key=lambda kv: -kv[1])[:limit]:
        p = papers.get(pid)
        out.append({
            "paper_id": pid, "title": p.title if p else pid, "year": p.year if p else None,
            "url": p.url if p else "", "fused_score": round(s, 5),
            "max_similarity": round(best_sim[pid], 4), "claims_matched": len(n_claims[pid]),
        })
    return out


def run_novelty(title: str, content: str, slug: str, cfg: NoveltyConfig,
                log=print) -> NoveltyReport:
    title = re.sub(r"\s*\[[A-Z]+\]\s*$", "", title or "").strip()  # drop " [PDF]" format tag
    title = re.sub(r"\s+", " ", title)  # incl. non-breaking spaces from HTML titles
    report = NoveltyReport(paper_slug=slug, title=title,
                           config={k: v for k, v in asdict(cfg).items()})
    self_arxiv = cfg.self_arxiv_id or extract_arxiv_id(slug)

    # 1. Claims (queries)
    claims = extract_claims(content, title=title, max_claims=cfg.max_claims)
    log(f"  {len(claims)} claims extracted (1 abstract + {len(claims) - 1} contribution sentences)")
    if not claims:
        report.score_basis = "no claims found"
        return report

    # 2. Web search
    queries = build_queries(title, claims, cfg.max_queries)
    if cfg.llm_queries:
        extra, usage = llm_expand_queries(title, claims, cfg)
        report.total_prompt_tokens += usage["prompt_tokens"]
        report.total_completion_tokens += usage["completion_tokens"]
        queries += [q for q in extra if q.lower() not in {x.lower() for x in queries}]
    report.queries = queries
    # Prior work must predate the submission. Use --before if given; otherwise
    # start from the arXiv id's month and refine with the paper's own record.
    before = cfg.before or arxiv_id_cutoff(self_arxiv)
    log(f"  Searching {', '.join(cfg.sources)} with {len(queries)} queries...")
    raw = search_all(queries, cfg.sources, per_query=cfg.per_query, before=before,
                     cache_dir=cfg.cache_dir, log=log)
    candidates = dedupe_candidates(raw)
    if not cfg.before:
        before = infer_cutoff(candidates, self_title=title, self_arxiv_id=self_arxiv) or before
    if before:
        how = "--before" if cfg.before else "the paper's own publication date"
        log(f"  Cutoff: ignoring work published after {before} ({how})")
    else:
        log("  Warning: no publication date known for this paper, so later work is NOT "
            "excluded. Pass --before YYYY-MM-DD (e.g. the submission date).")
    report.config["effective_before"] = before

    # 3. Embed + optional persistent corpus
    embedder = get_embedder(cfg.embedder, cache_dir=cfg.cache_dir)
    log(f"  Embedder: {embedder.name}")
    corpus = CorpusStore(cfg.corpus_dir, embedder.name) if cfg.corpus_dir else None
    if corpus:
        for p in corpus.papers.values():
            candidates.append(p)
        candidates = dedupe_candidates(candidates)

    kept, dropped = filter_candidates(candidates, self_title=title,
                                      self_arxiv_id=self_arxiv, before=before)
    log(f"  {len(raw)} hits -> {len(candidates)} unique papers -> {len(kept)} usable "
        f"({len(dropped)} dropped: self-match, post-dated, or no abstract)")
    papers = {p.paper_id: p for p in kept}
    report.candidates = kept

    def build_chunks() -> list[Chunk]:
        out: list[Chunk] = []
        for p in kept:
            out.extend(candidate_chunks(p, cfg.chunk_tokens))
        return out

    chunks = build_chunks()
    if not chunks:
        report.score_basis = "no prior work retrieved"
        log("  No prior work retrieved -- check network access and --sources.")
        return report

    query_vecs = embedder.embed([c.text for c in claims], kind="query")

    def make_retriever(chs: list[Chunk]) -> HybridRetriever:
        if corpus:
            corpus.add(kept, chs, embedder)
            allowed = set(papers)
            mask = [i for i, c in enumerate(corpus.chunks) if c.doc_id in allowed]
            return HybridRetriever([corpus.chunks[i] for i in mask], corpus.vectors[mask], cfg)
        return HybridRetriever(chs, embedder.embed([c.text for c in chs], kind="passage"), cfg)

    retriever = make_retriever(chunks)

    # 4. Optional full text for the most relevant arXiv papers, then re-index
    if cfg.full_text > 0:
        prelim = [ClaimAssessment(claim=c, hits=retriever.search(c.text, v)[0])
                  for c, v in zip(claims, query_vecs)]
        top = [r["paper_id"] for r in _aggregate_papers(prelim, papers, limit=cfg.full_text * 2)]
        fetched = 0
        for pid in top:
            p = papers[pid]
            if p.arxiv_id and not p.full_text and fetched < cfg.full_text:
                p.full_text = _fetch_full_text(p)
                fetched += bool(p.full_text)
        if fetched:
            chunks = build_chunks()
            retriever = make_retriever(chunks)
    log(f"  Index: {len(retriever.chunks)} chunks, BM25 + {retriever.index.backend} "
        f"(RRF k={cfg.rrf_k})")
    if corpus:
        corpus.save()

    # 5. Retrieve evidence per claim
    for claim, qv in zip(claims, query_vecs):
        hits, z = retriever.search(claim.text, qv)
        report.claims.append(ClaimAssessment(
            claim=claim, hits=hits, similarity_z=z,
            max_similarity=max((h.dense_score for h in hits if h.dense_score is not None),
                               default=None)))

    # 6. Judge
    if cfg.judge:
        log(f"  Judging {len(report.claims)} claims with {cfg.model}...")
        for ca in report.claims:
            usage = judge_claim(ca, papers, cfg)
            report.total_prompt_tokens += usage["prompt_tokens"]
            report.total_completion_tokens += usage["completion_tokens"]

    # 7. Score
    judged = [ca for ca in report.claims if ca.verdict in VERDICT_WEIGHT]
    if judged:
        report.novelty_score = sum(VERDICT_WEIGHT[c.verdict] for c in judged) / len(judged)
        report.score_basis = (f"llm_judge: mean over {len(judged)} claims of "
                              "novel=1, partial=0.5, anticipated=0")
    else:
        sims = [c.max_similarity for c in report.claims if c.max_similarity is not None]
        if sims:
            report.novelty_score = float(np.clip(1.0 - np.mean(sims), 0.0, 1.0))
            report.score_basis = (f"retrieval_only: 1 - mean max cosine ({embedder.name}); "
                                  "uncalibrated, compare only across runs with the same embedder")
    report.related_papers = _aggregate_papers(report.claims, papers)
    return report


# ---------------------------------------------------------------------------
# Markdown rendering
# ---------------------------------------------------------------------------

def render_markdown(report: NoveltyReport) -> str:
    lines = [f"# Novelty report: {report.title}", ""]
    if report.novelty_score is not None:
        lines += [f"**Novelty score:** {report.novelty_score:.2f}  ", f"_{report.score_basis}_", ""]
    cutoff = report.config.get("effective_before")
    lines += [f"Prior work considered: published on or before **{cutoff}**." if cutoff else
              "⚠️ No cutoff date: work published *after* this paper may appear below "
              "(pass `--before`).", ""]
    verdicts = defaultdict(int)
    for c in report.claims:
        verdicts[c.verdict or "unjudged"] += 1
    lines += ["| verdict | claims |", "|---|---|"] + [f"| {k} | {v} |" for k, v in verdicts.items()]
    lines += ["", "## Closest prior work", "", "| # | paper | year | claims matched | max cos |",
              "|---|---|---|---|---|"]
    for i, r in enumerate(report.related_papers[:10], 1):
        t = f"[{r['title']}]({r['url']})" if r["url"] else r["title"]
        lines.append(f"| {i} | {t} | {r['year'] or ''} | {r['claims_matched']} | {r['max_similarity']:.3f} |")
    lines += ["", "## Claims", ""]
    order = {"anticipated": 0, "partial": 1, "novel": 2, None: 3}
    papers = {p.paper_id: p for p in report.candidates}
    for c in sorted(report.claims, key=lambda c: order.get(c.verdict, 3)):
        tag = (c.verdict or "unjudged").upper()
        sim = f"max cos {c.max_similarity:.3f}" if c.max_similarity is not None else ""
        lines += [f"### [{tag}] {c.claim.section or 'Claim'} ({sim})", "",
                  "> " + c.claim.text.split("\n", 1)[-1], ""]
        if c.explanation:
            lines += [c.explanation, ""]
        if c.key_difference:
            lines += [f"**What is new:** {c.key_difference}", ""]
        for h in c.hits[:3]:
            p = papers.get(h.chunk.doc_id)
            name = f"{p.title} ({p.year})" if p else h.chunk.doc_id
            star = " ⟵ cited by judge" if h.chunk.chunk_id == c.evidence_chunk_id else ""
            snippet = h.chunk.text.split("\n", 1)[-1][:280]
            lines.append(f"- **{name}**{star} — cos {h.dense_score:.3f}, "
                         f"bm25 rank {h.bm25_rank or '–'}, dense rank {h.dense_rank or '–'}  \n  {snippet}…")
        lines.append("")
    lines += ["## Search queries", ""] + [f"- `{q}`" for q in report.queries]
    return "\n".join(lines) + "\n"
