# Design: category-budgets

## Requirements reference
This design implements requirements.md (AC-1 through AC-6) for the category-budgets
feature. Every design decision below is traceable to an AC or to the schema migration
constraint.

---

## 1. Data model (AC-1)

The ledger JSON file gains a top-level `budgets` key alongside `entries` and
`schema_version`:

```json
{
  "schema_version": 2,
  "entries": [...],
  "budgets": {
    "food": "500.00",
    "transport": "200.00"
  }
}
```

- Keys are category name strings.
- Values are Decimal amounts serialized as strings (same convention as entry amounts).
- A missing `budgets` key is treated as an empty dict (no budgets set).

---

## 2. Schema migration (feature constraint)

Following the `ledgerlite-migration` skill exactly:

| Step | Action |
|---|---|
| 1 | Bump `SCHEMA_VERSION` in `store.py`: 1 → 2 |
| 2 | Register `MIGRATIONS[1]` — adds `"budgets": {}` to any v1 file dict |
| 3 | Update `store.load` and `store.save` to read/write `budgets` |
| 4 | Add `fixtures/ledger_v1.json` with at least two entries, no `budgets` key |
| 5 | Add test in `tests/test_store.py`: load fixture, assert `budgets == {}`, save, assert `schema_version == 2` |

`models.py` (`Entry`) is not changed — `budgets` is a file-level key, not an entry field.

---

## 3. Store API changes (AC-1, AC-2)

`store.py` gains two functions alongside `load` and `save`:

```
load_budgets(path: Path) -> dict[str, Decimal]
save_budgets(path: Path, budgets: dict[str, Decimal]) -> None
```

Both functions route through the existing store machinery:

- A missing file is treated as an empty ledger, consistent with the existing `load`
  docstring: `"A missing file is an empty ledger."` No new missing-file behavior is
  introduced.
- `load_budgets` reads the raw file dict, passes it through `_migrate` (the same
  function `load` uses), then returns the `budgets` key as `dict[str, Decimal]`.
  This ensures any pending migration is applied before budgets are read.
- `save_budgets` reads the current file (migrating if needed), replaces the `budgets`
  key, and writes back a payload that always includes `schema_version: SCHEMA_VERSION`
  — the same field `save` always writes. Budget persistence cannot bypass the schema
  version mechanism because every write goes through the same payload construction.
- The atomic write pattern (`.tmp` → `replace`) is reused unchanged.

`_migrate` is not modified. It remains the single path through which all file reads
pass.

---

## 4. Budget logic module (AC-3, AC-5)

A new module `src/ledgerlite/budget.py` contains pure functions:

```
def month_spent(entries: list[Entry], category: str, year: int, month: int) -> Decimal
    """Sum of entry amounts for category in the given month."""

def budget_status(
    entries: list[Entry],
    budgets: dict[str, Decimal],
    year: int,
    month: int,
) -> list[tuple[str, Decimal, Decimal, Decimal]]
    """For each category in budgets, return (category, budget, spent, remaining).
    Categories with no budget are omitted (AC-6)."""

def is_over_budget(
    entries: list[Entry],
    budgets: dict[str, Decimal],
    category: str,
    year: int,
    month: int,
) -> bool
    """True if month_spent for category exceeds its budget. False if no budget set."""
```

These functions are pure (no I/O) and reuse `report.entries_in_month` for month
filtering.

---

## 5. CLI changes (AC-2, AC-3, AC-4, AC-5)

### 5a. New `budget` subcommand (AC-2, AC-3, AC-4)

```
ledgerlite budget set <category> <amount>
ledgerlite budget status --year Y --month M
```

`budget` is a subcommand of the existing parser. It has two sub-subcommands: `set`
and `status`.

**`budget set` (AC-2, AC-4)**
1. Validate `<amount>`: attempt `Decimal(amount)`, check > 0. On failure: print error
   to stderr, return non-zero (AC-4 requires rejection and no persistence; exit code
   is an implementation choice consistent with the existing `add` validation pattern).
2. On success: call `save_budgets`, print `budget <category> set to <amount>`.

**`budget status` (AC-3, AC-6)**
1. Call `load_budgets` and `store.load`.
2. Call `budget.budget_status(entries, budgets, year, month)`.
3. Print one line per result row. Output format:

```
Budget status 2026-09
  food            500.00    320.00    180.00
  transport       200.00    200.00      0.00
```
Columns: category (left, 16), budget (right, 12.2f), spent (right, 12.2f),
remaining (right, 12.2f). Mirrors the existing `report` format for consistency.

### 5b. Modified `add` command (AC-5)

After `store.save(args.ledger, entries)` succeeds:
1. Call `load_budgets`.
2. Call `is_over_budget(entries, budgets, entry.category, entry.day.year, entry.day.month)`.
3. If True: print warning to `sys.stderr`. Exit code remains 0.

Warning text (implementation choice, not prescribed by AC-5):
```
warning: <category> is over budget for <YYYY-MM>
```

---

## 6. Error handling

| Situation | Behaviour | AC |
|---|---|---|
| `<amount>` not a positive Decimal in `budget set` | print error to stderr, do not persist | AC-4 |
| No budget set for a category in `budget status` | category omitted from output | AC-6 |
| No budget set for a category in `add` | no warning printed | AC-5 |
| Ledger file does not exist | empty entries and empty budgets | AC-1 (consistent with existing `load`) |

---

## 7. Testing strategy

| Test file | What it covers |
|---|---|
| `tests/test_store.py` | v1 fixture migration; round-trip save/load of budgets |
| `tests/test_budget.py` | `month_spent`, `budget_status`, `is_over_budget` pure logic |
| `tests/test_cli.py` | `budget set` happy path; `budget set` invalid amount; `budget status` output; `add` over-budget warning on stderr; `add` still exits 0 when over budget |

---

## 8. Files touched

| File | Change |
|---|---|
| `src/ledgerlite/store.py` | bump SCHEMA_VERSION, add migration, add `load_budgets`/`save_budgets` |
| `src/ledgerlite/budget.py` | new module |
| `src/ledgerlite/cli.py` | add `budget` subcommand, modify `cmd_add` |
| `fixtures/ledger_v1.json` | new fixture |
| `tests/test_store.py` | migration test |
| `tests/test_budget.py` | new test file |
| `tests/test_cli.py` | new CLI tests |

`src/ledgerlite/models.py` is not touched — `budgets` is a file-level key, not an
`Entry` field.
