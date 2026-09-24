# AGENTS.md

This is the portable instruction file for any coding agent that opens this repo. Kiro loads it through `.kiro/steering/project.md`. Chapter 4 of the handbook asks you to complete the TODO sections. Every line must be true and checkable.

## What this is
`ledgerlite` is a tiny personal expense ledger: a Python library in `src/ledgerlite/` and a CLI (`ledgerlite add | list | report`). Entries live in a JSON file with a schema version. Amounts are `Decimal`, never `float`.

## Commands
- Install: `python -m pip install -e ".[dev]"`
- Verify (lint plus tests, the only gate that matters): `python scripts/verify.py`
- Run: `python -m ledgerlite.cli --ledger demo.json add --category food --amount 120.50`

## Conventions
- Code lives under src/ledgerlite/; tests live under tests/ and - mirror the module names.
- Use ruff for formatting and linting with a line length of 100.
- Use Decimal for money; never use float for monetary amounts.
- Use Conventional Commits: feat:, fix:, test:, or docs:.

## Definition of done
- Run python scripts/verify.py; it must print VERIFY PASS.
- Add tests for every new behaviour.
- Keep the diff limited to the files required by the task.
- Report the files changed, tests added, and verify result.

## Never do
- Never make network calls from this repo.
- Never edit SCHEMA_VERSION without following the ledgerlite-migration skill.
- Never delete or weaken existing tests.
- Never run git push.
- Never touch .kiro/ without asking first.

## Schema changes
Any change to `Entry` fields or the JSON layout must follow the `ledgerlite-migration` skill in `.kiro/skills/`.
