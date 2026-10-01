"""JSON store: the whole watch list lives in one file."""
from __future__ import annotations

import json
import os
from pathlib import Path


def load(path: str | Path) -> dict:
    """Load entries keyed by URL. Missing file -> {}. A corrupt file is
    renamed aside (never silently discarded) and treated as empty."""
    p = Path(path)
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        os.replace(p, p.with_name(p.name + ".corrupt"))
        return {}
    return data if isinstance(data, dict) else {}


def save(path: str | Path, entries: dict) -> None:
    """Write entries atomically (temp file + rename)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(json.dumps(entries, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(tmp, p)
