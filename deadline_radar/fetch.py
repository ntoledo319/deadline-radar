"""The only networked component: fetch one page with a timeout."""
from __future__ import annotations

import urllib.request

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) DeadlineRadar/0.1 "
    "(+https://github.com/ntoledo319/deadline-radar)"
)

DEFAULT_TIMEOUT = 10


def fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Download `url` and return the decoded body. Raises on any failure."""
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")
