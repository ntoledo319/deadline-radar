from deadline_radar.render import render_html, render_table

ROWS = [
    {"url": "https://missed.example", "title": "Missed Contest", "deadline": "2026-09-29",
     "prize": "$1,000", "status": "ok", "days_remaining": -2},
    {"url": "https://soon.example", "title": "Soon Contest", "deadline": "2026-10-26",
     "prize": "$2,500", "status": "ok", "days_remaining": 25},
    {"url": "https://flaky.example", "title": "Flaky Page", "deadline": None,
     "prize": None, "status": "failed", "days_remaining": None},
]


def test_table_contains_headers_and_rows():
    table = render_table(ROWS)
    lines = table.splitlines()
    assert lines[0].split()[0] == "DAYS"
    assert "DEADLINE" in lines[0] and "PRIZE" in lines[0] and "URL" in lines[0]
    assert "https://missed.example" in table
    assert "$2,500" in table
    # Unknown deadline renders as ?
    assert any(line.startswith("?") for line in lines[2:])


def test_table_flags_failed_rows():
    table = render_table(ROWS)
    assert "! Flaky Page" in table


def test_table_truncates_long_titles():
    rows = [dict(ROWS[0], title="x" * 100)]
    table = render_table(rows)
    assert "x" * 50 not in table
    assert "…" in table


def test_html_contains_every_entry_and_is_self_contained():
    html = render_html(ROWS, "2026-10-01T12:00:00Z")
    for row in ROWS:
        assert row["url"] in html
    assert "2026-10-01T12:00:00Z" in html
    assert "3 watched" in html
    assert "<style>" in html
    assert "http" not in html.split("</style>")[0]  # no external resources in <style>
    assert "<script" not in html


def test_html_row_classes_reflect_urgency():
    html = render_html(ROWS, "2026-10-01T12:00:00Z")
    assert 'class="past"' in html
    assert 'class="future"' in html
    assert 'class="unknown failed"' in html


def test_html_escapes_content():
    rows = [dict(ROWS[0], title='<script>alert("x")</script>')]
    html = render_html(rows, "2026-10-01T12:00:00Z")
    assert '<script>alert' not in html
    assert "&lt;script&gt;" in html
