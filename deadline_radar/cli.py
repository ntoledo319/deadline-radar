"""Command line: `python -m deadline_radar refresh|report`."""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from . import extract as extract_mod
from . import fetch as fetch_mod
from . import rank as rank_mod
from . import render as render_mod
from . import store as store_mod


def read_urls(path: str | Path) -> list[str]:
    """URLs from a plain-text file; blank lines and # comments ignored."""
    urls = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            urls.append(line)
    return urls


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cmd_refresh(args, fetcher=None) -> int:
    fetcher = fetcher or fetch_mod.fetch
    try:
        urls = read_urls(args.urls)
    except FileNotFoundError:
        print(f"URL file not found: {args.urls}", file=sys.stderr)
        print("Create it with one URL per line, then run `refresh` again.", file=sys.stderr)
        return 2
    if not urls:
        print(f"No URLs in {args.urls}. Add one per line, then run `refresh` again.")
        return 0

    entries = store_mod.load(args.store)
    ok = failed = 0
    for url in urls:
        try:
            info = extract_mod.extract(fetcher(url))
        except Exception as exc:
            previous = entries.get(url, {})
            entries[url] = {
                "url": url,
                "title": previous.get("title"),
                "deadline": previous.get("deadline"),
                "prize": previous.get("prize"),
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
                "fetched_at": _utc_now(),
            }
            failed += 1
            print(f"FAIL {url} — {type(exc).__name__}: {exc}")
            continue
        entries[url] = {
            "url": url,
            "title": info["title"],
            "deadline": info["deadline"],
            "prize": info["prize"],
            "status": "ok",
            "error": None,
            "fetched_at": _utc_now(),
        }
        ok += 1
        print(f"OK   {url} — deadline {info['deadline'] or '?'}, prize {info['prize'] or '?'}")

    store_mod.save(args.store, entries)
    print(f"{ok} refreshed, {failed} failed — stored in {args.store}")
    return 0


def cmd_report(args, today=None) -> int:
    today = today or date.today()
    entries = store_mod.load(args.store)
    if not entries:
        print(f"Watch list is empty ({args.store}).")
        print(f"Add URLs to {args.urls}, then run `refresh` first.")
        return 0
    rows = rank_mod.rank(entries, today)
    print(render_mod.render_table(rows))
    html_path = Path(args.html)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_mod.render_html(rows, _utc_now()), encoding="utf-8")
    print(f"\nWrote {html_path} ({len(rows)} entries)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deadline_radar",
        description="Turn contest/grant URLs into a ranked deadline countdown.",
    )
    parser.add_argument("--urls", default="urls.txt", help="watch list file (default: urls.txt)")
    parser.add_argument("--store", default="data/watchlist.json", help="JSON store path")
    parser.add_argument("--html", default="docs/index.html", help="report HTML output path")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("refresh", help="fetch every watched URL and re-extract deadline/prize")
    sub.add_parser("report", help="print the ranked countdown and write the HTML page")
    return parser


def main(argv=None, fetcher=None, today=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "refresh":
        return cmd_refresh(args, fetcher=fetcher)
    if args.command == "report":
        return cmd_report(args, today=today)
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
