---
doc: spec
status: approved
---

# Deadline Radar — Technical Spec

## How This Works, In Plain Language

Five small Python pieces, no frameworks, nothing to install:

- A **reader** takes the plain-text URL file and hands back a list of URLs.
- A **fetcher** downloads one page at a time with a timeout, and shrugs politely (returns an error record) instead of crashing when a page is unreachable.
- An **extractor** — the heart of the app — reads raw HTML, strips it down to text, and guesses the deadline (a date sitting near words like "deadline" or "closes") and the prize (a dollar amount near words like "prize" or "cash"), plus the page title.
- A **store** keeps every extracted row in one JSON file on disk, so results survive between runs.
- A **reporter** ranks stored rows by days until the deadline and draws the same ranked table twice: once as plain terminal text, once as a self-contained HTML page.

This shape — pipe-like, each piece doing one thing — is what keeps the whole app
offline-testable: every piece except the fetcher runs without network, and tests swap
the fetcher for fixture files.

## The Core Journey Through the System

PRD ref: `prd.md > The Core Journey`.

1. User runs `python -m deadline_radar refresh` → reader loads `urls.txt` → for each URL, fetcher downloads the page (10 s timeout) → extractor pulls title/deadline/prize → store upserts the row into `data/watchlist.json` → one status line printed per URL.
2. User runs `python -m deadline_radar report` → store loads rows → reporter computes `days_remaining = deadline − today` for each row, sorts (past first, soonest next, unknown last) → prints the CLI table → renders `docs/index.html` with the same rows and a generated-at timestamp.

## Stack

- **Python 3.12, standard library only** — learner's hard constraint: zero installs, fully offline-runnable, nothing to break in a fresh clone. Tradeoff accepted: hand-rolled HTML text extraction instead of BeautifulSoup, regex date parsing instead of dateparser.
  - [`urllib.request`](https://docs.python.org/3/library/urllib.request.html) — fetching. Docs: https://docs.python.org/3/library/urllib.request.html
  - [`html.parser`](https://docs.python.org/3/library/html.parser.html) — tag stripping and `<title>` capture. Docs: https://docs.python.org/3/library/html.parser.html
  - [`re`](https://docs.python.org/3/library/re.html), [`datetime`](https://docs.python.org/3/library/datetime.html), [`json`](https://docs.python.org/3/library/json.html), [`argparse`](https://docs.python.org/3/library/argparse.html), [`pathlib`](https://docs.python.org/3/library/pathlib.html)
- **pytest 9** — tests only; already present on the machine, never imported by the app. Docs: https://docs.pytest.org/

## Where It Runs and How Someone Tries It

Local command line, Python ≥ 3.11, no API keys, no services.

```
git clone <repo> && cd deadline-radar
echo "https://some-contest-page.example" > urls.txt   # one URL per line
python3 -m deadline_radar refresh                      # the only networked step
python3 -m deadline_radar report                       # prints table, writes docs/index.html
python3 -m pytest                                      # offline test suite
```

Demo recording: `refresh` against 2–3 real public pages, then `report`, then open
`docs/index.html`, then `pytest` passing. No deployment — the video and the public
repo are the submission artifacts.

## Look and Feel

PRD ref: `prd.md > Look and Feel`. CLI: plain aligned monospace columns, no color codes —
must read cleanly when piped or screen-captured. HTML: dark background (`#0d1117`),
monospace stack, green (`#3fb950`) for future deadlines, amber (`#d29922`) under 7 days,
red (`#f85149`) for past-due; dense rows, single screen, generated-at timestamp.
Honored fully within stdlib constraints — the HTML is a hand-written template string,
no framework.

## Components

### URL Reader
Reads `urls.txt`, drops blank lines and `#` comments, returns URLs in file order.
PRD ref: `prd.md > Watching URLs`.

### Fetcher
`fetch(url) -> str` (raises on failure). Uses `urllib.request` with a browser-like
User-Agent and a 10-second timeout. The only component that touches the network.
PRD ref: `prd.md > Extracting deadline and prize`, `prd.md > States and Boundaries` (fetch failure).

### Extractor
`extract(html) -> {title, deadline, prize}`. Strips tags and script/style blocks
via `html.parser`, collapses whitespace, then:
- finds all date candidates in several formats; scores each by distance to the nearest deadline keyword within a character window; returns the best-scoring future-or-past date as ISO `YYYY-MM-DD`;
- finds all `$`/`£`/`€` amounts near prize keywords; returns the largest amount as a normalized string (e.g. `$2,500`) — largest wins because headline pages list the pool and then smaller tier amounts;
- `<title>` comes from the parser directly.
PRD ref: `prd.md > Extracting deadline and prize`. This is `scope.md > The Unique Kernel`.

### Store
`data/watchlist.json`: one JSON object, `{url: entry}`. `load()` tolerates a missing or
corrupt file (returns empty; corrupt file is renamed aside, never silently discarded).
`save()` writes atomically (temp file + rename).
PRD ref: `prd.md > States and Boundaries` (persistence).

### Reporter
`rank(entries, today) -> ordered rows` with computed `days_remaining`; `render_table(rows)`
for the terminal; `render_html(rows, generated_at)` writing `docs/index.html`.
PRD ref: `prd.md > Ranking and reporting`.

### CLI
`python -m deadline_radar <refresh|report> [--urls PATH] [--store PATH] [--html PATH]`.
`refresh` catches per-URL fetch errors, keeps previous data for that URL, marks the row
`status: failed`, and never aborts the run. Exit code 0 unless the URL file is missing.
PRD ref: `prd.md > The Core Journey`, `prd.md > States and Boundaries` (first use, fetch failure).

## Data Model

`data/watchlist.json` (gitignored — runtime state, recreated by `refresh`):

```json
{
  "https://example.com/contest": {
    "url": "https://example.com/contest",
    "title": "Example Contest",
    "deadline": "2026-10-26",
    "prize": "$2,500",
    "status": "ok",
    "error": null,
    "fetched_at": "2026-10-01T12:00:00Z"
  }
}
```

`deadline` and `prize` are `null` when not found. `status` is `ok` or `failed`; a failed
refresh preserves the last known `deadline`/`prize`. Data originates only from fetched
pages, lives only in this file, is rewritten in full by each `refresh`, and is read-only
for `report`.

## File Structure

```
deadline-radar/
├── deadline_radar/
│   ├── __init__.py
│   ├── __main__.py      # enables `python -m deadline_radar`
│   ├── cli.py           # argparse, refresh/report orchestration
│   ├── fetch.py         # urllib fetch with timeout + UA
│   ├── extract.py       # HTML→text, deadline/prize/title heuristics (the kernel)
│   ├── store.py         # JSON load/save, atomic write
│   ├── rank.py          # days-remaining computation + ordering
│   └── render.py        # CLI table + docs/index.html template
├── tests/
│   ├── conftest.py      # fixture loaders, fake fetcher
│   ├── fixtures/        # offline HTML pages (devpost-like, grant-like, no-deadline, malformed)
│   ├── test_extract.py
│   ├── test_store.py
│   ├── test_rank.py
│   ├── test_render.py
│   └── test_cli.py      # end-to-end with fake fetcher, tmp paths
├── devpost/             # Devpost learning workspace (scope/prd/spec/checklist)
├── docs/
│   └── index.html       # generated report page (committed)
├── urls.example.txt     # sample watch list
├── .gitignore
├── pytest.ini
└── README.md
```

## External Services and Dependencies

None. The app calls only the URLs the user lists (plain HTTPS GET, no auth, no keys,
subject to each site's own terms and rate expectations — one request per URL per
`refresh`). pytest is a machine-level dev tool, not an app dependency.

## Important Failure Modes

- **Page unreachable / times out** → row keeps previous data, marked `status: failed`, error message in `refresh` output and a `!` flag in the table; the run continues.
- **Page has no recognizable deadline** → `deadline: null`, row sorts last with `DAYS = ?`; prize and title still shown. Nothing is invented.
- **JavaScript-rendered page** → extractor sees the static shell only; usually yields `deadline: null` — a known, accepted limitation (PRD non-goal), reported honestly rather than guessed.

## What Was Simplified and Why

- **Regex heuristics** instead of a real NLP/date-parsing library — stdlib-only constraint; a library would add an install step and network dependency for marginal accuracy at PoC scale.
- **JSON file** instead of SQLite — a handful of rows, read whole and written whole; SQLite buys querying this app never does.
- **Static HTML regen** instead of a live server — the report is a snapshot by nature; a server would be infrastructure proving nothing about the kernel.
- **Largest-near-keyword prize pick** instead of full prize-pool accounting — pages format prizes inconsistently; the headline number is the comparable one.

## Decisions and Open Issues

- **Stdlib-only (learner choice)** — accepted tradeoff: hand-rolled extraction; keeps clone-and-run friction at zero and every test offline.
- **Character-window proximity scoring for dates** — the learner's one genuine uncertainty: how close is "near a deadline keyword", and what wins when a page has several dates? Agreed resolution: start with a 160-character window, prefer the candidate with a keyword closest before it, and let the fixture pages settle it during the build — `tests/fixtures/` holds the evidence, and any tuning change must keep the whole suite green. This investigation is recorded in the checklist's Revisions if it changes.
- **Failed refresh preserves old data (derived)** — follows from `prd.md > States and Boundaries`; implemented in the CLI's per-URL error handling.
- Open issues: none. `prd.md > Open Questions` had none blocking.
