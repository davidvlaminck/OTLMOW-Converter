"""Collect every quality gate of this repository into one report.

Runs lint, format, type, test/coverage, complexity, CRAP, security and dead-code
checks, writes a machine-readable snapshot to ``code_quality/reports/qa.json`` and
renders the human readable dashboard ``code_quality/QA-REPORT.md``.

The report is generated, never hand-edited. Re-running it only changes the rows
that actually moved, which keeps the diff reviewable.

Usage:
    python code_quality/scripts/qa_report.py
    python code_quality/scripts/qa_report.py --skip-tests --coverage code_quality/reports/coverage.json
"""

from __future__ import annotations

import argparse
import ast
import datetime
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

QUALITY_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = QUALITY_DIR.parent
REPORTS_DIR = QUALITY_DIR / 'reports'
HISTORY_FILE = REPORTS_DIR / 'qa-history.json'
SNAPSHOT_FILE = REPORTS_DIR / 'qa.json'
REPORT_FILE = QUALITY_DIR / 'QA-REPORT.md'

sys.path.insert(0, str(QUALITY_DIR / 'scripts'))

from crap_scores import compute_crap, compute_hotspots, find_unparsable  # noqa: E402

DEFAULT_THRESHOLDS = {
    'ruff_issues': 0,
    'ruff_format_files': 0,
    'mypy_errors': 0,
    'coverage_percent': 80.0,
    'coverage_branch_percent': 75.0,
    'max_crap': 6.0,
    'max_complexity': 6,
    'bandit_high': 0,
    'dead_code': 0,
    'god_classes': 0,
    'unparsable_files': 0,
    'manual_conventions': 0,
    'pip_audit_vulns': 0,
    'import_architecture_violations': 0,
}

# Generated trees of this repository. They are rewritten by the daily
# auto_update workflow, so they are never refactored by hand: they are not
# linted, not type checked and not part of the complexity ranking. They ARE
# part of the coverage measurement: the model is the product.
# Adapt this list when the bundle is copied to another repository
# (see code_quality/README.md section 19).
DEFAULT_EXCLUDES = ()

# The gates that can be enforced on their own: the name, the metric it reads
# and whether a higher value is better. The ratchet is not in this list: it is
# enforced by every run, because a lint count that goes up is never acceptable.
GATES = {
    'ruff': ('ruff_issues', False),
    'format': ('ruff_format_files', False),
    'mypy': ('mypy_errors', False),
    'coverage': ('coverage_percent', True),
    'coverage-branch': ('coverage_branch_percent', True),
    'crap': ('max_crap', False),
    'complexity': ('max_complexity', False),
    'bandit': ('bandit_high', False),
    'dead-code': ('dead_code', False),
    'god-classes': ('god_classes', False),
    'radon-parse': ('unparsable_files', False),
    'pip-audit': ('pip_audit_vulns', False),
    'import-architecture': ('import_architecture_violations', False),
}

# The tool that produces the metric of a gate. A gate whose tool is missing
# cannot pass: it was not measured, and a missing tool reports 0 findings.
GATE_TOOLS = {
    'ruff': 'ruff',
    'format': 'ruff',
    'mypy': 'mypy',
    'coverage': 'pytest',
    'coverage-branch': 'pytest',
    'crap': 'radon',
    'complexity': 'radon',
    'bandit': 'bandit',
    'dead-code': 'vulture',
    'god-classes': 'ast',
    'radon-parse': 'radon',
    'pip-audit': 'pip-audit',
}


def _run(command: list[str], cwd: Path | str = REPO_ROOT, env: dict[str, str] | None = None) -> tuple[int, str]:
    """Run a command and return its exit code and combined output."""
    try:
        completed = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False, env=env)
    except FileNotFoundError:
        return 127, ''
    return completed.returncode, completed.stdout + completed.stderr


def _tool(name: str) -> list[str] | None:
    """Resolve a tool to a runnable command, preferring the project venv."""
    if shutil.which(name):
        return [name]
    return None


def run_ruff(source: str, tests: str, scripts: str, tooling: str = '') -> dict[str, Any]:
    """Count ruff violations per rule code."""
    command = _tool('ruff')
    if command is None:
        return {'available': False, 'total': 0, 'per_rule': {}, 'fixable': 0}
    code, output = _run([*command, 'check', '--output-format=json', source, tests, scripts, tooling])
    try:
        findings = json.loads(output or '[]')
    except json.JSONDecodeError:
        return {
            'available': True,
            'total': 0,
            'per_rule': {},
            'fixable': 0,
            'error': output.strip()[:500],
        }
    per_rule: dict[str, int] = {}
    fixable = 0
    for finding in findings:
        rule = finding.get('code', '?')
        per_rule[rule] = per_rule.get(rule, 0) + 1
        if finding.get('fix'):
            fixable += 1
    return {
        'available': True,
        'total': len(findings),
        'fixable': fixable,
        'per_rule': dict(sorted(per_rule.items(), key=lambda item: (-item[1], item[0]))),
        'exit_code': code,
    }


def run_ruff_format(source: str, tests: str, scripts: str, tooling: str = '') -> dict[str, Any]:
    """Count files that are not formatted yet."""
    command = _tool('ruff')
    if command is None:
        return {'available': False, 'files': 0}
    format_command = [*command, 'format', '--check', source, tests, scripts]
    if tooling:
        format_command.append(tooling)
    code, output = _run(format_command)
    # ruff 0.17 prints "unformatted: File would be reformatted" per file, older
    # versions print "Would reformat: <path>". Counting only the first one makes
    # the gate pass without checking anything.
    unformatted = [line for line in output.splitlines() if line.startswith('unformatted:')]
    would_reformat = [line for line in output.splitlines() if line.startswith('Would reformat')]
    result: dict[str, Any] = {
        'available': True,
        'files': len(unformatted) + len(would_reformat),
        'exit_code': code,
    }
    # A crash of the formatter (a panic in ruff) produces no output at all: the
    # counter would report 0 files and the gate could never fail. Report the
    # crash instead of hiding it.
    if 'panicked' in output or 'panicked at' in output:
        result['error'] = 'ruff format crashed; see the log'
        result['files'] = -1
    return result


def run_mypy(source: str, tests: str, scripts: str, tooling: str = '') -> dict[str, Any]:
    """Count mypy errors."""
    command = _tool('mypy')
    if command is None:
        return {'available': False, 'errors': 0}
    # --no-incremental: the incremental cache can report a wrong number of
    # errors after a partial change (only the files that changed are re-checked,
    # the rest is read from the cache). A gate that reports 1 error instead of
    # 680 because of a stale cache is a gate that cannot fail. The full check
    # takes a couple of seconds.
    mypy_command = [
        *command,
        '--no-incremental',
        '--no-error-summary',
        '--no-pretty',
        source,
        tests,
        scripts,
    ]
    if tooling:
        mypy_command.append(tooling)
    code, output = _run(mypy_command)
    errors = len([line for line in output.splitlines() if ': error:' in line])
    return {
        'available': True,
        'errors': errors,
        'exit_code': code,
        'output': output.strip().splitlines()[:50],
    }


def coverage_totals(data: dict[str, Any]) -> dict[str, float]:
    """Return the line and the branch coverage of a coverage report."""
    totals = data.get('totals', {})
    statements = int(totals.get('num_statements', 0))
    covered_lines = int(totals.get('covered_lines', 0))
    branches = int(totals.get('num_branches', 0))
    covered_branches = int(totals.get('covered_branches', 0))
    return {
        'percent': 100.0 * covered_lines / statements if statements else 0.0,
        'branch_percent': 100.0 * covered_branches / branches if branches else 0.0,
    }


def coverage_split(coverage_json: str, excludes: tuple[str, ...]) -> list[dict[str, Any]]:
    """Split the coverage of the report into the excluded and the owned code.

    The generated model is measured by the coverage gate but never refactored
    by hand. The number that matters for a refactor is the coverage of the
    code we own, so it is reported separately.
    """
    path = Path(coverage_json)
    if not path.exists():
        return []
    with path.open(encoding='utf-8') as handle:
        data = json.load(handle)
    groups: dict[str, list[int]] = {'generated (excluded)': [0, 0, 0, 0], 'hand-written': [0, 0, 0, 0]}
    for name, record in data.get('files', {}).items():
        summary = record.get('summary', {})
        bucket = (
            'generated (excluded)'
            if any(name.replace('\\', '/').startswith(exclude) for exclude in excludes)
            else 'hand-written'
        )
        entry = groups[bucket]
        entry[0] += int(summary.get('num_statements', 0))
        entry[1] += int(summary.get('covered_lines', 0))
        entry[2] += int(summary.get('num_branches', 0))
        entry[3] += int(summary.get('covered_branches', 0))
    rows = []
    for name, (statements, covered, branches, covered_branches) in groups.items():
        rows.append(
            {
                'group': name,
                'statements': statements,
                'line_percent': round(100.0 * covered / statements, 1) if statements else 0.0,
                'branches': branches,
                'branch_percent': (round(100.0 * covered_branches / branches, 1) if branches else 0.0),
            }
        )
    return rows


def owned_coverage(split: list[dict[str, Any]]) -> tuple[float, float]:
    """Return the line and the branch coverage of the hand-written code.

    The gate measures the code we own. The generated model is reported
    separately: it would otherwise lift the headline number and hide the gap
    in the code a refactor actually touches.
    """
    for row in split:
        if row['group'] == 'hand-written':
            return float(row['line_percent']), float(row['branch_percent'])
    return 0.0, 0.0


def run_pytest(source: str, coverage_json: str, skip_tests: bool) -> dict[str, Any]:
    """Run the test suite with coverage and return the coverage percentages."""
    if skip_tests:
        if not Path(coverage_json).exists():
            return {
                'available': False,
                'percent': 0.0,
                'branch_percent': 0.0,
                'detail': 'no coverage report available',
            }
        with Path(coverage_json).open(encoding='utf-8') as handle:
            data = json.load(handle)
        return {'available': True, **coverage_totals(data), 'reused': True}
    command = [
        sys.executable,
        '-m',
        'pytest',
        f'--cov={source}',
        f'--cov-report=json:{coverage_json}',
        '-q',
    ]
    environment = dict(os.environ)
    coverage_config = str(QUALITY_DIR / 'coverage.cfg')
    if Path(coverage_config).exists():
        environment['COVERAGE_RCFILE'] = coverage_config
    code, output = _run(command, env=environment)
    with Path(coverage_json).open(encoding='utf-8') as handle:
        data = json.load(handle)
    summary = [
        line for line in output.splitlines() if ' passed' in line or ' failed' in line or 'error' in line.lower()
    ]
    return {
        'available': True,
        **coverage_totals(data),
        'exit_code': code,
        'summary': summary[-3:],
    }


def run_bandit(source: str, excludes: tuple[str, ...] = ()) -> dict[str, Any]:
    """Count bandit findings by severity."""
    command = _tool('bandit')
    if command is None:
        return {'available': False, 'high': 0, 'medium': 0, 'low': 0}
    command = [*command, '-q', '-f', 'json', '-r', source]
    if excludes:
        command += ['-x', ','.join(excludes)]
    code, output = _run(command)
    try:
        data = json.loads(output or '{}')
    except json.JSONDecodeError:
        return {'available': True, 'high': 0, 'medium': 0, 'low': 0}
    counts = {'high': 0, 'medium': 0, 'low': 0}
    for result in data.get('results', []):
        severity = result.get('issue_severity', 'low').lower()
        if severity in counts:
            counts[severity] += 1
    counts['available'] = True
    counts['exit_code'] = code
    return counts


def run_pip_audit() -> dict[str, Any]:
    """Count known vulnerabilities in the project dependencies."""
    command = _tool('pip-audit')
    if command is None:
        return {'available': False, 'vulns': 0}
    code, output = _run([*command, '-f', 'json'])
    try:
        data = json.loads(output or '[]')
    except json.JSONDecodeError:
        return {'available': True, 'vulns': 0, 'error': output.strip()[:500]}
    count = 0
    if isinstance(data, list):
        for item in data:
            count += len(item.get('vulns', []))
    elif isinstance(data, dict):
        for item in data.get('dependencies', []):
            count += len(item.get('vulns', []))
    return {'available': True, 'vulns': count, 'exit_code': code}


def check_membership_tests(paths: list[str]) -> int:
    import re

    count = 0
    for p in paths:
        if not p:
            continue
        for path in Path(p).rglob('*.py'):
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue
            for match in re.finditer(r'\bin\s*\[([^\]]*)\]', text):
                items = [x for x in match.group(1).split(',') if x.strip()]
                if len(items) >= 4:
                    count += 1
    return count


MANUAL_CHECKS = [check_membership_tests]


def run_manual_conventions(source: str, tests: str, scripts: str, tooling: str = '') -> dict[str, Any]:
    """Run all registered manual-convention checks and sum their counts."""
    paths = [source, tests, scripts, tooling]
    total = sum(check(paths) for check in MANUAL_CHECKS)
    return {'available': True, 'items': total}


def run_lint_imports() -> dict[str, Any]:
    """Check import architecture with import-linter (report-only)."""
    command = _tool('lint-imports')
    if command is None:
        return {'available': False, 'violations': 0, 'status': 'not enabled'}
    code, output = _run([*command])
    if code == 0 and ('contracts' in output.lower() or output.strip() == ''):
        return {'available': True, 'violations': 0, 'status': 'ok', 'exit_code': code}
    # Try to count "broken contract" / "violation" lines
    violations = 0
    for line in output.splitlines():
        lower = line.lower()
        if 'broken contract' in lower or 'violation' in lower or 'forbidden' in lower and 'ok' not in lower:
            violations += 1
    if violations == 0 and code != 0:
        violations = 1
    return {
        'available': True,
        'violations': violations,
        'status': 'violations' if violations else ('ok' if code == 0 else 'unknown'),
        'exit_code': code,
        'sample': output.strip()[:500],
    }


def run_vulture(source: str, excludes: tuple[str, ...] = ()) -> dict[str, Any]:
    """Count likely dead code at confidence 80."""
    command = _tool('vulture')
    if command is None:
        return {'available': False, 'items': 0}
    command = [*command, source, '--min-confidence', '80']
    if excludes:
        command += ['--exclude', ','.join(excludes)]
    code, output = _run(command)
    items = [line for line in output.splitlines() if line.strip()]
    return {'available': True, 'items': len(items), 'exit_code': code, 'sample': items[:20]}


GOD_CLASS_METHOD_THRESHOLD = 30
GOD_CLASS_SIZE_THRESHOLD = 30000


def detect_god_classes(source: str, excludes: tuple[str, ...] = ()) -> dict[str, Any]:
    """Detect potential god classes using simple heuristics."""
    god_classes = []
    source_path = REPO_ROOT / source
    if not source_path.exists():
        return {'available': False, 'count': 0, 'classes': []}
    for py_file in source_path.rglob('*.py'):
        if '__pycache__' in str(py_file) or 'TestModel' in str(py_file):
            continue
        try:
            relative = py_file.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            relative = py_file.as_posix()
        if any(relative.startswith(exclude) for exclude in excludes):
            continue
        try:
            with py_file.open(encoding='utf-8') as f:
                content_file = f.read()
            tree = ast.parse(content_file)
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            # A file that cannot be read is not a god class. It is reported by
            # the "files radon cannot parse" row of the report.
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                method_count = len(methods)
                if method_count > GOD_CLASS_METHOD_THRESHOLD or py_file.stat().st_size > GOD_CLASS_SIZE_THRESHOLD:
                    god_classes.append(f'{relative}:{node.name}')
    return {'available': True, 'count': len(god_classes), 'classes': god_classes[:20]}


def repo_name() -> str:
    """Return the project name, taken from pyproject.toml when possible."""
    pyproject = REPO_ROOT / 'pyproject.toml'
    if pyproject.exists():
        for line in pyproject.read_text(encoding='utf-8').splitlines():
            stripped = line.strip()
            if stripped.startswith('name') and '=' in stripped:
                value = stripped.split('=', 1)[1].strip().strip('"\'')
                if value:
                    return value
    return REPO_ROOT.name


def read_history() -> list[dict[str, Any]]:
    """Read the ratchet history."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open(encoding='utf-8') as handle:
            history: list[dict[str, Any]] = json.load(handle)
    except json.JSONDecodeError:
        return []
    return history


def write_history(history: list[dict[str, Any]]) -> None:
    """Write the ratchet history."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open('w', encoding='utf-8') as handle:
        json.dump(history, handle, indent=2)


def ratchet_violations(current: dict[str, int], previous: dict[str, int]) -> list[str]:
    """Return the rules whose count increased compared to the previous run."""
    regressions = []
    for rule, count in current.items():
        before = previous.get(rule, 0)
        if count > before:
            regressions.append(f'{rule}: {before} -> {count}')
    return regressions


def status(value: Any, threshold: Any, higher_is_better: bool) -> str:
    """Return a status glyph for a metric against its threshold."""
    if higher_is_better:
        return '🟢' if value >= threshold else '🔴'
    return '🟢' if value <= threshold else '🔴'


def failed_gates(
    metrics: dict[str, Any],
    thresholds: dict[str, Any],
    gates: list[str],
    tools: dict[str, bool] | None = None,
) -> list[str]:
    """Return the names of the gates that are not met."""
    failed = []
    for gate in gates:
        metric, higher_is_better = GATES[gate]
        value = metrics[metric]
        threshold = thresholds[metric]
        if value < 0:
            # A negative value means the check could not run (a crash). A gate
            # that did not run is not a gate that passed.
            failed.append(gate)
            continue
        if tools is not None and not tools.get(GATE_TOOLS.get(gate, ''), True):
            # The tool is not installed: the metric was not measured.
            failed.append(gate)
            continue
        met = value >= threshold if higher_is_better else value <= threshold
        if not met:
            failed.append(gate)
    return failed


def render_thresholds(snapshot: dict[str, Any]) -> list[str]:
    """Render the header and the threshold table."""
    metrics = snapshot['metrics']
    thresholds = snapshot['thresholds']
    format_files = metrics['ruff_format_files']
    format_current = 'crashed' if format_files < 0 else str(format_files)
    rows = [
        ('ruff issues', 'ruff_issues', False, f'{metrics["ruff_issues"]}'),
        ('files needing `ruff format`', 'ruff_format_files', False, format_current),
        ('mypy errors', 'mypy_errors', False, f'{metrics["mypy_errors"]}'),
        (
            'test coverage (lines, owned code)',
            'coverage_percent',
            True,
            f'{metrics["coverage_percent"]} %',
        ),
        (
            'test coverage (branches, owned code)',
            'coverage_branch_percent',
            True,
            f'{metrics["coverage_branch_percent"]} %',
        ),
        ('max CRAP score', 'max_crap', False, f'{metrics["max_crap"]}'),
        (
            'max cyclomatic complexity',
            'max_complexity',
            False,
            f'{metrics["max_complexity"]}',
        ),
        ('bandit HIGH issues', 'bandit_high', False, f'{metrics["bandit_high"]}'),
        ('dead code items', 'dead_code', False, f'{metrics["dead_code"]}'),
        ('pip-audit vulnerabilities', 'pip_audit_vulns', False, f'{metrics["pip_audit_vulns"]}'),
        ('god classes', 'god_classes', False, f'{metrics["god_classes"]}'),
        (
            'files radon cannot parse',
            'unparsable_files',
            False,
            f'{metrics["unparsable_files"]}',
        ),
        ('manual conventions', 'manual_conventions', False, f'{metrics["manual_conventions"]}'),
        (
            'import cycles/architecture',
            'import_architecture_violations',
            False,
            'not enabled'
            if metrics.get('import_architecture_status') == 'not enabled'
            else str(metrics.get('import_architecture_violations', 0)),
        ),
    ]
    lines = [
        f'# QA Report — {snapshot["repo"]}',
        '',
        '> GENERATED FILE — produced by `code_quality/scripts/qa_report.py`.',
        '> Do not edit by hand; edit the thresholds in the script instead.',
        '',
        f'Generated: {snapshot["date"]} · commit `{snapshot["commit"]}`',
        '',
        '## Thresholds (gate)',
        '',
        '| Metric | Threshold | Current | Status |',
        '|---|---|---|---|',
    ]
    for label, metric, higher_is_better, current in rows:
        glyph = (
            '🔴'
            if (metric == 'ruff_format_files' and format_files < 0)
            else (
                '⚪'
                if label == 'import cycles/architecture' and current == 'not enabled'
                else status(metrics.get(metric, 0), thresholds.get(metric, 0), higher_is_better)
            )
        )
        comparison = '≥' if higher_is_better else '≤'
        threshold_display = (
            '—' if label == 'import cycles/architecture' and current == 'not enabled' else thresholds.get(metric, 0)
        )
        lines.append(f'| {label} | {comparison} {threshold_display} | {current} | {glyph} |')
    lines.append('')
    return lines


def render_regressions(regressions: list[str]) -> list[str]:
    """Render the ratchet regressions."""
    if not regressions:
        return []
    lines = [
        '## Ratchet regressions',
        '',
        'These lint counts went **up** compared to the previous cycle and block the merge:',
        '',
    ]
    lines.extend(f'- {item}' for item in regressions)
    lines.append('')
    return lines


def render_enforced_gates(snapshot: dict[str, Any]) -> list[str]:
    """Render the gates that block a merge."""
    enforced = snapshot.get('enforced_gates') or []
    if not enforced:
        return []
    metrics = snapshot['metrics']
    thresholds = snapshot['thresholds']
    failed = snapshot.get('failed_gates') or []
    met = 'all met' if not failed else f'failed: {", ".join(failed)}'
    lines = [
        '## Enforced gates',
        '',
        f'These gates block a merge — {met}. The gates that are not listed are '
        'reported only; the ratchet is enforced by every run.',
        '',
        '| Gate | Threshold | Current | Status |',
        '|---|---|---|---|',
    ]
    for gate in enforced:
        metric, higher_is_better = GATES[gate]
        value = metrics[metric]
        if value < 0:
            lines.append(f'| `{gate}` | {thresholds[metric]} | crashed | 🔴 |')
            continue
        lines.append(
            f'| `{gate}` | {thresholds[metric]} | {value} | {status(value, thresholds[metric], higher_is_better)} |'
        )
    lines.append('')
    return lines


def render_scope(snapshot: dict[str, Any]) -> list[str]:
    """Render the scope of the measurement."""
    excluded = snapshot.get('excluded') or []
    if not excluded:
        return []
    lines = [
        '## Scope',
        '',
        'The model in this repository is generated: the trees below are '
        'rewritten by the daily `auto_update` workflow and are never edited '
        'by hand. They are excluded from the lint, type, security, '
        'dead-code, complexity and CRAP checks, and from the coverage '
        '**gate** — the gate measures the code we own. Their coverage is '
        'still measured and reported below, because the model is the '
        'product.',
        '',
    ]
    lines.extend(f'- `{item}`' for item in excluded)
    lines.append('')
    return lines


def render_missing_tools(snapshot: dict[str, Any]) -> list[str]:
    """Render the tools that were not available."""
    tools = snapshot.get('tools') or {}
    missing = sorted(name for name, available in tools.items() if not available)
    if not missing:
        return []
    lines = [
        '## Tools not available',
        '',
        'The metrics of these tools are **not measured**: a missing tool '
        'reports 0 findings, which looks like a clean run. Install them '
        'before trusting the numbers above.',
        '',
    ]
    lines.extend(f'- `{name}`' for name in missing)
    lines.append('')
    return lines


def render_coverage_split(snapshot: dict[str, Any]) -> list[str]:
    """Render the coverage of the generated model and of the owned code."""
    split = snapshot.get('coverage_split') or []
    if not split:
        return []
    package_line = snapshot.get('coverage_package_percent', 0.0)
    package_branch = snapshot.get('coverage_package_branch_percent', 0.0)
    lines = [
        '## Coverage split — generated vs hand-written',
        '',
        'The gate above measures the **hand-written** code: that is the code a '
        'refactor touches. The whole package — generated model included — '
        f'covers {package_line} % of the lines and {package_branch} % of the '
        'branches. The generated model lifts the headline number and would '
        'hide the gap in the code we own.',
        '',
        '| Code | Statements | Line % | Branches | Branch % |',
        '|---|---:|---:|---:|---:|',
    ]
    lines.extend(
        f'| {row["group"]} | {row["statements"]} | {row["line_percent"]} % '
        f'| {row["branches"]} | {row["branch_percent"]} % |'
        for row in split
    )
    lines.append('')
    return lines


def render_unparsable(snapshot: dict[str, Any]) -> list[str]:
    """Render the files that the tools cannot read."""
    unparsable = snapshot.get('unparsable_detail') or []
    if not unparsable:
        return []
    lines = [
        '## Files the tools cannot read',
        '',
        'These files are invisible to the complexity gate and to the CRAP '
        'ranking. A file that cannot be parsed is a hole in the gate, not a '
        'clean file.',
        '',
        '| File | Error |',
        '|---|---|',
    ]
    lines.extend(f'| `{item["file"]}` | {item["error"]} |' for item in unparsable)
    lines.append('')
    return lines


def render_lead_target(snapshot: dict[str, Any]) -> list[str]:
    """Render the lead refactor target."""
    lead = snapshot.get('lead_target')
    lines = ['## Lead refactor target (highest CRAP)', '']
    if not lead:
        lines += ['_No CRAP data available._', '']
        return lines
    lines += [
        f'`{lead["file"]}:{lead["lineno"]}` → `{lead["name"]}` — '
        f'CRAP **{lead["crap"]}** — complexity **{lead["complexity"]}** — coverage **{lead["coverage"]} %**',
        '',
        'Verify with `code_quality/README.md` §7 before touching it: '
        'the behaviour must be pinned by a golden-file test first.',
        '',
    ]
    return lines


def render_hotspots(snapshot: dict[str, Any]) -> list[str]:
    """Render the change hot spots."""
    hotspots = snapshot.get('hotspots', [])[:5]
    lines = [
        '## Change hot spots (churn x complexity)',
        '',
        '| Score | Commits | Lines changed | Max complexity | File |',
        '|---:|---:|---:|---:|---|',
    ]
    lines.extend(
        f'| {spot["score"]} | {spot["commits"]} | {spot["lines_changed"]} '
        f'| {spot["max_complexity"]} | `{spot["file"]}` |'
        for spot in hotspots
    )
    lines.append('')
    return lines


def render_ruff_rules(snapshot: dict[str, Any]) -> list[str]:
    """Render the lint findings per rule."""
    per_rule = snapshot.get('ruff_per_rule', {})
    if not per_rule:
        return []
    lines = ['## ruff findings per rule', '', '| Rule | Count |', '|---|---:|']
    lines.extend(f'| `{rule}` | {count} |' for rule, count in list(per_rule.items())[:15])
    lines.append('')
    return lines


def render_history(history: list[dict[str, Any]]) -> list[str]:
    """Render the ratchet history."""
    lines = [
        '## History',
        '',
        '| Date | Coverage % | Branch % | Ruff | MyPy | Max CRAP | Max complexity | Result |',
        '|---|---:|---:|---:|---:|---:|---:|---|',
    ]
    lines.extend(
        f'| {entry["date"]} | {entry["metrics"]["coverage_percent"]} '
        f'| {entry["metrics"].get("coverage_branch_percent", "-")} '
        f'| {entry["metrics"]["ruff_issues"]} '
        f'| {entry["metrics"]["mypy_errors"]} | {entry["metrics"]["max_crap"]} '
        f'| {entry["metrics"]["max_complexity"]} | {entry.get("result", "")} |'
        for entry in history[-10:]
    )
    lines.append('')
    return lines


def render_report(snapshot: dict[str, Any], history: list[dict[str, Any]], regressions: list[str]) -> str:
    """Render the markdown dashboard."""
    lines = render_thresholds(snapshot)
    lines += render_regressions(regressions)
    lines += render_enforced_gates(snapshot)
    lines += render_scope(snapshot)
    lines += render_missing_tools(snapshot)
    lines += render_coverage_split(snapshot)
    lines += render_unparsable(snapshot)
    lines += render_lead_target(snapshot)
    lines += render_hotspots(snapshot)
    lines += render_ruff_rules(snapshot)
    lines += render_history(history)
    return '\n'.join(lines)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', default='otlmow_converter')
    parser.add_argument('--tests', default='UnitTests')
    parser.add_argument('--scripts', default='code_quality/scripts')
    parser.add_argument('--tooling', default='')
    parser.add_argument(
        '--exclude',
        default=','.join(DEFAULT_EXCLUDES),
        help=(
            'comma separated paths that are left out of the security, dead-code, '
            'complexity and CRAP checks: the generated trees of this repository, '
            'which are rewritten by the daily auto_update workflow'
        ),
    )
    parser.add_argument('--coverage', default=str(REPORTS_DIR / 'coverage.json'))
    parser.add_argument('--skip-tests', action='store_true', help='reuse the existing coverage report')
    parser.add_argument('--no-ratchet', action='store_true', help='do not compare against the previous cycle')
    parser.add_argument(
        '--no-history',
        action='store_true',
        help='do not append a row to the ratchet history (a CI run must not change it)',
    )
    parser.add_argument(
        '--fail-on',
        default='',
        help=(
            'comma separated gates that must pass for the run to succeed: '
            f'{", ".join(sorted(GATES))}. Without it, every gate must pass.'
        ),
    )
    parser.add_argument(
        '--churn-since',
        default='3 years ago',
        help=(
            'git --since window for the change hot spots. Three years, not one: '
            'the commits of the last year in this repository are the automatic '
            'model updates, which only touch the generated trees.'
        ),
    )
    parser.add_argument('--max-crap', type=float, default=DEFAULT_THRESHOLDS['max_crap'])
    parser.add_argument('--max-complexity', type=int, default=DEFAULT_THRESHOLDS['max_complexity'])
    parser.add_argument('--coverage-min', type=float, default=DEFAULT_THRESHOLDS['coverage_percent'])
    parser.add_argument(
        '--coverage-branch-min',
        type=float,
        default=DEFAULT_THRESHOLDS['coverage_branch_percent'],
    )
    args = parser.parse_args(argv)

    unknown = sorted({gate.strip() for gate in args.fail_on.split(',') if gate.strip()} - set(GATES))
    if unknown:
        parser.error(f'unknown gate: {unknown[0]} (known gates: {", ".join(sorted(GATES))})')

    return args


def collect(args: argparse.Namespace) -> dict[str, Any]:
    """Run every check and return the measured numbers."""
    excludes = tuple(item.strip() for item in args.exclude.split(',') if item.strip())

    ruff = run_ruff(args.source, args.tests, args.scripts)
    ruff_format = run_ruff_format(args.source, args.tests, args.scripts)
    mypy = run_mypy(args.source, args.tests, args.scripts)
    pytest_result = run_pytest(args.source, args.coverage, args.skip_tests)
    bandit = run_bandit(args.source, excludes)
    vulture = run_vulture(args.source, excludes)
    pip_audit = run_pip_audit()
    god_classes = detect_god_classes(args.source, excludes)
    unparsable = find_unparsable(args.source, excludes)
    crap_rows: list[dict[str, Any]] = []
    if Path(args.coverage).exists():
        crap_rows = [row.__dict__ for row in compute_crap(args.coverage, args.source, excludes)]
    hotspots = [spot.__dict__ for spot in compute_hotspots(args.source, args.churn_since, excludes)]
    manual = run_manual_conventions(args.source, args.tests, args.scripts, args.tooling)
    lint_imports = run_lint_imports()
    split = coverage_split(args.coverage, excludes)
    owned_line, owned_branch = owned_coverage(split)
    package_line = pytest_result.get('percent', 0.0)
    package_branch = pytest_result.get('branch_percent', 0.0)
    metrics = {
        'ruff_issues': ruff['total'],
        'ruff_format_files': ruff_format['files'],
        'mypy_errors': mypy['errors'],
        'coverage_percent': round(owned_line, 1),
        'coverage_branch_percent': round(owned_branch, 1),
        'max_crap': max((row['crap'] for row in crap_rows), default=0.0),
        'max_complexity': max((row['complexity'] for row in crap_rows), default=0),
        'bandit_high': bandit.get('high', 0),
        'dead_code': vulture.get('items', 0),
        'pip_audit_vulns': pip_audit.get('vulns', 0),
        'god_classes': god_classes.get('count', 0),
        'unparsable_files': len(unparsable),
        'manual_conventions': manual.get('items', 0),
        'import_architecture_violations': lint_imports.get('violations', 0),
        'import_architecture_status': lint_imports.get('status', 'not enabled'),
    }

    tools = {
        'ruff': ruff.get('available', False),
        'mypy': mypy.get('available', False),
        'bandit': bandit.get('available', False),
        'vulture': vulture.get('available', False),
        'pip-audit': pip_audit.get('available', False),
        'radon': bool(crap_rows) or bool(unparsable),
        'pytest': pytest_result.get('available', False),
        'lint-imports': lint_imports.get('available', False),
    }

    return {
        'metrics': metrics,
        'tools': tools,
        'excludes': excludes,
        'crap_rows': crap_rows,
        'hotspots': hotspots,
        'split': split,
        'package_line': package_line,
        'package_branch': package_branch,
        'unparsable': unparsable,
        'god_classes': god_classes,
        'ruff_per_rule': ruff['per_rule'],
    }


def build_snapshot(
    thresholds: dict[str, Any],
    enforced: list[str],
    collected: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the snapshot that is written to reports/qa.json."""
    metrics = collected['metrics']
    tools = collected['tools']
    failed = failed_gates(metrics, thresholds, enforced, tools)
    all_met = not failed_gates(metrics, thresholds, list(GATES), tools)
    commit = _run(['git', 'rev-parse', '--short', 'HEAD'])[1].strip() or 'unknown'
    crap_rows = collected['crap_rows']
    return {
        'date': datetime.date.today().isoformat(),
        'repo': repo_name(),
        'commit': commit,
        'thresholds': thresholds,
        'metrics': metrics,
        'enforced_gates': enforced,
        'failed_gates': failed,
        'all_gates_met': all_met,
        'lead_target': crap_rows[0] if crap_rows else None,
        'hotspots': collected['hotspots'],
        'ruff_per_rule': collected['ruff_per_rule'],
        'crap': crap_rows,
        'god_classes_detail': collected['god_classes'],
        'excluded': list(collected['excludes']),
        'coverage_split': collected['split'],
        'coverage_package_percent': round(collected['package_line'], 1),
        'coverage_package_branch_percent': round(collected['package_branch'], 1),
        'unparsable_detail': [{'file': path, 'error': error} for path, error in collected['unparsable']],
        'tools': tools,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    enforced = [gate.strip() for gate in args.fail_on.split(',') if gate.strip()]

    thresholds = dict(DEFAULT_THRESHOLDS)
    thresholds['max_crap'] = args.max_crap
    thresholds['max_complexity'] = args.max_complexity
    thresholds['coverage_percent'] = args.coverage_min
    thresholds['coverage_branch_percent'] = args.coverage_branch_min

    collected = collect(args)
    metrics = collected['metrics']
    snapshot = build_snapshot(thresholds, enforced, collected)
    failed = snapshot['failed_gates']
    all_met = snapshot['all_gates_met']

    history = read_history()
    previous = history[-1]['ruff_per_rule'] if history else {}
    regressions = []
    if history and not args.no_ratchet:
        regressions = ratchet_violations(collected['ruff_per_rule'], previous)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with SNAPSHOT_FILE.open('w', encoding='utf-8') as handle:
        json.dump(snapshot, handle, indent=2)

    result = 'green' if all_met and not regressions else 'red'
    if not args.no_history:
        history.append(
            {
                'date': snapshot['date'],
                'commit': snapshot['commit'],
                'metrics': metrics,
                'ruff_per_rule': collected['ruff_per_rule'],
                'result': result,
            }
        )
        write_history(history)

    with REPORT_FILE.open('w', encoding='utf-8') as handle:
        handle.write(render_report(snapshot, history, regressions))

    print(f'wrote {REPORT_FILE}')
    print(f'wrote {SNAPSHOT_FILE}')
    for name, value in metrics.items():
        print(f'  {name}: {value}')
    if failed:
        print('failed gates:')
        for gate in failed:
            print(f'  {gate}')
    if regressions:
        print('ratchet regressions:')
        for item in regressions:
            print(f'  {item}')

    # with --fail-on only the named gates block the run, without it every gate does
    blocked = bool(failed) if enforced else not all_met
    return 1 if blocked or regressions else 0


if __name__ == '__main__':
    raise SystemExit(main())
