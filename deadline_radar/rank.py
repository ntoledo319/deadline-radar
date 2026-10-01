"""Rank stored entries into a countdown: past first, soonest next, unknown last."""
from __future__ import annotations

from datetime import date


def rank(entries: dict, today: date) -> list[dict]:
    """Entries (keyed by URL) -> rows ordered by deadline, with days_remaining.

    Known deadlines sort by days ascending, so overdue entries (negative days)
    land on top — a missed deadline is the loudest signal. Entries without a
    deadline sort last with days_remaining None.
    """
    rows = []
    for entry in entries.values():
        deadline = entry.get("deadline")
        days = (date.fromisoformat(deadline) - today).days if deadline else None
        rows.append({**entry, "days_remaining": days})
    rows.sort(key=lambda r: (r["days_remaining"] is None, r["days_remaining"] or 0, r["url"]))
    return rows
