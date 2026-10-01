---
doc: prd
status: approved
---

# Deadline Radar — Product Requirements

A terminal-first watch list that turns a list of competition/grant URLs into a ranked
countdown of deadlines and prizes, for a maker who enters several contests at once.
Source: `scope.md > The Unique Kernel`, `scope.md > Who It's For`.

## The Core Journey

1. The user keeps a plain-text file of URLs — one per line — for contests and grants he is watching.
2. He runs `refresh`. For each URL the tool fetches the page, extracts a deadline and a prize amount, and stores the result. Each line of output reports what it found (or that it found nothing) for that URL.
3. He runs `report`. The terminal shows a ranked table: days remaining, deadline date, prize, title, URL — soonest deadline first. The same table is written to a static HTML page he can open in a browser.
4. Success: he looks at one screen and knows what closes next, what it's worth, and what he already missed. Source: `scope.md > The Core Loop`, `scope.md > What "Working" Looks Like`.

## Screens and Layout

Two surfaces, same content:

- **CLI table** — fixed-width columns: `DAYS`, `DEADLINE`, `PRIZE`, `TITLE`, `URL`. Rows sorted by deadline ascending; entries with no extractable deadline sort last with `DAYS = ?`. Past deadlines show a negative day count and sort first — they are the loudest signal ("you missed this").
- **Static HTML page** (`docs/index.html`) — the same ranked table plus a generated-at timestamp, styled dark/monospace, sorted identically. No JavaScript required to read it; fully self-contained so it works from `file://`.

## Look and Feel

Radar, not dashboard: dark background, monospace type, green/amber accents, dense rows,
countdown energy. Terminal output is plain aligned text (no color codes required —
must read cleanly when piped or captured). Reference: `htop`'s everything-on-one-screen
density. Source: `scope.md > Inspiration & Identity`.

## Features and Behavior

### Watching URLs

The user manages the watch list as a text file of URLs, one per line (blank lines and
`#` comments ignored). `refresh` processes every URL in the file.

- As a contest entrant, I want to add a contest to my watch list by pasting its URL into a text file, so that I never touch a database or a UI.
  - [ ] A text file with three URLs produces three stored entries after `refresh`.

### Extracting deadline and prize

For each fetched page, the tool extracts, without any per-site knowledge:

- **Deadline** — a date found near a deadline keyword ("deadline", "closes", "closing", "due", "ends", "submit by"). Multiple date formats are recognized (e.g. `October 26, 2026`, `Oct 26 2026`, `2026-10-26`, `10/26/2026`).
- **Prize** — a currency amount found near a prize keyword ("prize", "prizes", "cash", "award", "winnings").
- **Title** — the page's `<title>`.

- As a contest entrant, I want the tool to pull the deadline and prize off a page it has never seen before, so that any contest URL becomes a comparable row without me reading the page.
  - [ ] A fixture page containing "Submissions close October 26, 2026" and "$2,500 in prizes" yields deadline 2026-10-26 and prize $2,500.
  - [ ] The same extraction code path handles at least two differently-worded fixture pages.

### Ranking and reporting

Entries are ranked by deadline ascending (soonest first; past first; unknown last).
`report` prints the CLI table and regenerates the HTML page.

- As a contest entrant, I want the list ranked by days remaining, so that the row needing action today is always on top.
  - [ ] Given stored entries with deadlines in 5, 25, and −2 days, report order is −2, 5, 25, and the days-remaining values are computed against the current date.
  - [ ] `docs/index.html` is written on every `report` run and contains every stored entry.

## States and Boundaries

- **First use** — no store file yet: `report` says the watch list is empty and tells the user to add URLs and run `refresh`.
- **Fetch failure** — a URL that errors (DNS, HTTP error, timeout) keeps its previous stored data if any, and is reported as failed in `refresh` output and flagged in the table; one bad URL never aborts the run.
- **Nothing extracted** — a page with no recognizable deadline stores with deadline unknown and sorts last with `DAYS = ?`; the prize may still be shown.
- **Persistence** — the JSON store is the only state; it survives between runs and is rewritten by each `refresh`. Deleting it starts over cleanly.
- **Offline correctness** — extraction, ranking, and rendering never touch the network; only `refresh` does.

## Product Decisions

- **Plain-text URL file, edited by hand** — the user asked for zero UI friction and no new dependencies; a text file is the whole "add" flow.
- **Heuristics over per-site parsers** — the kernel (`scope.md > The Unique Kernel`) is that unseen pages still work; a wrong guess on an unusual page is an acceptable tradeoff at PoC scale.
- **Past deadlines shown, sorted first** — a missed deadline is more actionable information than hiding it.
- **Same ranking in CLI and HTML** — one canonical order; the HTML page is the shareable artifact, not a second product.

## What We're Building

- URL-file reading (`urls.txt`).
- Fetch with timeout and error tolerance.
- Heuristic extraction (deadline, prize, title) from raw HTML.
- JSON store.
- Ranked countdown computation against the current date.
- CLI table output and `docs/index.html` generation.
- Offline test suite over fixture HTML pages.

## Deferred From the POC

- **Manual correction command** — if heuristics misread a page there is no override; editing the store JSON by hand is the workaround. A real `set` command needs CLI design time the demo doesn't.
- **Scheduled refresh** — the user runs `refresh` when he cares; cron/systemd is deployment plumbing, not product.
- **Notifications** — the countdown table is the notification at this scale.

## Possible Later Enhancements

- `watch` mode with desktop/email alerts under N days.
- Per-site parser plugins falling back to heuristics.
- Prize normalization (sum prize pools, handle non-USD).

## Non-Goals

- **JavaScript-rendered pages** — stdlib-only constraint (`scope.md > Explicitly Cut`); a page that needs JS to show its deadline will extract as unknown.
- **Accounts, sync, multi-user** — single local user, single machine.
- **A server or web UI** — static HTML only.
- **Guaranteed extraction accuracy** — best-effort heuristics, honestly reported when they fail.

## Open Questions

None blocking. Which exact real pages to demo with is chosen at ship time from whatever contests are live.
