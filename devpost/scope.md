---
doc: scope
status: approved
---

# Deadline Radar

One line: paste competition/grant URLs, get a ranked countdown watch list of what closes next and what it's worth.

## The Unique Kernel
Automatic extraction of the two facts that matter from any contest page — **the deadline
and the prize money** — using simple heuristics (date patterns near words like
"deadline/closes/due", currency amounts near "prize/award/cash"), so any URL becomes a
comparable row in a ranked countdown without manual reading. Delete that and it's just a
bookmarks file.

## Who It's For
The maker who enters hackathons, contests, and grant programs — concretely, the learner
himself. He juggles several open applications at once and today tracks closing dates by
re-opening browser tabs and skimming each page, which is how deadlines get missed.

## The Core Loop
He keeps a plain-text list of URLs he's watching. He runs `refresh` — the tool fetches
every page, re-extracts deadline and prize, and stores the result. He runs `report` and
sees the watch list ranked by days remaining: what's closing soonest, what's it worth,
what he already missed. He comes back every time a new contest catches his eye or a
deadline is getting close.

## Inspiration & Identity
A radar scope, not a dashboard: dense, fast, glanceable. Terminal-first, monospace,
green-on-dark, countdown energy. The static HTML page is the same table, shareable.
Reference feeling: `htop` — everything on one screen, sorted by what needs attention.

## Why This Matters to the Learner
In his words: he runs multiple contest and grant applications at once and the tool
answers "what closes next, and what's it worth?" Missing a deadline is losing money he
had already half-earned.

## What "Working" Looks Like
Point it at 2–3 real public pages (a live hackathon page, a real grant page), run
`refresh`, run `report`, and see correct deadlines and prizes in a ranked countdown —
"that devpost hackathon closes in 25 days and it's $2,500" — in both the terminal table
and `docs/index.html`. The "oh, that's cool" beat: a page it has never seen before still
yields the right date and dollar amount.

## The POC Boundary
In: URL list in, fetch, heuristic extraction (deadline + prize), JSON storage, ranked
countdown, CLI table, one static HTML page, offline tests with fixture HTML.
Out: anything requiring accounts, JavaScript rendering, or per-site parsers.

## Later
- Notifications (email/desktop) when a deadline is under N days.
- Per-site parser plugins for pages where heuristics fail.
- A `watch` mode that refreshes on a schedule.
- Manual override commands to correct a wrong extraction.

## Explicitly Cut
- **Per-site parsers** — defeats the point; the kernel is that heuristics work on pages never seen before.
- **JavaScript-rendered pages** — needs a headless browser; stdlib-only constraint, and most rules pages are static HTML.
- **Web UI / server** — a static HTML page plus CLI covers the demo in a minute; a server adds nothing to the kernel.
- **External libraries (requests, BeautifulSoup, dateparser)** — stdlib-only keeps it install-free and offline-testable.
