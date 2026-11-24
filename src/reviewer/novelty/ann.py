"""Vector indexes: exact (NumPy) and approximate nearest neighbour (HNSW).

HNSW (Malkov & Yashunin, 2018) builds a layered proximity graph and answers
top-k queries in roughly O(log N) distance computations, at the cost of
being *approximate* (recall@k < 1, tunable with ``ef_search``).

When does ANN actually matter here?
  A single run retrieves a few hundred candidate papers -> a few thousand
  chunks. At that size brute-force matmul is exact and takes well under a
  millisecond per query, so ``--ann auto`` uses the exact index below
  ``exact_threshold`` vectors. ANN pays off with ``--corpus-dir``, where
  candidate chunks accumulate across runs into a persistent local library
  (10^5-10^7 chunks for a subfield). Both paths share one interface, and
  the test suite checks HNSW recall@10 against the exact index.

Backends: ``faiss`` (``faiss-cpu``, IndexHNSWFlat) or ``hnswlib``; both use
the inner-product metric on L2-normalised vectors (== cosine).
"""

from __future__ import annotations

import sys

import numpy as np


class VectorIndex:
    backend = "base"

    def search(self, queries: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
        """Return ``(ids, scores)``, each shaped ``(n_queries, k')``, best first.
        Missing slots (k > N) are dropped, so ``k' = min(k, N)``."""
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class ExactIndex(VectorIndex):
    backend = "exact"

    def __init__(self, vectors: np.ndarray):
        self.vectors = np.ascontiguousarray(vectors, dtype=np.float32)

    def __len__(self) -> int:
        return self.vectors.shape[0]

    def search(self, queries, k):
        queries = np.atleast_2d(np.asarray(queries, dtype=np.float32))
        n = len(self)
        k = min(k, n)
        if k == 0:
            return (np.zeros((len(queries), 0), dtype=np.int64),
                    np.zeros((len(queries), 0), dtype=np.float32))
        sims = queries @ self.vectors.T
        part = np.argpartition(-sims, k - 1, axis=1)[:, :k]
        part_scores = np.take_along_axis(sims, part, axis=1)
        order = np.argsort(-part_scores, axis=1, kind="stable")
        ids = np.take_along_axis(part, order, axis=1)
        return ids.astype(np.int64), np.take_along_axis(part_scores, order, axis=1)


class HNSWLibIndex(VectorIndex):
    backend = "hnswlib"

    def __init__(self, vectors: np.ndarray, m: int = 32, ef_construction: int = 200,
                 ef_search: int = 128, seed: int = 0):
        import hnswlib

        vectors = np.ascontiguousarray(vectors, dtype=np.float32)
        n, dim = vectors.shape
        self._n = n
        self._index = hnswlib.Index(space="ip", dim=dim)
        self._index.init_index(max_elements=max(n, 1), M=m,
                               ef_construction=ef_construction, random_seed=seed)
        if n:
            self._index.add_items(vectors, np.arange(n))
        self.ef_search = ef_search

    def __len__(self) -> int:
        return self._n

    def search(self, queries, k):
        queries = np.atleast_2d(np.asarray(queries, dtype=np.float32))
        k = min(k, self._n)
        if k == 0:
            return (np.zeros((len(queries), 0), dtype=np.int64),
                    np.zeros((len(queries), 0), dtype=np.float32))
        self._index.set_ef(max(self.ef_search, k))
        labels, dists = self._index.knn_query(queries, k=k)
        return labels.astype(np.int64), (1.0 - dists).astype(np.float32)  # ip dist = 1 - <q,v>


class FaissHNSWIndex(VectorIndex):
    backend = "faiss"

    def __init__(self, vectors: np.ndarray, m: int = 32, ef_construction: int = 200,
                 ef_search: int = 128):
        import faiss

        vectors = np.ascontiguousarray(vectors, dtype=np.float32)
        self._n, dim = vectors.shape
        self._index = faiss.IndexHNSWFlat(dim, m, faiss.METRIC_INNER_PRODUCT)
        self._index.hnsw.efConstruction = ef_construction
        if self._n:
            self._index.add(vectors)
        self.ef_search = ef_search

    def __len__(self) -> int:
        return self._n

    def search(self, queries, k):
        queries = np.atleast_2d(np.asarray(queries, dtype=np.float32))
        k = min(k, self._n)
        if k == 0:
            return (np.zeros((len(queries), 0), dtype=np.int64),
                    np.zeros((len(queries), 0), dtype=np.float32))
        self._index.hnsw.efSearch = max(self.ef_search, k)
        scores, ids = self._index.search(queries, k)
        return ids.astype(np.int64), scores.astype(np.float32)


def _try(cls, vectors, **kw):
    try:
        return cls(vectors, **kw)
    except ImportError:
        return None


def build_index(vectors: np.ndarray, backend: str = "auto",
                exact_threshold: int = 5000, **kw) -> VectorIndex:
    """Build a vector index.

    backend: ``auto`` | ``exact`` | ``hnsw`` (faiss, else hnswlib) | ``faiss`` | ``hnswlib``
    """
    n = int(vectors.shape[0])
    if backend == "exact" or (backend == "auto" and n < exact_threshold):
        return ExactIndex(vectors)
    order = {
        "auto": (FaissHNSWIndex, HNSWLibIndex),
        "hnsw": (FaissHNSWIndex, HNSWLibIndex),
        "faiss": (FaissHNSWIndex,),
        "hnswlib": (HNSWLibIndex,),
    }.get(backend)
    if order is None:
        raise ValueError(f"Unknown ANN backend: {backend!r}")
    for cls in order:
        idx = _try(cls, vectors, **kw)
        if idx is not None:
            return idx
    print(f"  Warning: ANN backend '{backend}' not installed "
          "(pip install 'openaireview[novelty]'); using exact search.", file=sys.stderr)
    return ExactIndex(vectors)
