from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from .models import Entry

SCHEMA_VERSION = 2

# Maps a schema version to the function that upgrades a raw file dict to the next version.
MIGRATIONS: dict[int, Callable[[dict], dict]] = {}


def _migrate_v1_to_v2(data: dict) -> dict:
    """Add empty budgets key to a v1 file dict."""
    data["budgets"] = {}
    return data


MIGRATIONS[1] = _migrate_v1_to_v2


def _migrate(data: dict) -> dict:
    version = data.get("schema_version", 1)
    while version < SCHEMA_VERSION:
        data = MIGRATIONS[version](data)
        version += 1
        data["schema_version"] = version
    return data


def _read_and_migrate(path: Path) -> dict:
    """Read a ledger file and run all pending migrations. Returns the migrated dict."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return _migrate(data)


def load(path: Path) -> list[Entry]:
    """Load entries. A missing file is an empty ledger. A corrupt file is an error."""
    if not path.exists():
        return []
    data = _read_and_migrate(path)
    return [Entry.from_dict(d) for d in data["entries"]]


def save(path: Path, entries: list[Entry]) -> None:
    # Preserve existing budgets if the file already exists; otherwise start with {}.
    if path.exists():
        existing = _read_and_migrate(path)
        budgets = existing.get("budgets", {})
    else:
        budgets = {}
    payload = {
        "schema_version": SCHEMA_VERSION,
        "entries": [e.to_dict() for e in entries],
        "budgets": budgets,
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_budgets(path: Path) -> dict[str, Decimal]:
    """Load budgets. A missing file is an empty ledger (returns {})."""
    if not path.exists():
        return {}
    data = _read_and_migrate(path)
    return {category: Decimal(amount) for category, amount in data.get("budgets", {}).items()}


def save_budgets(path: Path, budgets: dict[str, Decimal]) -> None:
    """Persist budgets, preserving entries. Routes through _migrate; always writes
    schema_version: SCHEMA_VERSION."""
    if path.exists():
        data = _read_and_migrate(path)
        entries_raw = data.get("entries", [])
    else:
        entries_raw = []
    payload = {
        "schema_version": SCHEMA_VERSION,
        "entries": entries_raw,
        "budgets": {category: str(amount) for category, amount in budgets.items()},
    }
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp.replace(path)
