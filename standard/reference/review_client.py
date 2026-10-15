#!/usr/bin/env python3
"""Reference client for the Anchored Review Format hosted API profile.

This script checks if your system is compatible with the benchmark.
Submits a paper to a conformant endpoint, polls until the review job is
terminal, and returns the review payload. It then runs the payload through the
bundled validator and prints the verdict, so a system's creators can point this
at a staging endpoint and confirm their API is compatible with the benchmark.

This client follows the standard endpoints described in profile-api.md:

    POST /v1/reviews          -> {session_id, status}
    GET  /v1/reviews/{id}     -> {status, result?, error?}

Usage:
    python review_client.py --base-url https://api.example.com --api-key KEY paper.txt
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

# Reuse the validator that ships next to this client.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate as _validate  # noqa: E402

TERMINAL_OK = {"completed", "complete", "done", "ready", "succeeded", "success"}
TERMINAL_FAIL = {"failed", "error", "errored", "rejected", "cancelled", "canceled"}


class ReviewClient:
    def __init__(self, base_url, api_key, *, auth_header="Authorization",
                 auth_scheme="Bearer", request_timeout=60.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.auth_header = auth_header
        self.auth_scheme = auth_scheme
        self.request_timeout = request_timeout

    def _headers(self):
        value = f"{self.auth_scheme} {self.api_key}".strip() if self.auth_scheme else self.api_key
        return {self.auth_header: value, "Content-Type": "application/json"}

    def _request(self, method, url, body=None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = urllib.request.Request(url, data=data, headers=self._headers(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.request_timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            raise RuntimeError(f"{method} {url} failed (HTTP {e.code}): {detail}") from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"{method} {url} failed: {e.reason}") from e

    def submit(self, paper_text, options=None):
        """POST /v1/reviews. Returns the session id."""
        body = {"paper": {"text": paper_text}, "options": options or {}}
        resp = self._request("POST", f"{self.base_url}/v1/reviews", body)
        session_id = resp.get("session_id") or resp.get("id")
        if not session_id:
            raise RuntimeError(f"submit response missing session_id: {resp}")
        return session_id

    def fetch(self, session_id):
        """GET /v1/reviews/{id}. Returns the raw job object."""
        return self._request("GET", f"{self.base_url}/v1/reviews/{session_id}")

    def poll(self, session_id, *, interval=5.0, timeout=1200.0):
        """Poll until the job is terminal. Returns the review payload."""
        deadline = time.monotonic() + timeout
        last_status = None
        while True:
            job = self.fetch(session_id)
            status = str(job.get("status", "")).lower()
            if status != last_status:
                print(f"  status={status or '<none>'}", file=sys.stderr, flush=True)
                last_status = status
            if status in TERMINAL_OK:
                result = job.get("result")
                if result is None:
                    raise RuntimeError(f"job {session_id} is {status} but has no 'result'")
                return result
            if status in TERMINAL_FAIL:
                raise RuntimeError(f"job {session_id} {status}: {job.get('error', '(no error field)')}")
            if time.monotonic() >= deadline:
                raise TimeoutError(f"job {session_id} not done after {timeout:.0f}s (last status={status!r})")
            time.sleep(interval)

    def review(self, paper_text, *, options=None, interval=5.0, timeout=1200.0):
        """Submit a paper and return its review payload once ready."""
        session_id = self.submit(paper_text, options)
        print(f"  submitted, session_id={session_id}", file=sys.stderr, flush=True)
        return self.poll(session_id, interval=interval, timeout=timeout)


def main():
    parser = argparse.ArgumentParser(description="Reference client for the hosted API profile.")
    parser.add_argument("paper", help="Path to a paper text file to submit.")
    parser.add_argument("--base-url", required=True, help="Base URL of the review API.")
    parser.add_argument("--api-key", required=True, help="API key / token.")
    parser.add_argument("--auth-header", default="Authorization", help="Auth header name (default: Authorization).")
    parser.add_argument("--auth-scheme", default="Bearer",
                        help="Auth scheme prefix (default: Bearer). Pass '' for a bare key, e.g. x-api-key.")
    parser.add_argument("--poll-interval", type=float, default=5.0, help="Seconds between polls.")
    parser.add_argument("--timeout", type=float, default=1200.0, help="Max seconds to wait for a review.")
    parser.add_argument("--out", help="Optional path to write the returned payload.")
    args = parser.parse_args()

    paper_text = Path(args.paper).read_text(encoding="utf-8")
    client = ReviewClient(
        args.base_url, args.api_key,
        auth_header=args.auth_header, auth_scheme=args.auth_scheme,
    )

    try:
        payload = client.review(paper_text, interval=args.poll_interval, timeout=args.timeout)
    except (RuntimeError, TimeoutError) as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Payload written to {args.out}")
    else:
        print(text)

    report = _validate.Report()
    _validate.validate(payload, report)
    for w in report.warnings:
        print(f"  warning: {w}", file=sys.stderr)
    for err in report.errors:
        print(f"  error:   {err}", file=sys.stderr)
    if report.errors:
        print(f"\n✗ Returned payload is INVALID ({len(report.errors)} error(s)). See profile-api.md.", file=sys.stderr)
        return 1
    print(f"\n✓ Returned payload is VALID ({len(payload.get('comments', []))} comment(s)). API is benchmark-ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
