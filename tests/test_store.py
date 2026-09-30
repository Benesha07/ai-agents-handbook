import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerlite import store
from ledgerlite.models import Entry


def test_missing_file_is_empty(tmp_path):
    assert store.load(tmp_path / "nope.json") == []


def test_save_then_load(tmp_path):
    p = tmp_path / "ledger.json"
    entries = [
        Entry(date(2026, 1, 5), "rent", Decimal("15000")),
        Entry(date(2026, 1, 6), "food", Decimal("250.25")),
    ]
    store.save(p, entries)
    assert store.load(p) == entries


def test_corrupt_file_raises(tmp_path):
    p = tmp_path / "ledger.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError):
        store.load(p)


# --- Task 1: schema migration tests ---

FIXTURE_V1 = Path(__file__).parent.parent / "fixtures" / "ledger_v1.json"


def test_v1_migration(tmp_path):
    # load via store.load — entries should come through correctly
    entries = store.load(FIXTURE_V1)
    assert len(entries) == 2
    assert entries[0].category == "rent"
    assert entries[1].category == "food"

    # load_budgets should return empty dict after migration
    budgets = store.load_budgets(FIXTURE_V1)
    assert budgets == {}

    # save to tmp and assert schema_version is bumped to 2
    out = tmp_path / "migrated.json"
    store.save(out, entries)
    written = json.loads(out.read_text(encoding="utf-8"))
    assert written["schema_version"] == 2
    assert written["budgets"] == {}


def test_save_load_budgets(tmp_path):
    p = tmp_path / "ledger.json"
    budgets_in = {"food": Decimal("500.00"), "transport": Decimal("200.00")}
    store.save_budgets(p, budgets_in)
    budgets_out = store.load_budgets(p)
    assert budgets_out == budgets_in
    assert all(isinstance(v, Decimal) for v in budgets_out.values())


def test_missing_file_budgets_empty(tmp_path):
    assert store.load_budgets(tmp_path / "nope.json") == {}
