"""Shared HTTP helpers for OpenReview (API + PDF) behind Cloudflare.

Visit ``openreview.net`` first so ``api2.openreview.net`` and PDF URLs succeed.
"""

from __future__ import annotations

import time
from typing import Literal

import requests

WEB_ORIGIN = "https://openreview.net"
API_BASE_URL = "https://api2.openreview.net"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.5",
}


def create_openreview_session(
    *,
    mode: Literal["api", "pdf"] = "api",
    warmup_timeout: float = 30.0,
    warmup_max_attempts: int = 1,
) -> requests.Session:
    """Session that passes Cloudflare: warm up on the main site, then set Accept.

    mode ``api``: JSON API calls to ``api2.openreview.net``.
    mode ``pdf``: fetches from ``openreview.net/pdf?...``.
    """
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    for attempt in range(warmup_max_attempts):
        try:
            session.get(WEB_ORIGIN, timeout=warmup_timeout)
            break
        except requests.RequestException as e:
            last_err = e
            if attempt == warmup_max_attempts - 1:
                raise last_err
            time.sleep(1.0)
    if mode == "api":
        session.headers["Accept"] = "application/json"
    else:
        session.headers["Accept"] = "application/pdf,*/*"
    return session


def rewarm_session(session: requests.Session, *, timeout: float = 15.0) -> None:
    """Call after HTTP 403 on the API to refresh the Cloudflare session."""
    session.get(WEB_ORIGIN, timeout=timeout)


def pdf_download_url(forum_id: str) -> str:
    """HTTPS URL for the venue PDF for a forum id."""
    return f"{WEB_ORIGIN}/pdf?id={forum_id}"
