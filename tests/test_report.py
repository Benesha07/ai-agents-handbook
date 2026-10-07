from datetime import date
from decimal import Decimal

import pytest

from ledgerlite import report
from ledgerlite.models import Entry


def _e(d, c, a):
    return Entry(date.fromisoformat(d), c, Decimal(a))


def test_month_range_mid_year():
    assert report.month_range(2026, 4) == (date(2026, 4, 1), date(2026, 4, 30))


def test_month_range_december():
    # Fails today: month_range does date(year, month + 1, 1) which raises
    # ValueError when month=12 because there is no month 13.
    assert report.month_range(2026, 12) == (date(2026, 12, 1), date(2026, 12, 31))


def test_entries_in_month_includes_both_ends():
    entries = [
        _e("2026-04-01", "a", "1"),
        _e("2026-04-30", "a", "2"),
        _e("2026-05-01", "a", "4"),
    ]
    got = [e.amount for e in report.entries_in_month(entries, 2026, 4)]
    assert got == [Decimal("1"), Decimal("2")]


def test_totals_by_category_sorted():
    entries = [
        _e("2026-04-02", "food", "10"),
        _e("2026-04-03", "auto", "5"),
        _e("2026-04-04", "food", "2.5"),
    ]
    assert report.totals_by_category(entries) == {"auto": Decimal("5"), "food": Decimal("12.5")}


def test_format_report_has_total_line():
    out = report.format_report(2026, 4, {"food": Decimal("12.50")})
    assert out.splitlines()[0] == "Report 2026-04"
    assert out.splitlines()[-1].split() == ["TOTAL", "12.50"]


# Characterization tests: every month of 2024, a leap year.
# Last-day values are the ground truth for 2024; February ends on the 29th.
@pytest.mark.parametrize(
    "month, expected_last",
    [
        (1,  date(2024, 1,  31)),  # January  – 31 days
        (2,  date(2024, 2,  29)),  # February – leap year, 29 days
        (3,  date(2024, 3,  31)),  # March    – 31 days
        (4,  date(2024, 4,  30)),  # April    – 30 days
        (5,  date(2024, 5,  31)),  # May      – 31 days
        (6,  date(2024, 6,  30)),  # June     – 30 days
        (7,  date(2024, 7,  31)),  # July     – 31 days
        (8,  date(2024, 8,  31)),  # August   – 31 days
        (9,  date(2024, 9,  30)),  # September– 30 days
        (10, date(2024, 10, 31)),  # October  – 31 days
        (11, date(2024, 11, 30)),  # November – 30 days
        (12, date(2024, 12, 31)),  # December – 31 days
    ],
)
def test_month_range_all_months_2024(month, expected_last):
    first, last = report.month_range(2024, month)
    assert first == date(2024, month, 1)
    assert last == expected_last
