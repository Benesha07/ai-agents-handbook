1. Task I would Delegate
### bus attendance project
### Task
I would delegate fixing a small authentication bug in the bus attendance system.

### Four Questions

- **Bounded:** Yes. The task can be limited to `js/auth.js`.
- **Verifiable:** Yes. I can test the login and authentication flow and verify that the user is authenticated correctly.
- **Reversible:** Yes. The changes can be reverted using Git if something goes wrong.
- **Understood:** Yes. I understand that the task is to fix the authentication issue without changing the overall authentication architecture.

### Files
- `js/auth.js`

### Verification Command
```bash
git diff

2. Task

I would not delegate making the overall security and authentication architecture decisions for the bus attendance system.

Four Questions
Bounded: No. The decision can affect multiple parts of the project.
Verifiable: No. Security architecture cannot be fully verified by a single test or command.
Reversible: Yes. Git can revert code changes, but a wrong architecture decision can affect many parts of the system.
Understood: Yes. I understand the purpose of the authentication and security requirements.
Question That Fails

Bounded and Verifiable fail because the architecture affects multiple components and cannot be completely validated with one simple verification command.

3. Reflection

The habit I have rarely seen in student projects is treating AI-generated code as an untrusted contribution. Students may accept AI-generated code when it works without reviewing every change carefully. Reviewing the complete diff is important because passing a test does not always mean that the implementation is correct or secure.


chapter 3
round 1 (just random fix the add comment)
Files changed: src/ledgerlite/cli.py, tests/test_cli.py
tests added :Yes. Kiro added 7 new tests covering invalid-input cases and checking that the ledger file is not created when validation fails.
as anything else improved that I did not ask for?** Yes. Kiro also added validation for bad date strings and non-numeric amounts, even though I only asked it to fix validation in the `add` command without specifying these additional cases.
- **Verification:** `python scripts/verify.py` returned `VERIFY PASS` with 19 tests passing.


Reflection

The naive run made additional validation changes and added more tests than I specifically requested.
The directed brief prevented this by clearly defining the rules, test cases, scope, and definition of done.
The line "Do not change any other file" specifically prevented changes outside src/ledgerlite/cli.py and tests/test_cli.py.


## Chapter 4 Part B — Skills Experiment

I ran the same `currency` schema-change task twice on separate branches: once with the `ledgerlite-migration` skill hidden and once with the skill available.

### No-skill run

The no-skill agent still implemented a correct migration. It:

* Added `currency` with default `"INR"` to `Entry`.
* Persisted `currency` in the JSON ledger.
* Bumped `SCHEMA_VERSION` from 1 to 2.
* Added a v1-to-v2 migration that supplies `"INR"` to existing entries.
* Added a `ledger_v1.json` fixture.
* Added migration and model tests.
* Did not modify the CLI.
* Passed `python scripts/verify.py` with `VERIFY PASS`.

Commit: `49e346f`

### With-skill run

The with-skill agent first read `.kiro/skills/ledgerlite-migration/SKILL.md` and then created a plan that explicitly followed the required migration sequence.

It:

* Bumped `SCHEMA_VERSION` from 1 to 2.
* Registered the v1-to-v2 migration.
* Added `currency: str = "INR"`.
* Persisted and loaded `currency`.
* Used direct key access in `from_dict`.
* Created the required v1 fixture.
* Added migration and round-trip tests.
* Kept the CLI untouched.
* Passed `python scripts/verify.py` with `VERIFY PASS`.

Commit: `4b93a33`

### Reflection

The interesting result was that the no-skill agent did not fail; it happened to infer the correct migration approach. However, the skill made the required process explicit and checkable before implementation.

I would merge the with-skill run because it follows the repository's documented migration procedure explicitly and makes the reasoning and required safeguards easier to audit.

If the no-skill approach were used for future schema changes, the current implementation would not necessarily break after six months. The bigger risk would be process drift: a future agent might forget a schema-version bump, migration registration, backward-compatibility fixture, or migration test. The skill reduces that risk by providing a repeatable procedure instead of depending on the agent to infer all of the requirements each time.


chapter 5
# Category Budgets — Acceptance Criteria

1. **Ubiquitous:**
   The system shall store budgets in the ledger file under a `budgets` key mapping each category to a positive Decimal amount.

2. **Event-driven:**
   WHEN the user runs `budget set <category> <amount>`, the system shall persist the budget and print `budget <category> set to <amount>`.

3. **Event-driven:**
   WHEN the user runs `budget status --year Y --month M`, the system shall print, for each category with a budget, the budget amount, the month-to-date spent amount, and the remaining amount.

4. **Unwanted:**
   IF `<amount>` is not a positive Decimal THEN the system shall reject the budget, print an error message, and shall not persist the invalid budget.

5. **State-driven:**
   WHILE a category's month-to-date spend exceeds its budget, the `add` command shall print an over-budget warning to stderr and shall complete successfully without changing its exit code.

6. **Optional:**
   WHERE no budget exists for a category, `budget status --year Y --month M` shall omit that category from the budget status output.
