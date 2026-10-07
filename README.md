# Deadline Radar

Paste competition/grant URLs; get a ranked countdown of what closes next and what
it's worth. Python 3.11+ standard library only — nothing to install.

Built for the Devpost **Build With AI: Basics** hackathon with the Devpost Learn
Skill Pack. The planning documents the process produced are in
[`devpost/`](devpost/): [scope](devpost/scope.md) · [prd](devpost/prd.md) ·
[spec](devpost/spec.md) · [build checklist](devpost/checklist.md).

**Demo video:** https://youtu.be/Sx2gVP23gK4 (1 min, unlisted)

**Live demo:** https://ntoledo319.github.io/deadline-radar/

## How it works

`refresh` fetches every URL in your watch list, extracts the deadline (a date near
words like "deadline/closes/due") and the prize (a currency amount near
"prize/award/cash") with site-agnostic heuristics, and stores results in
`data/watchlist.json`. `report` ranks entries by days remaining — overdue first,
unknown last — prints a terminal table, and writes a self-contained dark HTML page
to `docs/index.html`.

## Usage

```bash
cp urls.example.txt urls.txt   # then edit: one URL per line, # comments ok
python3 -m deadline_radar refresh   # the only networked step
python3 -m deadline_radar report    # prints table, writes docs/index.html
```

Options: `--urls PATH` (default `urls.txt`), `--store PATH`
(default `data/watchlist.json`), `--html PATH` (default `docs/index.html`).

## Tests

Fully offline — fixture HTML pages, a fake fetcher, no network ever:

```bash
python3 -m pytest
```

## Honest limitations

- Heuristics, not guarantees: a page with no recognizable date near a deadline
  keyword is reported as `?` rather than guessed.
- JavaScript-rendered pages only yield their static shell (stdlib-only constraint).
- A failed fetch keeps the last known data and flags the row with `!`.
