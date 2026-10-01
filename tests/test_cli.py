import json

from deadline_radar import store
from deadline_radar.cli import main


def _write_urls(path, urls):
    path.write_text("\n".join(urls) + "\n", encoding="utf-8")


def test_refresh_extracts_and_stores(tmp_path, load_fixture, make_fetcher):
    urls_file = tmp_path / "urls.txt"
    store_path = tmp_path / "data" / "watchlist.json"
    _write_urls(urls_file, [
        "# my watch list",
        "",
        "https://hackathon.example",
        "https://grant.example",
    ])
    fetcher = make_fetcher({
        "https://hackathon.example": load_fixture("devpost_like.html"),
        "https://grant.example": load_fixture("grant_like.html"),
    })

    rc = main(["--urls", str(urls_file), "--store", str(store_path), "refresh"], fetcher=fetcher)

    assert rc == 0
    entries = json.loads(store_path.read_text())
    assert set(entries) == {"https://hackathon.example", "https://grant.example"}
    assert entries["https://hackathon.example"]["deadline"] == "2026-10-26"
    assert entries["https://hackathon.example"]["prize"] == "$2,500"
    assert entries["https://hackathon.example"]["status"] == "ok"
    assert entries["https://grant.example"]["deadline"] == "2026-11-15"


def test_refresh_failure_keeps_previous_data(tmp_path, make_fetcher, load_fixture):
    urls_file = tmp_path / "urls.txt"
    store_path = tmp_path / "watchlist.json"
    _write_urls(urls_file, ["https://flaky.example"])
    store.save(store_path, {
        "https://flaky.example": {
            "url": "https://flaky.example",
            "title": "Old Title",
            "deadline": "2026-12-01",
            "prize": "$750",
            "status": "ok",
            "error": None,
            "fetched_at": "2026-09-01T00:00:00Z",
        }
    })
    fetcher = make_fetcher({"https://flaky.example": OSError("boom")})

    rc = main(["--urls", str(urls_file), "--store", str(store_path), "refresh"], fetcher=fetcher)

    assert rc == 0
    entry = store.load(store_path)["https://flaky.example"]
    assert entry["status"] == "failed"
    assert "boom" in entry["error"]
    assert entry["deadline"] == "2026-12-01"
    assert entry["prize"] == "$750"


def test_refresh_missing_urls_file(tmp_path, capsys):
    rc = main(["--urls", str(tmp_path / "missing.txt"), "--store", str(tmp_path / "s.json"), "refresh"])
    assert rc == 2
    assert "URL file not found" in capsys.readouterr().err


def test_refresh_empty_urls_file(tmp_path, capsys):
    urls_file = tmp_path / "urls.txt"
    _write_urls(urls_file, ["# nothing here yet"])
    rc = main(["--urls", str(urls_file), "--store", str(tmp_path / "s.json"), "refresh"])
    assert rc == 0
    assert "No URLs" in capsys.readouterr().out


def test_refresh_page_with_no_deadline_stores_nulls(tmp_path, load_fixture, make_fetcher):
    urls_file = tmp_path / "urls.txt"
    store_path = tmp_path / "watchlist.json"
    _write_urls(urls_file, ["https://about.example"])
    fetcher = make_fetcher({"https://about.example": load_fixture("no_deadline.html")})

    rc = main(["--urls", str(urls_file), "--store", str(store_path), "refresh"], fetcher=fetcher)

    assert rc == 0
    entry = store.load(store_path)["https://about.example"]
    assert entry["status"] == "ok"
    assert entry["deadline"] is None
    assert entry["prize"] is None
