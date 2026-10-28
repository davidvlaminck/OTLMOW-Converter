# QA Report — otlmow_converter

> GENERATED FILE — produced by `code_quality/scripts/qa_report.py`.
> Do not edit by hand; edit the thresholds in the script instead.

Generated: 2026-10-28 · commit `967b6bb`

## Thresholds (gate)

| Metric | Threshold | Current | Status |
|---|---|---|---|
| ruff issues | ≤ 0 | 0 | 🟢 |
| files needing `ruff format` | ≤ 0 | crashed | 🔴 |
| mypy errors | ≤ 0 | 63 | 🔴 |
| test coverage (lines, owned code) | ≥ 80.0 | 86.0 % | 🟢 |
| test coverage (branches, owned code) | ≥ 75.0 | 76.6 % | 🟢 |
| max CRAP score | ≤ 6.0 | 474.4 | 🔴 |
| max cyclomatic complexity | ≤ 6 | 43 | 🔴 |
| bandit HIGH issues | ≤ 0 | 0 | 🟢 |
| dead code items | ≤ 0 | 0 | 🟢 |
| pip-audit vulnerabilities | ≤ 0 | 0 | 🟢 |
| god classes | ≤ 0 | 4 | 🔴 |
| files radon cannot parse | ≤ 0 | 0 | 🟢 |
| manual conventions | ≤ 0 | 1 | 🔴 |
| import cycles/architecture | ≤ — | not enabled | ⚪ |

## Tools not available

The metrics of these tools are **not measured**: a missing tool reports 0 findings, which looks like a clean run. Install them before trusting the numbers above.

- `lint-imports`

## Coverage split — generated vs hand-written

The gate above measures the **hand-written** code: that is the code a refactor touches. The whole package — generated model included — covers 86.0 % of the lines and 76.6 % of the branches. The generated model lifts the headline number and would hide the gap in the code we own.

| Code | Statements | Line % | Branches | Branch % |
|---|---:|---:|---:|---:|
| generated (excluded) | 0 | 0.0 % | 0 | 0.0 % |
| hand-written | 3613 | 86.0 % | 1556 | 76.6 % |

## Lead refactor target (highest CRAP)

`otlmow_converter/FileFormats/CsvImporter.py:611` → `_python_fallback_to_objects_async` — CRAP **474.4** — complexity **22** — coverage **2.2 %**

Verify with `code_quality/README.md` §7 before touching it: the behaviour must be pinned by a golden-file test first.

## Change hot spots (churn x complexity)

| Score | Commits | Lines changed | Max complexity | File |
|---:|---:|---:|---:|---|
| 74089 | 45 | 1723 | 43 | `otlmow_converter/DotnotationDictConverter.py` |
| 48789 | 39 | 1807 | 27 | `otlmow_converter/FileFormats/CsvImporter.py` |
| 44640 | 53 | 1440 | 31 | `otlmow_converter/FileFormats/ExcelImporter.py` |
| 33600 | 45 | 1680 | 20 | `otlmow_converter/OtlmowConverter.py` |
| 25312 | 54 | 1582 | 16 | `otlmow_converter/FileFormats/DotnotationTableConverter.py` |

## History

| Date | Coverage % | Branch % | Ruff | MyPy | Max CRAP | Max complexity | Result |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
| 2026-10-28 | 86.0 | 76.6 | 0 | 63 | 474.4 | 43 | red |
