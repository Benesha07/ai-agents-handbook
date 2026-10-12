from datetime import date
from decimal import Decimal

from ledgerlite.models import Entry


def test_roundtrip_default_currency():
    e = Entry(day=date(2026, 3, 14), category="food", amount=Decimal("120.50"))
    assert Entry.from_dict(e.to_dict()) == e
    assert e.currency == "INR"


def test_roundtrip_explicit_currency():
    e = Entry(day=date(2026, 3, 14), category="food", amount=Decimal("120.50"), currency="USD")
    assert Entry.from_dict(e.to_dict()) == e
    assert e.currency == "USD"


def test_amount_is_decimal_not_float():
    e = Entry.from_dict({"day": "2026-01-01", "category": "x", "amount": "0.10", "currency": "INR"})
    assert e.amount + Decimal("0.20") == Decimal("0.30")


def test_currency_in_to_dict():
    e = Entry(day=date(2026, 1, 1), category="food", amount=Decimal("100"), currency="EUR")
    d = e.to_dict()
    assert d["currency"] == "EUR"


def test_currency_from_dict():
    d = {"day": "2026-06-01", "category": "travel", "amount": "5000", "currency": "USD"}
    e = Entry.from_dict(d)
    assert e.currency == "USD"
