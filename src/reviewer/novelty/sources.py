"""Candidate prior-work retrieval from public scholarly search APIs.

Only the standard library is used (``urllib`` + ``xml.etree``), matching how
``reviewer.parsers`` already fetches arXiv HTML.

Sources
-------
* ``arxiv``            export.arxiv.org Atom API (no key; ~1 request / 3 s).
* ``semantic_scholar`` Graph API ``/paper/search`` (optional ``S2_API_KEY``
                       raises the rate limit; unauthenticated works but 429s).
* ``openalex``         ``/works?search=`` (no key; ``OPENALEX_MAILTO`` puts
                       you in the polite pool). Abstracts arrive as an
                       inverted index and are reconstructed here.

Every response is cached on disk (JSON, keyed by URL hash) so iterating on
the ranking/judging stages never re-hits the APIs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .bm25 import STOPWORDS
from .types import CandidatePaper

USER_AGENT = "openaireview-novelty/0.1 (+https://github.com/ChicagoHAI/OpenAIReview)"
_ATOM = "{http://www.w3.org/2005/Atom}"
_ARXIV_ID = re.compile(r"(\d{4}\.\d{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/\d{7})(v\d+)?", re.I)


# ---------------------------------------------------------------------------
# HTTP with cache + polite retry
# ---------------------------------------------------------------------------

class HttpClient:
    def __init__(self, cache_dir: str | Path | None = None, min_interval: float = 1.0,
                 timeout: float = 30.0, retries: int = 3):
        self.cache_dir = Path(cache_dir).expanduser() / "http" if cache_dir else None
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.min_interval = min_interval
        self.timeout = timeout
        self.retries = retries
        self._last: dict[str, float] = {}

    def get(self, url: str, headers: dict | None = None, host_interval: float | None = None) -> str:
        cache_file = None
        if self.cache_dir:
            cache_file = self.cache_dir / (hashlib.sha256(url.encode()).hexdigest() + ".txt")
            if cache_file.exists():
                return cache_file.read_text()
        host = url.split("/")[2]
        interval = self.min_interval if host_interval is None else host_interval
        hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
        for attempt in range(self.retries):
            wait = interval - (time.monotonic() - self._last.get(host, 0.0))
            if wait > 0:
                time.sleep(wait)
            self._last[host] = time.monotonic()
            try:
                with urlopen(Request(url, headers=hdrs), timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8", errors="replace")
                if cache_file:
                    cache_file.write_text(body)
                return body
            except HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self.retries - 1:
                    retry_after = e.headers.get("Retry-After") if e.headers else None
                    time.sleep(float(retry_after) if retry_after and retry_after.isdigit()
                               else 2 ** (attempt + 1))
                    continue
                raise
            except URLError:
                if attempt < self.retries - 1:
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise
        raise RuntimeError(f"unreachable: {url}")


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize_title(title: str) -> str:
    t = re.sub(r"\$[^$]*\$", " ", title.lower())
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def title_similarity(a: str, b: str) -> float:
    na, nb = normalize_title(a), normalize_title(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb, autojunk=False).ratio()


def extract_arxiv_id(text: str) -> str:
    m = _ARXIV_ID.search(text or "")
    return m.group(1) if m else ""


def reconstruct_inverted_abstract(inv: dict | None) -> str:
    """OpenAlex ships abstracts as ``{word: [positions]}``."""
    if not inv:
        return ""
    slots: dict[int, str] = {}
    for word, positions in inv.items():
        for p in positions:
            slots[p] = word
    return " ".join(slots[i] for i in sorted(slots))


def _year(date_str: str) -> int | None:
    m = re.match(r"(\d{4})", date_str or "")
    return int(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

class Source:
    name = "base"

    def __init__(self, http: HttpClient):
        self.http = http

    def search(self, query: str, limit: int = 25, before: str | None = None) -> list[CandidatePaper]:
        raise NotImplementedError


class ArxivSource(Source):
    name = "arxiv"
    BASE = "http://export.arxiv.org/api/query"

    def search(self, query, limit=25, before=None):
        terms = [t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]+", query)
                 if t.lower() not in STOPWORDS][:12]
        if not terms:
            return []
        # arXiv's engine is strictly boolean; ANDing more than ~4 terms
        # usually returns nothing, so use the leading (most specific) terms.
        sq = " AND ".join(f"all:{t}" for t in terms[:4])
        if before:
            d = before.replace("-", "")
            sq = f"({sq}) AND submittedDate:[190001010000 TO {d}2359]"
        url = f"{self.BASE}?" + urlencode({
            "search_query": sq, "start": 0, "max_results": limit,
            "sortBy": "relevance", "sortOrder": "descending",
        })
        return self.parse(self.http.get(url, host_interval=3.0))

    @staticmethod
    def parse(xml_text: str) -> list[CandidatePaper]:
        root = ET.fromstring(xml_text)
        out = []
        for e in root.findall(f"{_ATOM}entry"):
            raw_id = (e.findtext(f"{_ATOM}id") or "").strip()
            aid = extract_arxiv_id(raw_id.split("/abs/")[-1])
            title = re.sub(r"\s+", " ", e.findtext(f"{_ATOM}title") or "").strip()
            if not title or not aid:
                continue
            published = (e.findtext(f"{_ATOM}published") or "")[:10]
            doi = ""
            for child in e:
                if child.tag.endswith("doi"):
                    doi = (child.text or "").strip().lower()
            out.append(CandidatePaper(
                paper_id=f"arxiv:{aid}", title=title,
                abstract=re.sub(r"\s+", " ", e.findtext(f"{_ATOM}summary") or "").strip(),
                year=_year(published), published=published,
                url=f"https://arxiv.org/abs/{aid}",
                authors=[(a.findtext(f"{_ATOM}name") or "").strip()
                         for a in e.findall(f"{_ATOM}author")][:20],
                sources=["arxiv"], arxiv_id=aid, doi=doi,
            ))
        return out


class SemanticScholarSource(Source):
    name = "semantic_scholar"
    BASE = "https://api.semanticscholar.org/graph/v1/paper/search"
    FIELDS = "title,abstract,year,publicationDate,externalIds,url,authors"

    def search(self, query, limit=25, before=None):
        params = {"query": query[:300], "limit": min(limit, 100), "fields": self.FIELDS}
        if before:
            params["publicationDateOrYear"] = f":{before}"
        headers = {}
        key = os.environ.get("S2_API_KEY") or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        if key:
            headers["x-api-key"] = key
        body = self.http.get(f"{self.BASE}?{urlencode(params)}", headers=headers,
                             host_interval=1.0 if key else 3.0)
        return self.parse(body)

    @staticmethod
    def parse(body: str) -> list[CandidatePaper]:
        out = []
        for p in json.loads(body).get("data") or []:
            ext = p.get("externalIds") or {}
            aid = ext.get("ArXiv") or ""
            doi = (ext.get("DOI") or "").lower()
            pid = (f"arxiv:{aid}" if aid else f"doi:{doi}" if doi else f"s2:{p.get('paperId')}")
            if not p.get("title"):
                continue
            out.append(CandidatePaper(
                paper_id=pid, title=p["title"].strip(), abstract=(p.get("abstract") or "").strip(),
                year=p.get("year"), published=p.get("publicationDate") or "",
                url=p.get("url") or "", authors=[a.get("name", "") for a in (p.get("authors") or [])][:20],
                sources=["semantic_scholar"], arxiv_id=aid, doi=doi,
            ))
        return out


class OpenAlexSource(Source):
    name = "openalex"
    BASE = "https://api.openalex.org/works"

    def search(self, query, limit=25, before=None):
        params = {"search": query[:300], "per-page": min(limit, 200),
                  "select": "id,doi,title,publication_date,publication_year,"
                            "abstract_inverted_index,authorships,ids,primary_location"}
        if before:
            params["filter"] = f"to_publication_date:{before}"
        mailto = os.environ.get("OPENALEX_MAILTO")
        if mailto:
            params["mailto"] = mailto
        return self.parse(self.http.get(f"{self.BASE}?{urlencode(params, quote_via=quote)}",
                                        host_interval=0.2))

    @staticmethod
    def parse(body: str) -> list[CandidatePaper]:
        out = []
        for w in json.loads(body).get("results") or []:
            title = (w.get("title") or "").strip()
            if not title:
                continue
            doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
            loc = (w.get("primary_location") or {}).get("landing_page_url") or ""
            aid = extract_arxiv_id(loc) if "arxiv.org" in loc else ""
            pid = f"arxiv:{aid}" if aid else f"doi:{doi}" if doi else f"openalex:{w.get('id', '').rsplit('/', 1)[-1]}"
            out.append(CandidatePaper(
                paper_id=pid, title=title,
                abstract=reconstruct_inverted_abstract(w.get("abstract_inverted_index")),
                year=w.get("publication_year"), published=w.get("publication_date") or "",
                url=loc or (f"https://doi.org/{doi}" if doi else w.get("id", "")),
                authors=[(a.get("author") or {}).get("display_name", "")
                         for a in (w.get("authorships") or [])][:20],
                sources=["openalex"], arxiv_id=aid, doi=doi,
            ))
        return out


SOURCES = {cls.name: cls for cls in (ArxivSource, SemanticScholarSource, OpenAlexSource)}


# ---------------------------------------------------------------------------
# Merge / filter
# ---------------------------------------------------------------------------

def dedupe_candidates(papers: list[CandidatePaper], title_threshold: float = 0.93) -> list[CandidatePaper]:
    """Merge the same paper returned by several sources.

    Identity: arXiv id, then DOI, then near-identical normalised title
    (preprint vs. published version usually differ only in punctuation).
    Merged records keep the longest abstract and union of sources.
    """
    merged: list[CandidatePaper] = []
    by_key: dict[str, CandidatePaper] = {}
    by_title: dict[str, CandidatePaper] = {}
    for p in papers:
        keys = [k for k in (f"arxiv:{p.arxiv_id}" if p.arxiv_id else "",
                            f"doi:{p.doi}" if p.doi else "") if k]
        hit = next((by_key[k] for k in keys if k in by_key), None)
        nt = normalize_title(p.title)
        if hit is None and nt:
            hit = by_title.get(nt)
            if hit is None and len(nt) > 20:
                # Fuzzy fallback only against same-prefix titles to stay O(n) in practice.
                for t, cand in by_title.items():
                    if t[:12] == nt[:12] and title_similarity(t, nt) >= title_threshold:
                        hit = cand
                        break
        if hit is None:
            hit = CandidatePaper(**{**p.__dict__, "sources": list(p.sources),
                                    "authors": list(p.authors)})
            merged.append(hit)
        else:
            if len(p.abstract) > len(hit.abstract):
                hit.abstract = p.abstract
            hit.arxiv_id = hit.arxiv_id or p.arxiv_id
            hit.doi = hit.doi or p.doi
            hit.year = hit.year or p.year
            hit.published = hit.published or p.published
            hit.url = hit.url or p.url
            hit.authors = hit.authors or p.authors
            for s in p.sources:
                if s not in hit.sources:
                    hit.sources.append(s)
            if hit.arxiv_id and not hit.paper_id.startswith("arxiv:"):
                hit.paper_id = f"arxiv:{hit.arxiv_id}"
        for k in (f"arxiv:{hit.arxiv_id}" if hit.arxiv_id else "", f"doi:{hit.doi}" if hit.doi else ""):
            if k:
                by_key[k] = hit
        if nt:
            by_title.setdefault(nt, hit)
    return merged


def filter_candidates(
    papers: list[CandidatePaper],
    self_title: str = "",
    self_arxiv_id: str = "",
    before: str | None = None,
    self_title_threshold: float = 0.9,
) -> tuple[list[CandidatePaper], list[CandidatePaper]]:
    """Drop the submission itself (and its other versions) and post-dated work.

    Without this the top hit is almost always the paper under review, which
    is already on arXiv, and every claim looks "anticipated".
    Returns ``(kept, dropped)``.
    """
    kept, dropped = [], []
    for p in papers:
        is_self = (
            (self_arxiv_id and p.arxiv_id == self_arxiv_id)
            or (self_title and title_similarity(self_title, p.title) >= self_title_threshold)
        )
        too_new = bool(before and p.published and p.published[:10] > before)
        if before and not p.published and p.year and p.year > int(before[:4]):
            too_new = True
        (dropped if (is_self or too_new or not p.abstract) else kept).append(p)
    return kept, dropped


def search_all(
    queries: list[str],
    sources: list[str],
    per_query: int = 25,
    before: str | None = None,
    cache_dir: str | Path | None = None,
    log=print,
) -> list[CandidatePaper]:
    http = HttpClient(cache_dir=cache_dir)
    results: list[CandidatePaper] = []
    for name in sources:
        if name not in SOURCES:
            raise ValueError(f"Unknown source {name!r}; choose from {', '.join(SOURCES)}")
        src = SOURCES[name](http)
        n_before = len(results)
        for q in queries:
            try:
                results.extend(src.search(q, limit=per_query, before=before))
            except Exception as e:  # one flaky API must not sink the run
                print(f"  Warning: {name} search failed for {q[:60]!r}: {e}", file=sys.stderr)
        log(f"  {name}: {len(results) - n_before} results")
    return results
