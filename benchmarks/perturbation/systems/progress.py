"""Progress-logging utilities for the coarse adapter.

`coarse` emits little progress output during a review and runs for several
minutes per paper; adapter callers wrap each subprocess with heartbeat()
so the operator sees the job is still alive.
"""

from __future__ import annotations

import contextlib
import subprocess
import sys
import threading
import time
from typing import Iterator


@contextlib.contextmanager
def heartbeat(tag: str, interval: float = 30.0) -> Iterator[None]:
    """Print '[{tag}] elapsed Ys' every `interval` seconds until the context exits.

    Runs on a daemon thread so it stops automatically if the parent aborts.
    All output goes to stderr so stdout stays clean for any piped JSON.
    """
    stop = threading.Event()
    start = time.time()

    def _loop() -> None:
        while not stop.wait(interval):
            elapsed = int(time.time() - start)
            print(f"[{tag}] elapsed {elapsed}s", file=sys.stderr, flush=True)

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1.0)


def stream_prefixed(proc: subprocess.Popen, tag: str) -> None:
    """Stream a subprocess's stdout+stderr to our stderr, line-by-line, prefixed.

    Blocks until the subprocess exits. Uses a background thread for stderr
    so both streams drain concurrently (avoids pipe-buffer deadlock).
    """
    def _drain(src, label: str) -> None:
        if src is None:
            return
        for raw in iter(src.readline, b""):
            line = raw.decode("utf-8", errors="replace").rstrip()
            print(f"[{tag}] {line}" if not label else f"[{tag}][{label}] {line}",
                  file=sys.stderr, flush=True)

    err_thread = threading.Thread(target=_drain, args=(proc.stderr, "err"), daemon=True)
    err_thread.start()
    _drain(proc.stdout, "")
    err_thread.join(timeout=5.0)
