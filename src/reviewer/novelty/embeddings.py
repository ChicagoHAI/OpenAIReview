"""Embedding backends.

All embedders return L2-normalised ``float32`` arrays, so inner product ==
cosine similarity everywhere downstream (and the ANN index can use the
inner-product metric).

Backends (selected with ``--embedder``):

* ``st:<model>`` -- local sentence-transformers model
  (``pip install "openaireview[novelty-local]"``). Default model
  ``BAAI/bge-small-en-v1.5``: small (33M params), CPU-friendly, strong on
  BEIR's SciFact/SCIDOCS splits. Scientific-specific alternatives:
  ``allenai-specter`` (paper-level citation-trained) or ``intfloat/e5-base-v2``.
* ``openai:<model>`` -- OpenAI-compatible embeddings endpoint, using the
  existing ``OPENAI_API_KEY`` / ``OPENAI_BASE_URL``. Default
  ``text-embedding-3-small``.
* ``hashing`` -- dependency-free signed feature hashing of uni/bigrams.
  Not semantic; used for tests/offline runs and as a last-resort fallback.
* ``auto`` -- sentence-transformers if installed, else OpenAI if a key is set,
  else hashing (with a warning).

``CachedEmbedder`` wraps any backend with a SQLite cache keyed on
(model, kind, sha256(text)), so re-running on the same paper -- or on a
growing local corpus -- never re-embeds text it has already seen.
"""

from __future__ import annotations

import hashlib
import math
import os
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

import numpy as np

# Asymmetric retrieval models expect different prefixes for queries and passages.
_QUERY_PREFIX = {
    "bge": "Represent this sentence for searching relevant passages: ",
    "e5": "query: ",
}
_PASSAGE_PREFIX = {"e5": "passage: "}


def _family(model: str) -> str:
    m = model.lower()
    if "bge" in m and "m3" not in m:
        return "bge"
    if "e5" in m:
        return "e5"
    return ""


def l2_normalize(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        x = x[None, :]
    norms = np.linalg.norm(x, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return x / norms


class Embedder:
    name: str = "base"
    dim: int = 0

    def embed(self, texts: list[str], kind: str = "passage") -> np.ndarray:
        raise NotImplementedError


class HashingEmbedder(Embedder):
    """Signed feature hashing (Weinberger et al., 2009) of word uni/bigrams."""

    def __init__(self, dim: int = 1024):
        self.dim = dim
        self.name = f"hashing-{dim}"

    def _vec(self, text: str) -> np.ndarray:
        words = re.findall(r"[a-z0-9]+", text.lower())
        feats = Counter(words + [f"{a}_{b}" for a, b in zip(words, words[1:])])
        v = np.zeros(self.dim, dtype=np.float32)
        for f, c in feats.items():
            h = int.from_bytes(hashlib.blake2b(f.encode(), digest_size=8).digest(), "little")
            v[h % self.dim] += (1.0 if (h >> 63) & 1 else -1.0) * (1.0 + math.log(c))
        return v

    def embed(self, texts: list[str], kind: str = "passage") -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return l2_normalize(np.stack([self._vec(t) for t in texts]))


class SentenceTransformerEmbedder(Embedder):
    def __init__(self, model: str = "BAAI/bge-small-en-v1.5", batch_size: int = 32,
                 device: str | None = None):
        from sentence_transformers import SentenceTransformer

        self.model_name = model
        self.name = f"st:{model}"
        self.batch_size = batch_size
        self._model = SentenceTransformer(model, device=device)
        self.dim = int(self._model.get_sentence_embedding_dimension())
        self._family = _family(model)

    def embed(self, texts: list[str], kind: str = "passage") -> np.ndarray:
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        prefix = (_QUERY_PREFIX if kind == "query" else _PASSAGE_PREFIX).get(self._family, "")
        vecs = self._model.encode(
            [prefix + t for t in texts], batch_size=self.batch_size,
            normalize_embeddings=True, show_progress_bar=False, convert_to_numpy=True,
        )
        return l2_normalize(vecs)


class OpenAIEmbedder(Embedder):
    def __init__(self, model: str = "text-embedding-3-small", batch_size: int = 128):
        from openai import OpenAI

        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is required for the openai embedder")
        kwargs = {"api_key": key}
        if os.environ.get("OPENAI_BASE_URL"):
            kwargs["base_url"] = os.environ["OPENAI_BASE_URL"]
        self._client = OpenAI(**kwargs)
        self.model_name = model
        self.name = f"openai:{model}"
        self.batch_size = batch_size
        self.dim = 0  # learned on first call

    def embed(self, texts: list[str], kind: str = "passage") -> np.ndarray:
        out: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = [t[:8000] for t in texts[i:i + self.batch_size]]
            resp = self._client.embeddings.create(model=self.model_name, input=batch)
            out.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
        if not out:
            return np.zeros((0, self.dim), dtype=np.float32)
        arr = l2_normalize(np.asarray(out, dtype=np.float32))
        self.dim = arr.shape[1]
        return arr


class CachedEmbedder(Embedder):
    def __init__(self, inner: Embedder, cache_dir: str | Path):
        self.inner = inner
        self.name = inner.name
        path = Path(cache_dir).expanduser()
        path.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(str(path / "embeddings.sqlite"))
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS emb (key TEXT PRIMARY KEY, dim INTEGER, vec BLOB)"
        )

    @property
    def dim(self) -> int:  # type: ignore[override]
        return self.inner.dim

    def _key(self, text: str, kind: str) -> str:
        return hashlib.sha256(f"{self.name}\x00{kind}\x00{text}".encode()).hexdigest()

    def embed(self, texts: list[str], kind: str = "passage") -> np.ndarray:
        keys = [self._key(t, kind) for t in texts]
        found: dict[str, np.ndarray] = {}
        for i in range(0, len(keys), 500):
            batch = keys[i:i + 500]
            q = f"SELECT key, vec FROM emb WHERE key IN ({','.join('?' * len(batch))})"
            for k, blob in self._db.execute(q, batch):
                found[k] = np.frombuffer(blob, dtype=np.float32)
        missing = [i for i, k in enumerate(keys) if k not in found]
        if missing:
            new = self.inner.embed([texts[i] for i in missing], kind=kind)
            rows = []
            for i, v in zip(missing, new):
                found[keys[i]] = v
                rows.append((keys[i], int(v.shape[0]), v.astype(np.float32).tobytes()))
            self._db.executemany("INSERT OR REPLACE INTO emb VALUES (?, ?, ?)", rows)
            self._db.commit()
        if not texts:
            return np.zeros((0, self.dim), dtype=np.float32)
        return np.stack([found[k] for k in keys]).astype(np.float32)


def get_embedder(spec: str = "auto", cache_dir: str | Path | None = None) -> Embedder:
    spec = (spec or "auto").strip()
    emb: Embedder
    if spec == "hashing":
        emb = HashingEmbedder()
    elif spec.startswith("st:") or spec == "st":
        emb = SentenceTransformerEmbedder(spec[3:] or "BAAI/bge-small-en-v1.5")
    elif spec.startswith("openai:") or spec == "openai":
        emb = OpenAIEmbedder(spec[7:] or "text-embedding-3-small")
    elif spec == "auto":
        try:
            emb = SentenceTransformerEmbedder()
        except ImportError:
            if os.environ.get("OPENAI_API_KEY"):
                emb = OpenAIEmbedder()
            else:
                print("  Warning: no semantic embedder available (install "
                      "'openaireview[novelty-local]' or set OPENAI_API_KEY); "
                      "falling back to lexical hashing embeddings.", file=sys.stderr)
                emb = HashingEmbedder()
    else:
        raise ValueError(f"Unknown embedder spec: {spec!r} "
                         "(use auto, hashing, st:<model>, openai:<model>)")
    if cache_dir and not isinstance(emb, HashingEmbedder):
        emb = CachedEmbedder(emb, cache_dir)
    return emb
