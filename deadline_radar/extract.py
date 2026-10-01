"""Heuristic extraction of title, deadline, and prize from raw HTML.

The kernel of Deadline Radar: no per-site knowledge, just proximity between
dates and deadline keywords, and between currency amounts and prize keywords.
"""
from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser

DEADLINE_KEYWORDS = (
    "submissions close",
    "submission deadline",
    "applications close",
    "application deadline",
    "deadline",
    "closes",
    "closing",
    "due",
    "ends",
    "submit by",
    "submitted by",
    "apply by",
    "enter by",
)

PRIZE_KEYWORDS = (
    "prize",
    "prizes",
    "cash",
    "award",
    "awards",
    "winnings",
    "pool",
    "funding",
    "grant",
)

# How close (in characters) a keyword must be for a candidate to count.
WINDOW = 160

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}

_MONTH_NAMES = "|".join(sorted(_MONTHS, key=len, reverse=True))

_DATE_PATTERNS = (
    # October 26, 2026 / Oct 26 2026 / October 26th, 2026
    re.compile(
        rf"\b(?P<month>{_MONTH_NAMES})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?,?\s+(?P<year>\d{{4}})\b",
        re.IGNORECASE,
    ),
    # 26 October 2026 / 26th of October, 2026
    re.compile(
        rf"\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:\s+of)?\s+(?P<month>{_MONTH_NAMES})\.?,?\s+(?P<year>\d{{4}})\b",
        re.IGNORECASE,
    ),
    # 2026-10-26
    re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\b"),
    # 10/26/2026 (US numeric)
    re.compile(r"\b(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4})\b"),
)

_AMOUNT_RE = re.compile(r"([$£€])\s?(\d[\d,]*(?:\.\d{1,2})?)")


class _TextParser(HTMLParser):
    """Strip tags (and script/style bodies) down to visible text plus <title>."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_chunks: list[str] = []
        self.title_chunks: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title_chunks.append(data)
        if not self._skip_depth:
            self.text_chunks.append(data)


def _html_to_text(html: str) -> tuple[str, str | None]:
    parser = _TextParser()
    try:
        parser.feed(html)
        parser.close()
    except Exception:
        # Malformed markup: use whatever was parsed before the failure.
        pass
    text = re.sub(r"\s+", " ", " ".join(parser.text_chunks)).strip()
    title = re.sub(r"\s+", " ", " ".join(parser.title_chunks)).strip() or None
    return text, title


def _find_dates(text: str) -> list[tuple[int, int, date]]:
    """All parseable dates as (start, end, date) in document order."""
    found: list[tuple[int, int, date]] = []
    for pattern in _DATE_PATTERNS:
        for m in pattern.finditer(text):
            try:
                month = m.group("month")
                month_num = _MONTHS[month.lower().rstrip(".")] if month.isalpha() else int(month)
                found.append((m.start(), m.end(), date(int(m.group("year")), month_num, int(m.group("day")))))
            except (ValueError, KeyError):
                continue
    found.sort(key=lambda item: item[0])
    return found


def _keyword_positions(text: str, keywords: tuple[str, ...]) -> list[tuple[int, int]]:
    lowered = text.lower()
    positions: list[tuple[int, int]] = []
    for kw in keywords:
        start = 0
        while True:
            idx = lowered.find(kw, start)
            if idx == -1:
                break
            positions.append((idx, idx + len(kw)))
            start = idx + len(kw)
    return positions


def _nearest_keyword_distance(span: tuple[int, int], keywords: list[tuple[int, int]]) -> int | None:
    best: int | None = None
    for kstart, kend in keywords:
        distance = max(0, span[0] - kend, kstart - span[1])
        if best is None or distance < best:
            best = distance
    return best


def extract_deadline(text: str) -> str | None:
    """Best deadline candidate as ISO YYYY-MM-DD, or None."""
    keywords = _keyword_positions(text, DEADLINE_KEYWORDS)
    if not keywords:
        return None
    best: tuple[int, int, date] | None = None
    best_score: int | None = None
    for span_start, span_end, day in _find_dates(text):
        distance = _nearest_keyword_distance((span_start, span_end), keywords)
        if distance is None or distance > WINDOW:
            continue
        score = WINDOW - distance
        if best_score is None or score > best_score:
            best = (span_start, span_end, day)
            best_score = score
    return best[2].isoformat() if best else None


def extract_prize(text: str) -> str | None:
    """Largest currency amount near a prize keyword, normalized like '$2,500'."""
    keywords = _keyword_positions(text, PRIZE_KEYWORDS)
    if not keywords:
        return None
    best_amount = -1.0
    best_text: str | None = None
    for m in _AMOUNT_RE.finditer(text):
        distance = _nearest_keyword_distance((m.start(), m.end()), keywords)
        if distance is None or distance > WINDOW:
            continue
        symbol, digits = m.group(1), m.group(2)
        amount = float(digits.replace(",", ""))
        if amount > best_amount:
            best_amount = amount
            best_text = f"{symbol}{digits}"
    return best_text


def extract(html: str) -> dict:
    """Extract {title, deadline, prize} from a raw HTML document."""
    text, title = _html_to_text(html)
    return {
        "title": title,
        "deadline": extract_deadline(text),
        "prize": extract_prize(text),
    }
