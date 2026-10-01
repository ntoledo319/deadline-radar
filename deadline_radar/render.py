"""Render ranked rows as a terminal table and a self-contained HTML page."""
from __future__ import annotations

from html import escape

TITLE_WIDTH = 42

_HEADERS = ("DAYS", "DEADLINE", "PRIZE", "TITLE", "URL")


def _display_title(row: dict) -> str:
    title = row.get("title") or "(untitled)"
    if row.get("status") == "failed":
        title = "! " + title
    if len(title) > TITLE_WIDTH:
        title = title[: TITLE_WIDTH - 1] + "…"
    return title


def _display_days(row: dict) -> str:
    days = row.get("days_remaining")
    return "?" if days is None else str(days)


def render_table(rows: list[dict]) -> str:
    """Fixed-width plain-text table. No color codes — must read cleanly piped."""
    cells = [
        (
            _display_days(row),
            row.get("deadline") or "—",
            row.get("prize") or "—",
            _display_title(row),
            row["url"],
        )
        for row in rows
    ]
    widths = [len(h) for h in _HEADERS]
    for row in cells:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(_HEADERS)).rstrip()]
    lines.append("  ".join("-" * w for w in widths))
    for row in cells:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


_CSS = """
:root { color-scheme: dark; }
body { background: #0d1117; color: #c9d1d9; font-family: ui-monospace, SFMono-Regular,
  Menlo, Consolas, monospace; margin: 0; padding: 2rem; }
h1 { color: #3fb950; font-size: 1.25rem; letter-spacing: 0.05em; }
.meta { color: #8b949e; font-size: 0.85rem; margin-bottom: 1.5rem; }
table { border-collapse: collapse; width: 100%; }
th { color: #8b949e; text-align: left; text-transform: uppercase; font-size: 0.75rem;
  letter-spacing: 0.1em; border-bottom: 1px solid #30363d; padding: 0.4rem 0.75rem; }
td { border-bottom: 1px solid #21262d; padding: 0.45rem 0.75rem; font-size: 0.9rem; }
td.days, td.prize { font-weight: 700; }
tr.future td.days { color: #3fb950; }
tr.soon td.days { color: #d29922; }
tr.past td.days { color: #f85149; }
tr.failed td.title { color: #f85149; }
td.url a { color: #58a6ff; text-decoration: none; }
td.url a:hover { text-decoration: underline; }
"""


def _row_class(row: dict) -> str:
    days = row.get("days_remaining")
    if days is None:
        return "unknown"
    if days < 0:
        return "past"
    if days < 7:
        return "soon"
    return "future"


def render_html(rows: list[dict], generated_at: str) -> str:
    """Self-contained dark radar page; no JS, no external resources."""
    body_rows = []
    for row in rows:
        classes = [_row_class(row)]
        if row.get("status") == "failed":
            classes.append("failed")
        body_rows.append(
            f'    <tr class="{" ".join(classes)}">'
            f'<td class="days">{escape(_display_days(row))}</td>'
            f'<td>{escape(row.get("deadline") or "—")}</td>'
            f'<td class="prize">{escape(row.get("prize") or "—")}</td>'
            f'<td class="title">{escape(_display_title(row))}</td>'
            f'<td class="url"><a href="{escape(row["url"], quote=True)}">{escape(row["url"])}</a></td>'
            f"</tr>"
        )
    table_body = "\n".join(body_rows) or '    <tr><td colspan="5">No entries yet.</td></tr>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deadline Radar</title>
<style>{_CSS}</style>
</head>
<body>
<h1>◉ DEADLINE RADAR</h1>
<p class="meta">generated {escape(generated_at)} — {len(rows)} watched</p>
<table>
  <thead><tr><th>days</th><th>deadline</th><th>prize</th><th>title</th><th>url</th></tr></thead>
  <tbody>
{table_body}
  </tbody>
</table>
</body>
</html>
"""
