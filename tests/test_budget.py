from datetime import date
from decimal import Decimal

from ledgerlite import budget
from ledgerlite.models import Entry

# Helpers — fixed entries used across tests
ENTRIES = [
    Entry(date(2026, 4, 1), "food", Decimal("100.00")),
    Entry(date(2026, 4, 15), "food", Decimal("80.00")),
    Entry(date(2026, 4, 20), "transport", Decimal("50.00")),
    Entry(date(2026, 3, 31), "food", Decimal("999.00")),   # different month
    Entry(date(2026, 5, 1), "food", Decimal("999.00")),    # different month
]


def test_month_spent_sums_correct_category_and_month():
    result = budget.month_spent(ENTRIES, "food", 2026, 4)
    assert result == Decimal("180.00")


def test_month_spent_ignores_other_months():
    # March and May entries must not appear in April total
    result = budget.month_spent(ENTRIES, "food", 2026, 4)
    assert result == Decimal("180.00")


def test_month_spent_ignores_other_categories():
    # transport entry in April must not appear in food total
    result = budget.month_spent(ENTRIES, "food", 2026, 4)
    assert Decimal("50.00") not in [result]
    assert result == Decimal("180.00")


def test_budget_status_returns_budget_spent_remaining():
    budgets = {"food": Decimal("500.00"), "transport": Decimal("100.00")}
    rows = budget.budget_status(ENTRIES, budgets, 2026, 4)
    # rows sorted by category name: food, transport
    assert len(rows) == 2
    food_row = rows[0]
    assert food_row[0] == "food"
    assert food_row[1] == Decimal("500.00")   # budget
    assert food_row[2] == Decimal("180.00")   # spent
    assert food_row[3] == Decimal("320.00")   # remaining
    transport_row = rows[1]
    assert transport_row[0] == "transport"
    assert transport_row[2] == Decimal("50.00")   # spent
    assert transport_row[3] == Decimal("50.00")   # remaining


def test_budget_status_omits_categories_without_budget():
    # transport has entries but no budget — must be absent from output (AC-6)
    budgets = {"food": Decimal("500.00")}
    rows = budget.budget_status(ENTRIES, budgets, 2026, 4)
    categories = [r[0] for r in rows]
    assert "transport" not in categories
    assert "food" in categories


def test_is_over_budget_true_when_spend_exceeds_budget():
    budgets = {"food": Decimal("150.00")}   # 180 spent > 150 budget
    assert budget.is_over_budget(ENTRIES, budgets, "food", 2026, 4) is True


def test_is_over_budget_false_when_no_budget_set():
    # AC-5: no warning if no budget set for the category
    assert budget.is_over_budget(ENTRIES, {}, "food", 2026, 4) is False
