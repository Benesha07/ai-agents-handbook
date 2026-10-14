import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from ledgerlite import store
from ledgerlite.models import Entry

# Locate the fixture relative to this file's repo root.
FIXTURES = Path(__file__).parent.parent / "fixtures"


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
    assert store.load(p) == []  # robust loading


def test_v1_fixture_migrates_currency(tmp_path):
    """Loading a v1 file must give every entry currency='INR'."""
    entries = store.load(FIXTURES / "ledger_v1.json")
    assert len(entries) == 2
    for entry in entries:
        assert entry.currency == "INR"
    assert entries[0] == Entry(date(2026, 1, 5), "rent", Decimal("15000"), currency="INR")
    assert entries[1] == Entry(date(2026, 1, 6), "food", Decimal("250.25"), currency="INR")


def test_v1_fixture_written_as_v2(tmp_path):
    """After migrating and saving, the file on disk must have schema_version 2."""
    entries = store.load(FIXTURES / "ledger_v1.json")
    out = tmp_path / "migrated.json"
    store.save(out, entries)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema_version"] == 2


def test_currency_survives_roundtrip(tmp_path):
    """Non-default currency must be preserved through save/load."""
    p = tmp_path / "ledger.json"
    entries = [
        Entry(date(2026, 6, 1), "travel", Decimal("5000"), currency="USD"),
        Entry(date(2026, 6, 2), "hotel", Decimal("8000"), currency="EUR"),
    ]
    store.save(p, entries)
    loaded = store.load(p)
    assert loaded[0].currency == "USD"
    assert loaded[1].currency == "EUR"
