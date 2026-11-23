"""Unit tests for reviewer.novelty (offline: no network, no API keys, no model downloads)."""

import json

import pytest

np = pytest.importorskip("numpy")

from reviewer.novelty import pipeline as pl
from reviewer.novelty.ann import ExactIndex, build_index
from reviewer.novelty.bm25 import BM25, tokenize
from reviewer.novelty.chunking import (
    chunk_document, extract_claims, find_abstract, split_sections, split_sentences,
)
from reviewer.novelty.embeddings import CachedEmbedder, HashingEmbedder, get_embedder
from reviewer.novelty.fusion import reciprocal_rank_fusion
from reviewer.novelty.sources import (
    ArxivSource, OpenAlexSource, SemanticScholarSource, dedupe_candidates,
    filter_candidates, reconstruct_inverted_abstract,
)
from reviewer.novelty.types import CandidatePaper, Chunk

PAPER = """# Sparse Routing for Efficient Transformers

## Abstract

We propose RouteFormer, a transformer in which a learned router sends each token \
to a small subset of expert feed-forward layers. This reduces inference compute by 3x \
while matching dense quality on language modeling benchmarks.

## 1 Introduction

Large language models are expensive to serve. Prior work has studied pruning and \
distillation. In this paper, we introduce a token-level learned router that selects \
two experts per token. To the best of our knowledge, we are the first to combine \
routing with dynamic depth. Fig. 1 shows the architecture, e.g. the router and experts.

## 2 Method

The router is a linear layer followed by a softmax over experts. We train it with \
an auxiliary load-balancing loss. $x_i = W h_i$ is the routing logit.

## References

[1] Shazeer et al. Outrageously large neural networks. 2017.
"""


# ── chunking ───────────────────────────────────────────────────────────────

def test_split_sections_and_skip_references():
    heads = [h for h, _ in split_sections(PAPER)]
    assert "Abstract" in heads and "References" in heads
    chunks = chunk_document(PAPER, "doc", title="T", max_tokens=60)
    assert chunks, "expected chunks"
    assert all("Shazeer" not in c.text for c in chunks), "references must be skipped"
    assert all(c.text.startswith("T | ") for c in chunks), "contextual header expected"


def test_sentence_splitter_respects_abbreviations_and_math():
    s = split_sentences("See Fig. 1 for details, e.g. the router. Next sentence $a. B$ here. Done.")
    assert s[0].startswith("See Fig. 1") and s[0].endswith("router.")
    assert any("$a. B$" in x for x in s)


def test_chunk_budget_and_overlap():
    text = "## S\n\n" + " ".join(f"Sentence number {i} talks about topic {i}." for i in range(60))
    chunks = chunk_document(text, "d", max_tokens=40, overlap_sentences=1)
    assert len(chunks) > 3
    # consecutive chunks share the overlap sentence
    last_sent = chunks[0].text.rsplit("Sentence", 1)[-1]
    assert last_sent in chunks[1].text
    # no text lost: every sentence appears somewhere
    joined = " ".join(c.text for c in chunks)
    assert all(f"number {i} " in joined for i in range(60))


def test_extract_claims_abstract_first_and_cues():
    claims = extract_claims(PAPER, title="Sparse Routing")
    assert claims[0].kind == "abstract"
    assert "RouteFormer" in claims[0].text
    texts = " ".join(c.text for c in claims[1:])
    assert "first to combine routing with dynamic depth" in texts
    assert "linear layer followed by a softmax" not in texts  # not a claim


def test_find_abstract_latex():
    assert find_abstract(r"\begin{abstract} Hello world. \end{abstract}") == "Hello world."


# ── BM25 / fusion ──────────────────────────────────────────────────────────

def test_tokenize_keeps_compounds_and_parts():
    toks = tokenize("Graph-based GNNs use mixture-of-experts")
    assert "graph-based" in toks and "graph" in toks and "gnn" in toks
    assert "mixture-of-expert" in toks or "mixture-of-experts" in toks


def test_bm25_ranks_rare_term_match_first():
    docs = ["the cat sat on the mat", "dogs and cats are pets",
            "FlashAttention is an IO-aware exact attention algorithm",
            "attention is all you need"]
    bm = BM25.from_texts(docs)
    top = bm.top_k("FlashAttention exact attention", 2)
    assert top[0][0] == 2
    assert all(v >= 0 for v in bm.idf.values())
    assert bm.top_k("zzz", 3) == []


def test_rrf():
    fused = reciprocal_rank_fusion([[1, 2, 3], [3, 1, 4]], k=60)
    ids = [d for d, _ in fused]
    assert ids[0] == 1  # ranks 1 and 2 beats ranks 3 and 1
    assert set(ids) == {1, 2, 3, 4}
    with pytest.raises(ValueError):
        reciprocal_rank_fusion([[1]], weights=[1, 2])


# ── embeddings / ANN ───────────────────────────────────────────────────────

def test_hashing_embedder_normalised_and_semantic_ish():
    e = HashingEmbedder(dim=512)
    v = e.embed(["learned token router experts", "token router with learned experts",
                 "protein folding with diffusion"])
    assert np.allclose(np.linalg.norm(v, axis=1), 1.0, atol=1e-5)
    assert v[0] @ v[1] > v[0] @ v[2]
    assert np.array_equal(v, e.embed(["learned token router experts", "token router with learned experts",
                                       "protein folding with diffusion"]))


def test_cached_embedder_avoids_recompute(tmp_path):
    calls = []

    class Counting(HashingEmbedder):
        name = "counting"

        def embed(self, texts, kind="passage"):
            calls.append(len(texts))
            return super().embed(texts, kind)

    c = CachedEmbedder(Counting(64), tmp_path)
    a = c.embed(["x y", "z w"])
    b = c.embed(["z w", "x y", "new one"])
    assert calls == [2, 1]
    assert np.allclose(a[0], b[1])


def test_get_embedder_rejects_unknown():
    with pytest.raises(ValueError):
        get_embedder("nope")


def test_exact_index_matches_bruteforce():
    rng = np.random.default_rng(0)
    x = rng.normal(size=(300, 32)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    q = x[:5] + 0.01
    ids, scores = ExactIndex(x).search(q, 10)
    ref = np.argsort(-(q @ x.T), axis=1)[:, :10]
    assert np.array_equal(ids, ref)
    assert np.all(np.diff(scores, axis=1) <= 1e-6)
    assert ExactIndex(x).search(q, 1000)[0].shape == (5, 300)


@pytest.mark.parametrize("backend", ["hnswlib", "faiss"])
def test_hnsw_recall_vs_exact(backend):
    pytest.importorskip(backend if backend != "faiss" else "faiss")
    rng = np.random.default_rng(1)
    x = rng.normal(size=(4000, 64)).astype(np.float32)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    q = rng.normal(size=(50, 64)).astype(np.float32)
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    exact_ids, _ = ExactIndex(x).search(q, 10)
    idx = build_index(x, backend=backend)
    assert idx.backend == backend
    ann_ids, ann_scores = idx.search(q, 10)
    recall = np.mean([len(set(a) & set(e)) / 10 for a, e in zip(ann_ids, exact_ids)])
    assert recall >= 0.9, recall
    np.testing.assert_allclose(ann_scores[:, 0], (q * x[ann_ids[:, 0]]).sum(1), atol=1e-4)


def test_build_index_auto_uses_exact_for_small():
    x = np.eye(10, dtype=np.float32)
    assert build_index(x, "auto").backend == "exact"


# ── sources ────────────────────────────────────────────────────────────────

ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/1701.06538v1</id>
    <published>2017-01-23T00:00:00Z</published>
    <title>Outrageously Large Neural Networks: The Sparsely-Gated
      Mixture-of-Experts Layer</title>
    <summary>  We introduce a Sparsely-Gated Mixture-of-Experts layer with a trainable gating network. </summary>
    <author><name>Noam Shazeer</name></author>
    <arxiv:doi>10.1000/XYZ</arxiv:doi>
  </entry>
</feed>"""


def test_arxiv_parse():
    [p] = ArxivSource.parse(ARXIV_XML)
    assert p.paper_id == "arxiv:1701.06538"
    assert p.title.startswith("Outrageously Large") and "\n" not in p.title
    assert p.year == 2017 and p.authors == ["Noam Shazeer"] and p.doi == "10.1000/xyz"


def test_semantic_scholar_and_openalex_parse():
    s2 = json.dumps({"data": [{"paperId": "abc", "title": "Switch Transformers",
                               "abstract": "Simplified MoE routing.", "year": 2021,
                               "externalIds": {"ArXiv": "2101.03961"}, "authors": [{"name": "W. Fedus"}]}]})
    [p] = SemanticScholarSource.parse(s2)
    assert p.paper_id == "arxiv:2101.03961" and p.sources == ["semantic_scholar"]

    oa = json.dumps({"results": [{"id": "https://openalex.org/W1", "title": "GShard",
                                  "doi": "https://doi.org/10.5/G", "publication_year": 2020,
                                  "abstract_inverted_index": {"Scaling": [0], "with": [1], "MoE": [2]},
                                  "authorships": [], "primary_location": {"landing_page_url": "https://x.org"}}]})
    [q] = OpenAlexSource.parse(oa)
    assert q.abstract == "Scaling with MoE" and q.paper_id == "doi:10.5/g"


def test_reconstruct_inverted_abstract_empty():
    assert reconstruct_inverted_abstract(None) == ""


def test_dedupe_merges_across_sources():
    a = CandidatePaper("arxiv:2101.03961", "Switch Transformers: Scaling to Trillion Parameter Models",
                       abstract="short", arxiv_id="2101.03961", sources=["arxiv"])
    b = CandidatePaper("doi:10.1/x", "Switch transformers - scaling to trillion parameter models",
                       abstract="a much longer abstract text", doi="10.1/x", sources=["openalex"])
    c = CandidatePaper("s2:1", "Unrelated", abstract="z", sources=["semantic_scholar"])
    out = dedupe_candidates([a, b, c])
    assert len(out) == 2
    assert out[0].abstract == "a much longer abstract text"
    assert set(out[0].sources) == {"arxiv", "openalex"} and out[0].paper_id.startswith("arxiv:")


def test_filter_drops_self_and_postdated():
    me = CandidatePaper("arxiv:2601.00001", "Sparse Routing for Efficient Transformers",
                        abstract="x", arxiv_id="2601.00001", published="2026-01-02")
    late = CandidatePaper("s2:2", "Later work", abstract="x", published="2026-06-01")
    ok = CandidatePaper("s2:3", "Older work", abstract="x", published="2020-01-01")
    empty = CandidatePaper("s2:4", "No abstract", published="2019-01-01")
    kept, dropped = filter_candidates([me, late, ok, empty],
                                      self_title="Sparse routing for efficient transformers",
                                      before="2026-03-01")
    assert [p.paper_id for p in kept] == ["s2:3"]
    assert len(dropped) == 3


# ── pipeline end to end (fake web, hashing embedder, no LLM) ─────────────────

PRIOR = [
    CandidatePaper("arxiv:1701.06538", "Outrageously Large Neural Networks: Sparsely-Gated Mixture-of-Experts",
                   abstract="We introduce a learned router that sends each token to a small subset of "
                            "expert feed-forward layers, reducing compute while matching dense quality.",
                   year=2017, published="2017-01-23", arxiv_id="1701.06538", sources=["arxiv"]),
    CandidatePaper("s2:p", "Protein structure prediction with diffusion",
                   abstract="We fold proteins using a diffusion model over residue coordinates.",
                   year=2023, published="2023-01-01", sources=["semantic_scholar"]),
    CandidatePaper("s2:self", "Sparse Routing for Efficient Transformers",
                   abstract="Self copy of the submission on arXiv.", year=2026, published="2026-01-01",
                   sources=["semantic_scholar"]),
]


@pytest.fixture
def fake_web(monkeypatch):
    seen = {}

    def fake_search_all(queries, sources, per_query=25, before=None, cache_dir=None, log=print):
        seen["queries"] = queries
        return [CandidatePaper(**{**p.__dict__, "sources": list(p.sources)}) for p in PRIOR]

    monkeypatch.setattr(pl, "search_all", fake_search_all)
    return seen


def _cfg(**kw):
    base = dict(embedder="hashing", judge=False, cache_dir=None, sources=["arxiv"])
    base.update(kw)
    return pl.NoveltyConfig(**base)


def test_pipeline_retrieval_only(fake_web):
    rep = pl.run_novelty("Sparse Routing for Efficient Transformers [PDF]", PAPER, "sr", _cfg())
    assert fake_web["queries"][0] == "Sparse Routing for Efficient Transformers"
    ids = {p.paper_id for p in rep.candidates}
    assert "s2:self" not in ids, "the submission itself must be excluded"
    assert rep.related_papers[0]["paper_id"] == "arxiv:1701.06538"
    abstract_claim = rep.claims[0]
    assert abstract_claim.hits[0].chunk.doc_id == "arxiv:1701.06538"
    assert abstract_claim.hits[0].bm25_rank == 1
    assert rep.score_basis.startswith("retrieval_only") and 0 <= rep.novelty_score <= 1
    md = pl.render_markdown(rep)
    assert "Closest prior work" in md and "Outrageously" in md
    json.dumps(rep.to_dict())  # serialisable


def test_pipeline_with_judge(fake_web, monkeypatch):
    calls = []

    def fake_chat(messages, model=None, max_tokens=0, reasoning_effort=None, **kw):
        calls.append(messages[0]["content"])
        verdict = "anticipated" if "RouteFormer" in messages[0]["content"].split("PRIOR WORK")[0] else "novel"
        return json.dumps({"verdict": verdict, "evidence_index": 1,
                           "explanation": "e", "key_difference": "d"}), \
            {"prompt_tokens": 10, "completion_tokens": 5}

    import reviewer.client
    monkeypatch.setattr(reviewer.client, "chat", fake_chat)
    rep = pl.run_novelty("Sparse Routing for Efficient Transformers", PAPER, "sr", _cfg(judge=True))
    assert len(calls) == len(rep.claims)
    assert rep.claims[0].verdict == "anticipated"
    assert rep.claims[0].evidence_chunk_id == rep.claims[0].hits[0].chunk.chunk_id
    assert rep.score_basis.startswith("llm_judge")
    assert rep.total_prompt_tokens == 10 * len(calls)


def test_parse_judge_response_robust():
    assert pl.parse_judge_response("garbage")["verdict"] is None
    r = pl.parse_judge_response('```json\n{"verdict": "Partial", "evidence_index": "2"}\n```')
    assert r["verdict"] == "partial" and r["evidence_index"] == 2


def test_corpus_store_persists_and_grows(fake_web, tmp_path):
    corpus = tmp_path / "corpus"
    pl.run_novelty("Sparse Routing for Efficient Transformers", PAPER, "sr", _cfg(corpus_dir=str(corpus)))
    meta = json.loads((corpus / "meta.json").read_text())
    assert meta["embedder"] == "hashing-1024" and meta["n_chunks"] > 0
    n_vec = np.load(corpus / "vectors.npy").shape[0]
    assert n_vec == meta["n_chunks"]
    store = pl.CorpusStore(corpus, "hashing-1024")
    assert store.vectors is not None and len(store.chunks) == n_vec
    # A second run with the same web results must not duplicate chunks.
    pl.run_novelty("Sparse Routing for Efficient Transformers", PAPER, "sr", _cfg(corpus_dir=str(corpus)))
    assert json.loads((corpus / "meta.json").read_text())["n_chunks"] == meta["n_chunks"]


def test_build_queries_drops_generic_words():
    claims = [Chunk("c", "d", "T | Intro\nWe propose a novel learned token router for sparse experts")]
    qs = pl.build_queries("My Title [PDF]", claims)
    assert qs[0] == "My Title"
    assert "propose" not in qs[1].lower() and "router" in qs[1]
