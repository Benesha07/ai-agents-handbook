# Tasks: category-budgets

Rules applied:
- 3–5 tasks total
- Task 1 is the schema migration
- Every task names the files it touches (max 3)
- Every task names the tests added
- Each task ends with a demoable, verifiable increment

---

## Task 1: Schema migration — add `budgets` key to ledger file

**Objective**
Bump SCHEMA_VERSION from 1 to 2, register the v1→v2 migration that adds an empty
`budgets` dict, and update `store.load`/`store.save` to read and write the `budgets`
key. Add `load_budgets` and `save_budgets`. Provide the v1 backward-compatibility
fixture and migration test.

**Files touched**
- `src/ledgerlite/store.py` — bump SCHEMA_VERSION to 2, register MIGRATIONS[1],
  update `load`/`save` payload, add `load_budgets`/`save_budgets`
- `fixtures/ledger_v1.json` — new file: a v1 ledger with at least two entries, no
  `budgets` key
- `tests/test_store.py` — new tests (see below)

**Constraint**
`load_budgets` and `save_budgets` must route through the existing store machinery:
`load_budgets` passes the raw file dict through `_migrate` before reading the
`budgets` key; `save_budgets` reads and migrates the current file, then writes back
a payload containing `schema_version: SCHEMA_VERSION` — exactly as `save` does.
Neither function may introduce a separate migration path or write a file without
`schema_version`.

**Tests added**
- `test_v1_migration`: loads `fixtures/ledger_v1.json`, asserts `budgets == {}`,
  saves to a tmp path, asserts `schema_version == 2` in the written file
- `test_save_load_budgets`: saves budgets via `save_budgets`, reloads via
  `load_budgets`, asserts round-trip equality as `Decimal`
- `test_missing_file_budgets_empty`: `load_budgets` on a non-existent path returns `{}`

**Demo**
`python scripts/verify.py` prints `VERIFY PASS`. A v1 fixture file loads without
error and the migrated file contains `"schema_version": 2` and `"budgets": {}`.

---

## Task 2: Budget logic module

**Objective**
Create `src/ledgerlite/budget.py` with three pure functions: `month_spent`,
`budget_status`, and `is_over_budget`. No I/O. Reuses
`report.entries_in_month` for month filtering.

**Files touched**
- `src/ledgerlite/budget.py` — new module with `month_spent`, `budget_status`,
  `is_over_budget`
- `tests/test_budget.py` — new test file (see below)

**Tests added**
- `test_month_spent_sums_correct_category_and_month`
- `test_month_spent_ignores_other_months`
- `test_month_spent_ignores_other_categories`
- `test_budget_status_returns_budget_spent_remaining`
- `test_budget_status_omits_categories_without_budget` (AC-6)
- `test_is_over_budget_true_when_spend_exceeds_budget`
- `test_is_over_budget_false_when_no_budget_set` (AC-5: no warning if no budget)

**Demo**
`python scripts/verify.py` prints `VERIFY PASS`. All budget logic tests pass with
no CLI or store changes yet.

---

## Task 3: `budget set` and `budget status` CLI commands

**Objective**
Add the `budget` subcommand to the CLI with two sub-subcommands: `set` and `status`.
`budget set` validates the amount, persists via `save_budgets`, and prints the
confirmation. `budget status` loads entries and budgets, calls `budget.budget_status`,
and prints the formatted table.

**Files touched**
- `src/ledgerlite/cli.py` — add `cmd_budget_set`, `cmd_budget_status`, wire into
  parser
- `tests/test_cli.py` — new tests (see below)

**Tests added**
- `test_budget_set_happy_path`: runs `budget set food 500`, asserts exit 0 and
  stdout contains `budget food set to 500`
- `test_budget_set_invalid_amount_zero`: asserts non-zero exit, error on stderr,
  no file written (AC-4)
- `test_budget_set_invalid_amount_negative`: same as above for `-10`
- `test_budget_set_invalid_amount_string`: same for `abc`
- `test_budget_status_shows_budget_spent_remaining`: sets a budget of `500` for
  `food`, adds an entry `food 120.00` on `2026-04-15`, runs
  `budget status --year 2026 --month 4`; asserts `500`, `120.00`, and `380.00`
  all appear in stdout (AC-3). All dates are fixed; no dependency on the current
  date.
- `test_budget_status_omits_unbudgeted_category`: adds entry for category with no
  budget, asserts it does not appear in `budget status` output (AC-6)

**Demo**
```
ledgerlite --ledger demo.json budget set food 500
# stdout: budget food set to 500

ledgerlite --ledger demo.json budget status --year 2026 --month 9
# stdout: food row with budget, spent, remaining
```
`python scripts/verify.py` prints `VERIFY PASS`.

---

## Task 4: Over-budget warning in `add`

**Objective**
Modify `cmd_add` to call `is_over_budget` after a successful save and print a warning
to stderr if the category exceeds its monthly budget. Exit code remains 0 (AC-5).

**Files touched**
- `src/ledgerlite/cli.py` — modify `cmd_add` to load budgets and call
  `is_over_budget` after save
- `tests/test_cli.py` — new tests (see below)

**Tests added**
- `test_add_over_budget_warning_on_stderr`: sets a budget, adds an entry that
  exceeds it, asserts warning appears on stderr and exit code is 0 (AC-5)
- `test_add_under_budget_no_warning`: adds entry below budget, asserts stderr
  is empty
- `test_add_no_budget_no_warning`: adds entry with no budget set, asserts stderr
  is empty (AC-5: no warning if no budget)
- `test_add_over_budget_entry_persisted`: asserts the entry is saved even when
  over budget (AC-5: completes successfully)

**Demo**
```
ledgerlite --ledger demo.json budget set food 10
ledgerlite --ledger demo.json add --category food --amount 50
# stderr: warning: food is over budget for 2026-09
# exit code: 0
# entry is saved and visible in list
```
`python scripts/verify.py` prints `VERIFY PASS`.
