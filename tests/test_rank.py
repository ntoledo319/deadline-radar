from datetime import date

from deadline_radar.rank import rank

TODAY = date(2026, 10, 1)


def _entry(url, deadline, status="ok"):
    return {"url": url, "title": url, "deadline": deadline, "prize": None,
            "status": status, "error": None, "fetched_at": "2026-10-01T00:00:00Z"}


def test_past_first_then_soonest_then_unknown_last():
    entries = {
        "https://later.example": _entry("https://later.example", "2026-10-26"),
        "https://soon.example": _entry("https://soon.example", "2026-10-06"),
        "https://missed.example": _entry("https://missed.example", "2026-09-29"),
        "https://unknown.example": _entry("https://unknown.example", None),
    }
    rows = rank(entries, TODAY)
    assert [r["url"] for r in rows] == [
        "https://missed.example",
        "https://soon.example",
        "https://later.example",
        "https://unknown.example",
    ]


def test_days_remaining_math():
    rows = rank({"https://a.example": _entry("https://a.example", "2026-10-26")}, TODAY)
    assert rows[0]["days_remaining"] == 25
    rows = rank({"https://b.example": _entry("https://b.example", "2026-09-29")}, TODAY)
    assert rows[0]["days_remaining"] == -2
    rows = rank({"https://c.example": _entry("https://c.example", None)}, TODAY)
    assert rows[0]["days_remaining"] is None


def test_today_is_zero_days():
    rows = rank({"https://a.example": _entry("https://a.example", "2026-10-01")}, TODAY)
    assert rows[0]["days_remaining"] == 0


def test_empty_store_ranks_empty():
    assert rank({}, TODAY) == []
