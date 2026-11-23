"""Okapi BM25 over an inverted index (pure Python, no dependencies).

Why BM25 alongside embeddings: dense retrievers are good at paraphrase but
weak on exact, rare tokens -- method names ("FlashAttention"), dataset names,
symbols, and specific numbers -- which are exactly the tokens that reveal
"this was already done". BM25 catches those; the two are fused with RRF.

Scoring (Robertson & Zaragoza, 2009) with the Lucene IDF variant, which is
always non-negative:

    idf(t)     = ln(1 + (N - df + 0.5) / (df + 0.5))
    score(d,q) = sum_t idf(t) * tf * (k1 + 1) / (tf + k1 * (1 - b + b * |d| / avgdl))
"""

from __future__ import annotations

import heapq
import math
import re
from collections import Counter, defaultdict

STOPWORDS = frozenset("""
a about above after again against all also am an and any are as at be because been
before being below between both but by can could did do does doing down during each
few for from further had has have having he her here hers herself him himself his how
i if in into is it its itself just me more most my myself no nor not now of off on
once only or other our ours ourselves out over own same she should so some such than
that the their theirs them themselves then there these they this those through to too
under until up very was we were what when where which while who whom why will with
would you your yours yourself yourselves via using use used based paper work show
shows shown propose proposed approach method methods new novel result results however
thus therefore hence moreover furthermore et al fig figure table section eq
""".split())

_TOKEN = re.compile(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*")


def _stem(tok: str) -> str:
    """Very light, conservative plural stripping (no Porter: it mangles jargon)."""
    if len(tok) > 4 and tok.endswith("ies"):
        return tok[:-3] + "y"
    if len(tok) > 3 and tok.endswith("s") and not tok.endswith(("ss", "us", "is")):
        return tok[:-1]
    return tok


def tokenize(text: str) -> list[str]:
    """Lowercase, keep hyphenated/dotted compounds *and* their parts.

    "graph-based GNN" -> ["graph-based", "graph", "based", "gnn"]
    so that both the exact compound and its components can match.
    """
    out: list[str] = []
    for raw in _TOKEN.findall(text.lower()):
        parts = re.split(r"[-_.]", raw)
        if len(parts) > 1 and raw not in STOPWORDS:
            out.append(raw)
        for p in parts:
            if len(p) < 2 or p in STOPWORDS:
                continue
            out.append(_stem(p))
    return out


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.2, b: float = 0.75):
        self.k1, self.b = k1, b
        self.n_docs = len(docs)
        self.doc_len = [len(d) for d in docs]
        self.avgdl = (sum(self.doc_len) / self.n_docs) if self.n_docs else 0.0
        self.postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        for i, doc in enumerate(docs):
            for term, tf in Counter(doc).items():
                self.postings[term].append((i, tf))
        self.idf = {
            t: math.log(1.0 + (self.n_docs - len(p) + 0.5) / (len(p) + 0.5))
            for t, p in self.postings.items()
        }

    @classmethod
    def from_texts(cls, texts: list[str], **kw) -> "BM25":
        return cls([tokenize(t) for t in texts], **kw)

    def scores(self, query_tokens: list[str]) -> dict[int, float]:
        """Sparse scores: only documents sharing at least one query term."""
        acc: dict[int, float] = defaultdict(float)
        if not self.n_docs or not self.avgdl:
            return acc
        k1, b, avgdl = self.k1, self.b, self.avgdl
        for term, qtf in Counter(query_tokens).items():
            idf = self.idf.get(term)
            if idf is None:
                continue
            for doc_id, tf in self.postings[term]:
                norm = k1 * (1.0 - b + b * self.doc_len[doc_id] / avgdl)
                acc[doc_id] += qtf * idf * tf * (k1 + 1.0) / (tf + norm)
        return acc

    def top_k(self, query: str | list[str], k: int = 10) -> list[tuple[int, float]]:
        toks = tokenize(query) if isinstance(query, str) else query
        sc = self.scores(toks)
        return heapq.nlargest(k, sc.items(), key=lambda kv: kv[1])
