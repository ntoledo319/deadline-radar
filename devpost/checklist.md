---
doc: checklist
status: approved
---

# Build Checklist

Build mode: fast

## Slices

- [x] **1. `refresh` turns URLs into stored extractions**
  Becomes usable: A runnable package where `python -m deadline_radar refresh` reads `urls.txt`, fetches each page, extracts title/deadline/prize with the heuristic kernel, and stores rows in `data/watchlist.json` — with per-URL failure tolerance. Bootstrapping (package layout, pytest.ini, fixtures) lives here.
  Why now: The kernel — extraction from pages never seen before — must come first; everything else formats what it produces. Proves the whole fetch→extract→store path end to end.
  PRD ref: `prd.md > Watching URLs`, `prd.md > Extracting deadline and prize`, `prd.md > States and Boundaries` (fetch failure, persistence)
  Spec ref: `spec.md > URL Reader`, `spec.md > Fetcher`, `spec.md > Extractor`, `spec.md > Store`, `spec.md > CLI`
  Build: Create the package skeleton per the spec's file structure (`__main__.py`, `cli.py` with `refresh`, `fetch.py`, `extract.py`, `store.py`), the fixture HTML pages (devpost-like, grant-like, no-deadline, malformed), a fake-fetcher conftest, and tests for extraction (both fixture wordings, missing data, malformed input) and store round-trip/corrupt-file handling.
  Verify (mechanical): `python3 -m pytest tests/test_extract.py tests/test_store.py tests/test_cli.py -q` all green; `refresh` run with a fake fetcher via the test suite writes the expected JSON rows.
  Learner check: Run `python3 -m deadline_radar refresh` against one real URL and say whether the extracted deadline and prize match what the page says.
  Commit: `Add refresh pipeline: fetch, heuristic extraction, JSON store`

- [ ] **2. `report` ranks the watch list as a CLI table and static HTML page**
  Becomes usable: `python -m deadline_radar report` prints a ranked countdown table (past first, unknown last, days remaining) and writes `docs/index.html` with the same rows, dark radar styling, and a timestamp.
  Why now: This is the payoff screen — the ranked countdown is what the user actually comes back for, and it closes the core loop (refresh → report).
  PRD ref: `prd.md > Ranking and reporting`, `prd.md > Screens and Layout`, `prd.md > Look and Feel`
  Spec ref: `spec.md > Reporter`, `spec.md > Look and Feel`, `spec.md > Where It Runs and How Someone Tries It`
  Build: Add `rank.py` (days-remaining against an injectable `today`, ordering rules), `render.py` (fixed-width CLI table, self-contained HTML template), the `report` CLI command, README with run instructions, `urls.example.txt`, and tests for ranking order/days math, table and HTML rendering content, and a full refresh→report end-to-end with the fake fetcher.
  Verify (mechanical): `python3 -m pytest -q` all green; a scripted refresh→report against fixture-backed fake pages prints rows in the expected order and writes `docs/index.html` containing every entry.
  Learner check: Run `refresh` then `report` against 2–3 real pages, open `docs/index.html`, and say whether the ranking and look match the radar feel.
  Commit: `Add ranked countdown report: CLI table and static HTML page`

## Hands-on Checkpoints

- [ ] Early usable behavior explored — after slice 1, real-URL refresh checked (feedback can still reshape extraction before reporting is built on it)
- [ ] Final kick-the-tires exploration and feedback completed

## Final Review

- [ ] Final review complete — feedback resolved and learner confirms ready to ship

## Code Tour and App Map

- [ ] Learning activity complete — guided route, focused alternative, prior practice connected, or brief recap
- [ ] Optional edit and transfer reflection addressed — offered/declined/already covered/not applicable as appropriate
- [ ] `devpost/app-map.html` generated from finished code, checked, and shown, including a project-grounded practice to reuse

Activity and evidence:
Route and stops:
Edit outcome:
Reflection:
Activity mode:

## Revisions

- `spec.md > Extractor` signature corrected from `extract(html, today)` to `extract(html)` — extraction never needed the current date; only ranking does (`rank.py` takes `today`). Internal correction, no product change.
