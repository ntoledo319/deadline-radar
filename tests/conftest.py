from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> str:
        return (FIXTURES / name).read_text(encoding="utf-8")
    return _load


@pytest.fixture
def make_fetcher():
    """Build a fake fetcher from a {url: html-or-exception} mapping."""
    def _make(mapping):
        def _fetch(url: str) -> str:
            value = mapping[url]
            if isinstance(value, Exception):
                raise value
            return value
        return _fetch
    return _make
