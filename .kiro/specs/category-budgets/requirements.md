  # Requirements: category-budgets

  ## Summary

  A user sets a monthly spending budget per category. The system
  persists budgets in the
  ledger file, reports spend against budget for any given month, and
  warns on stderr when
  an entry pushes a category over its budget.

  Source of truth: the six acceptance criteria in NOTES.md, Chapter
  5.
  Every requirement here is traceable to one criterion (AC-1 through
  AC-6).
  No behavior is added beyond those criteria.

  ---

  ## Feature constraint: schema migration
  
  Storing budgets in the ledger file changes the JSON schema. The
  `ledgerlite-migration`
  skill must be followed: SCHEMA_VERSION must be bumped, a migration
  function must be
  registered, and a backward-compatibility fixture and test must be
  provided.
  This is a constraint on how AC-1 is implemented, not an additional
  acceptance criterion.

  ---

  ## User Stories
  
  ### US-1 — Store budgets in the ledger file
  
  As a user, I want my budgets saved in the same ledger file as my
  entries.
  
  **AC-1 (Ubiquitous)**
  The system shall store budgets in the ledger file under a `budgets`
  key mapping each
  category name to a positive Decimal amount.
  
  ---
  
  ### US-2 — Set a budget for a category
  
  As a user, I want to run a command to set a budget for a category.
  
  **AC-2 (Event-driven)**
  WHEN the user runs `budget set <category> <amount>`, the system
  shall:
  1. Persist the budget.
  2. Print `budget <category> set to <amount>`.
  
  **AC-4 (Unwanted)**
  IF `<amount>` is not a positive Decimal THEN the system shall:
  1. Reject the budget.
  2. Print an error message.
  3. Not persist the invalid budget.
  
  ---
  
  ### US-3 — View budget status for a month
  
  As a user, I want to see budget versus actual spend for each
  budgeted category in a
  given month.
  
  **AC-3 (Event-driven)**
  WHEN the user runs `budget status --year Y --month M`, the system
  shall print, for each
  category with a budget:
  - the budget amount,
  - the month-to-date spent amount,
  - and the remaining amount.
  
  **AC-6 (Optional)**
  WHERE no budget exists for a category, `budget status --year Y
  --month M` shall omit
  that category from the output.
  
  ---
  
  ### US-4 — Over-budget warning on `add`

  As a user, I want the `add` command to warn me when a category goes
  over its monthly
  budget.
  
  **AC-5 (State-driven)**
  WHILE a category's month-to-date spend exceeds its budget, the
  `add` command shall:
  1. Print an over-budget warning to stderr.
  2. Complete successfully without changing its exit code.
  
