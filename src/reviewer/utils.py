"""Utilities for parsing reviewer output and chunking text."""

import json
import re
from difflib import SequenceMatcher

import tiktoken

from .models import Comment


def _get_encoding():
    """Get a tiktoken encoding for approximate token counting."""
    try:
        return tiktoken.get_encoding("o200k_base")
    except Exception:
        return None


def count_tokens(text: str) -> int:
    enc = _get_encoding()
    if enc is None:
        return len(text) // 4
    return len(enc.encode(text))


def truncate_text(text: str, max_tokens: int) -> str:
    """Truncate text to at most max_tokens tokens."""
    enc = _get_encoding()
    if enc is None:
        return text[: max_tokens * 4]
    tokens = enc.encode(text)[:max_tokens]
    return enc.decode(tokens)


def chunk_text(text: str, max_tokens: int = 6000, overlap_tokens: int = 200) -> list[str]:
    """Split text into chunks of at most max_tokens with overlap."""
    try:
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        chars_per_chunk = max_tokens * 4
        overlap_chars = overlap_tokens * 4
        chunks = []
        i = 0
        while i < len(text):
            chunks.append(text[i : i + chars_per_chunk])
            i += chars_per_chunk - overlap_chars
        return chunks

    tokens = enc.encode(text)
    chunks = []
    i = 0
    while i < len(tokens):
        chunk_tokens = tokens[i : i + max_tokens]
        chunks.append(enc.decode(chunk_tokens))
        i += max_tokens - overlap_tokens
    return chunks


def split_into_paragraphs(text: str, min_chars: int = 100) -> list[str]:
    """Split document into paragraphs, merging short ones with the next."""
    raw = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraphs: list[str] = []
    carry = ""
    for p in raw:
        if carry:
            p = carry + "\n\n" + p
            carry = ""
        if len(p) < min_chars:
            carry = p
        else:
            paragraphs.append(p)
    if carry:
        if paragraphs:
            paragraphs[-1] = paragraphs[-1] + "\n\n" + carry
        else:
            paragraphs.append(carry)
    return paragraphs


def _normalize_for_match(text: str) -> str:
    """Normalize extracted text for quote-to-paragraph matching."""
    text = text.lower()
    text = text.replace("<br>", " ")
    text = text.replace("|", " ")
    text = text.replace("*", "")
    text = text.replace("_", "")
    text = text.replace("\u2019", "'")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _quote_coverage(quote: str, window: str) -> float:
    """Fraction of the quote covered by matching blocks in the window.

    Unlike ``SequenceMatcher.ratio()`` which divides by the combined length
    of both strings, this divides only by the quote length so that extra
    content in the window does not penalise the score.
    """
    if not quote:
        return 0.0
    sm = SequenceMatcher(None, quote, window, autojunk=False)
    matched = sum(block.size for block in sm.get_matching_blocks())
    return matched / len(quote)


def locate_comment_in_document(
    quote: str,
    paragraphs: list[str],
    threshold: float = 0.3,
) -> int | None:
    """Find the paragraph index that best matches a quote.

    Uses fuzzy substring matching. Returns the index of the best-matching
    paragraph, or None if no paragraph scores above *threshold*.
    """
    if not quote or not paragraphs:
        return None

    quote_norm = _normalize_for_match(quote)[:1000]
    best_idx = None
    best_score = 0.0

    for i, para in enumerate(paragraphs):
        para_norm = _normalize_for_match(para)
        # Fast exact-substring check first
        if quote_norm and quote_norm in para_norm:
            return i

        # Compare against sliding windows so long table-like paragraphs still match.
        if len(para_norm) <= len(quote_norm) + 200:
            windows = [para_norm]
        else:
            window_size = min(len(para_norm), max(len(quote_norm) + 200, 400))
            step = max(window_size // 2, 100)
            windows = [
                para_norm[start : start + window_size]
                for start in range(0, len(para_norm) - window_size + 1, step)
            ]
            if (len(para_norm) - window_size) % step:
                windows.append(para_norm[-window_size:])

        score = max(_quote_coverage(quote_norm, window) for window in windows)
        if score > best_score:
            best_score = score
            best_idx = i

    return best_idx if best_score >= threshold else None


def locate_comments_in_window(
    comments: list[Comment],
    chunk_idx: int,
    chunks: list[tuple[list[int], str]],
    paragraphs: list[str],
    window_size: int = 3,
) -> None:
    """Set paragraph_index on each comment by matching within the context window.
    """
    before = window_size + 2
    after = max(1, window_size - 1)
    win_start = max(0, chunk_idx - before)
    win_end = min(len(chunks), chunk_idx + after + 1)
    window_para_indices: list[int] = []
    for wi in range(win_start, win_end):
        window_para_indices.extend(chunks[wi][0])
    window_paras = [paragraphs[i] for i in window_para_indices]
    for c in comments:
        located = locate_comment_in_document(c.quote, window_paras)
        if located is not None and located < len(window_para_indices):
            c.paragraph_index = window_para_indices[located]
        else:
            c.paragraph_index = None


def assign_paragraph_indices(
    comments: list[Comment],
    document_content: str,
) -> None:
    """Set paragraph_index on each comment by locating its quote in the document."""
    paragraphs = split_into_paragraphs(document_content)
    for comment in comments:
        comment.paragraph_index = locate_comment_in_document(
            comment.quote, paragraphs
        )


def parse_comments_from_list(items: list[dict]) -> list[Comment]:
    """Convert a list of raw dicts into Comment objects."""
    comments = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = item.get("title", item.get("name", "Untitled"))
        quote = item.get("quote", item.get("flagged_text", item.get("text", "")))
        explanation = item.get("explanation", item.get("message", item.get("comment", "")))
        comment_type = item.get("type", item.get("comment_type", "logical")).lower()
        if comment_type not in ("technical", "logical"):
            comment_type = "technical" if any(
                kw in (title + explanation).lower()
                for kw in ["formula", "equation", "math", "proof", "calculation",
                           "theorem", "incorrect", "wrong", "error", "sign", "factor",
                           "variance", "derivation", "typo", "parameter"]
            ) else "logical"
        paragraph_index = item.get("paragraph_index", None)
        if paragraph_index is not None:
            paragraph_index = int(paragraph_index)
        comments.append(Comment(
            title=title,
            quote=quote,
            explanation=explanation,
            comment_type=comment_type,
            paragraph_index=paragraph_index,
        ))
    return comments


def _decode_jsonish_string(value: str) -> str:
    """Best-effort decode of a JSON-style string fragment."""
    def _unicode_repl(match):
        try:
            return chr(int(match.group(1), 16))
        except ValueError:
            return match.group(0)

    value = re.sub(r"\\u([0-9a-fA-F]{4})", _unicode_repl, value)
    value = value.replace(r"\/", "/")
    value = value.replace(r"\"",
                          "\"")
    value = value.replace(r"\n", "\n")
    value = value.replace(r"\r", "\r")
    value = value.replace(r"\t", "\t")
    value = value.replace(r"\\", "\\")
    return value


def _extract_overall_feedback_fallback(text: str) -> str:
    """Recover overall_feedback from malformed JSON-ish output."""
    match = re.search(
        r'"overall_feedback"\s*:\s*"(?P<value>.*?)"\s*,\s*"comments"\s*:',
        text,
        re.DOTALL,
    )
    if not match:
        return ""
    return _decode_jsonish_string(match.group("value")).strip()


def _extract_comments_fallback(text: str) -> list[Comment]:
    """Recover comment objects from malformed JSON-ish output.

    This is intentionally schema-specific and only targets the comment shape
    emitted by our prompts: title, quote, explanation, type.
    """
    pattern = re.compile(
        r'\{\s*"title"\s*:\s*"(?P<title>.*?)"\s*,\s*'
        r'"quote"\s*:\s*"(?P<quote>.*?)"\s*,\s*'
        r'"explanation"\s*:\s*"(?P<explanation>.*?)"\s*,\s*'
        r'"type"\s*:\s*"(?P<type>technical|logical)"\s*\}',
        re.DOTALL,
    )
    items = []
    for match in pattern.finditer(text):
        items.append({
            "title": _decode_jsonish_string(match.group("title")).strip(),
            "quote": _decode_jsonish_string(match.group("quote")).strip(),
            "explanation": _decode_jsonish_string(match.group("explanation")).strip(),
            "type": match.group("type").strip(),
        })
    return parse_comments_from_list(items)


def parse_review_response(response: str) -> tuple[str, list[Comment]]:
    """Parse LLM response returning (overall_feedback, comments).

    Handles two formats:
    - {"overall_feedback": "...", "comments": [...]}  (preferred)
    - [...]  (bare array fallback)
    """
    # Try to extract first valid JSON object or array using raw_decode
    text = response.strip()
    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    decoder = json.JSONDecoder()
    obj = None
    # Scan for the first parseable top-level object/array
    for i, ch in enumerate(text):
        if ch in ("{", "["):
            try:
                candidate, _ = decoder.raw_decode(text, i)
            except json.JSONDecodeError:
                continue
            if isinstance(candidate, list):
                if not candidate or isinstance(candidate[0], dict):
                    obj = candidate
                    break
                continue
            if isinstance(candidate, dict) and (
                "overall_feedback" in candidate or "comments" in candidate
            ):
                obj = candidate
                break
    else:
        # Nothing parseable found
        return _extract_overall_feedback_fallback(text), _extract_comments_fallback(text)

    if isinstance(obj, dict):
        overall_feedback = obj.get("overall_feedback", "")
        items = obj.get("comments", [])
        return overall_feedback, parse_comments_from_list(items)
    elif isinstance(obj, list):
        return "", parse_comments_from_list(obj)
    return _extract_overall_feedback_fallback(text), _extract_comments_fallback(text)


def parse_comments_from_response(response: str) -> list[Comment]:
    """Parse a JSON array of comments from an LLM response (legacy wrapper)."""
    _, comments = parse_review_response(response)
    return comments
