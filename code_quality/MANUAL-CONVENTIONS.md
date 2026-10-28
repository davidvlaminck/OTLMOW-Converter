# Manual conventions (no ruff rule)

This file collects conventions that cannot be enforced by a linter. Append a new entry here whenever a new manual rule is agreed upon.

Each entry here must have a corresponding custom check, and that check's result must be added to the QA report table.

## How to add a new manual convention (for agents)

1. **Add the rule** to this file with a short description, rationale, and fix.
2. **Implement a check** in `code_quality/scripts/qa_report.py`:
   - Write `def check_<name>(paths: list[str]) -> int:` that scans files and returns the number of violations.
   - Add it to `MANUAL_CHECKS` (e.g. `MANUAL_CHECKS = [check_membership_tests, check_<name>]`).
3. **Verify**: run `python code_quality/scripts/qa_report.py`. The total appears as `manual conventions` in `QA-REPORT.md` and `reports/qa.json`.
4. **Keep it cheap**: use regex/AST, skip generated/vendored trees, avoid slow scans.

## Membership tests

- Use a set (or tuple) for `x in {...}` membership checks instead of a list literal when there are 4 or more members. No ruff rule; manual convention.
