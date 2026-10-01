import json

from deadline_radar import store


def test_missing_file_returns_empty(tmp_path):
    assert store.load(tmp_path / "nope.json") == {}


def test_round_trip(tmp_path):
    path = tmp_path / "data" / "watchlist.json"
    entries = {"https://a.example": {"url": "https://a.example", "deadline": "2026-10-26"}}
    store.save(path, entries)
    assert store.load(path) == entries


def test_save_creates_parent_directories(tmp_path):
    path = tmp_path / "deep" / "nested" / "store.json"
    store.save(path, {})
    assert path.exists()


def test_corrupt_file_is_renamed_aside(tmp_path):
    path = tmp_path / "watchlist.json"
    path.write_text("{not json")
    assert store.load(path) == {}
    backup = tmp_path / "watchlist.json.corrupt"
    assert backup.exists()
    assert backup.read_text() == "{not json"
    assert not path.exists()


def test_non_dict_json_returns_empty(tmp_path):
    path = tmp_path / "watchlist.json"
    path.write_text(json.dumps(["a", "b"]))
    assert store.load(path) == {}
