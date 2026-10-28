## 19. Using this bundle in another repository

The bundle is designed to be copied. This section is the checklist for doing that.

### Copy as-is, no edits

| File | Why it is portable |
|---|---|
| `code_quality/scripts/crap_scores.py` | every path is derived from `__file__`; the package, the coverage report, the excluded trees and the churn window are CLI arguments. Falls back to `uvx radon` when radon is not installed. |
| `code_quality/scripts/qa_report.py` | same; the project name in the report title is read from `pyproject.toml`. The thresholds in `DEFAULT_THRESHOLDS` are the ones of the repository it was written for — every one of them has a CLI flag (`--max-crap`, `--max-complexity`, `--coverage-min`, `--coverage-branch-min`), or you edit the constant. |
| `code_quality/PY-ANTI-PATTERNS.md` | documentation only, no repository specifics. |

### Copy and edit these values

| File | What to change |
|---|---|
| `code_quality/coverage.cfg` | `source = <package>` and the `omit` list (drop the vendored-model entry if there is none). |
| `code_quality/ci/quality.yml` | the four path arguments (`otlmow_model`, `UnitTests`, `model_update`), the Python version, the tool pins (`ruff==…`, `mypy<2`), the `--exclude` list and the gates that block the merge in the `--fail-on` step. |
| `code_quality/README.md` | §4.1/§4.4/§6 config blocks; delete §18 (the measured baseline) and §20 (the test analysis of this repository) and write your own. |
| `pyproject.toml` | `[tool.ruff*]`, `[tool.mypy]`: the `src`, `extend-exclude` and `per-file-ignores` paths. |
| `DEFAULT_EXCLUDES` in both scripts | the generated trees of the repository. A repository without generated code sets it to an empty list. |

### Do not copy

`code_quality/QA-REPORT.md` and `code_quality/reports/` — they are generated.
Running the script recreates them.

### Verify after copying

```bash
python -m pytest --cov=<package> --cov-report=json:code_quality/reports/coverage.json -q
python code_quality/scripts/crap_scores.py --source <package> --exclude <generated trees>
python code_quality/scripts/qa_report.py --source <package> --tests <tests> --tooling <tooling>
```

The first two commands must print a CRAP table; the third must print the ten
metrics and write `QA-REPORT.md`. If `radon` is missing, the CRAP table comes back
empty — install it (`uv pip install radon`) or let the script use `uvx radon`. The
report lists the tools that were not available: a missing tool is reported as a
failed gate, never as a clean run.

---
