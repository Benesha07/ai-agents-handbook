from __future__ import annotations

from decimal import Decimal

from .models import Entry
from .report import entries_in_month


def month_spent(entries: list[Entry], category: str, year: int, month: int) -> Decimal:
    """Sum of entry amounts for the given category in the given calendar month."""
    return sum(
        (e.amount for e in entries_in_month(entries, year, month) if e.category == category),
        Decimal("0"),
    )


def budget_status(
    entries: list[Entry],
    budgets: dict[str, Decimal],
    year: int,
    month: int,
) -> list[tuple[str, Decimal, Decimal, Decimal]]:
    """Return (category, budget, spent, remaining) for every category that has a budget.
    Categories with no budget are omitted (AC-6)."""
    result = []
    for category, budget in sorted(budgets.items()):
        spent = month_spent(entries, category, year, month)
        remaining = budget - spent
        result.append((category, budget, spent, remaining))
    return result


def is_over_budget(
    entries: list[Entry],
    budgets: dict[str, Decimal],
    category: str,
    year: int,
    month: int,
) -> bool:
    """True if month_spent for category exceeds its budget.
    False if no budget is set for the category."""
    if category not in budgets:
        return False
    return month_spent(entries, category, year, month) > budgets[category]
