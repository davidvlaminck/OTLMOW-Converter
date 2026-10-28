"""Compute CRAP scores and change hot spots for a Python package.

CRAP (Change Risk Anti-Patterns) fuses cyclomatic complexity with test coverage:

    CRAP = complexity^2 * (1 - coverage / 100)^3 + complexity

At 100% coverage CRAP degenerates to the raw complexity, so it must be read
together with the complexity and coverage columns, never on its own.

Usage:
    python -m pytest --cov=<package> --cov-report=json:code_quality/reports/coverage.json
    python code_quality/scripts/crap_scores.py --coverage code_quality/reports/coverage.json --source <package>
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

QUALITY_DIR = Path(__file__).resolve().parent.parent
DEFAULT_COVERAGE_JSON = str(QUALITY_DIR / 'reports' / 'coverage.json')

NUMSTAT_COLUMNS = 3
CRAP_REFACTOR_NOW = 30.0
CRAP_MONITOR = 10.0

# Generated trees of this repository. They are rewritten by the daily
# auto_update workflow, so they are never refactored by hand and must not
# dominate the ranking. Adapt this list when the bundle is copied to another
# repository (see code_quality/README.md section 19).
DEFAULT_EXCLUDES = ()


@dataclass
class CrapRow:
    """One ranked code block."""

    file: str
    name: str
    block_type: str
    complexity: int
    coverage: float
    crap: float
    lineno: int


@dataclass
class HotSpot:
    """A file ranked by churn multiplied by complexity."""

    file: str
    commits: int
    lines_changed: int
    max_complexity: int
    score: float


def _run(command: list[str]) -> str:
    """Run a command and return stdout, or an empty string when it fails."""
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return ''
    if completed.returncode not in (0, 1):
        return ''
    return completed.stdout


def radon_command() -> list[str]:
    """Return the command prefix that runs radon.

    Radon is a dev-only tool and is not necessarily installed in the project
    virtualenv, so fall back to ``uvx radon`` when it is missing.
    """
    if shutil.which('radon'):
        return ['radon']
    if shutil.which('uvx'):
        return ['uvx', 'radon']
    return ['radon']


def radon_blocks(path: str) -> tuple[list[dict[str, Any]], str | None]:
    """Return the radon complexity blocks of a single file.

    Radon's JSON shape differs between "one file" and "many files" invocations,
    so both are normalised to a flat list of blocks here. A file that radon
    cannot parse is reported as an error instead of being silently skipped: a
    file that is invisible to the complexity gate is a hole in the gate.
    """
    raw = _run([*radon_command(), 'cc', '-j', '-s', path])
    if not raw.strip():
        return [], None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return [], 'invalid json output'
    blocks: list[dict[str, Any]] = []
    error: str | None = None
    for value in data.values():
        if isinstance(value, list):
            blocks.extend(value)
        elif isinstance(value, dict):
            # {"file.py": {"error": "invalid non-printable character U+FEFF ..."}}
            if 'error' in value:
                error = str(value['error'])
            else:
                for group in value.values():
                    if isinstance(group, list):
                        blocks.extend(group)
    return blocks, error


def find_unparsable(source: str, excludes: tuple[str, ...] = ()) -> list[tuple[str, str]]:
    """Return the files that radon cannot parse.

    A file that radon cannot read is invisible to the complexity gate and to
    the CRAP ranking: it is a hole in the gate, not a clean file. The usual
    cause is a byte order mark at the start of the file.
    """
    unparsable: list[tuple[str, str]] = []
    for root, _dirs, files in os.walk(source):
        for filename in sorted(files):
            if not filename.endswith('.py'):
                continue
            path = str(Path(root) / filename)
            if is_excluded(path, excludes):
                continue
            _blocks, error = radon_blocks(path)
            if error:
                unparsable.append((path, error))
    return unparsable


def load_coverage(coverage_json: str) -> dict[str, Any]:
    """Load a coverage.py JSON report."""
    with Path(coverage_json).open(encoding='utf-8') as handle:
        data: dict[str, Any] = json.load(handle)
    return data


def file_coverage(data: dict[str, Any], path: str) -> dict[str, Any]:
    """Return the coverage record of a single file, matching on suffix."""
    files: dict[str, dict[str, Any]] = data.get('files', {})
    if path in files:
        return files[path]
    for name, record in files.items():
        if name.endswith(path) or path.endswith(name):
            return record
    return {}


def coverage_for_range(record: dict[str, Any], first: int, last: int) -> float | None:
    """Percentage of executable lines covered inside a line range."""
    executed = set(record.get('executed_lines', []))
    missing = set(record.get('missing_lines', []))
    lines = executed | missing
    relevant = [line for line in lines if first <= line <= last]
    if not relevant:
        return None
    return 100.0 * sum(1 for line in relevant if line in executed) / len(relevant)


def is_excluded(path: str, excludes: tuple[str, ...]) -> bool:
    """Return whether a path is inside one of the excluded trees."""
    normalised = path.replace('\\', '/')
    return any(normalised.startswith(exclude.replace('\\', '/')) for exclude in excludes)


def compute_crap(coverage_json: str, source: str, excludes: tuple[str, ...] = ()) -> list[CrapRow]:
    """Rank every function of the source tree by CRAP score."""
    data = load_coverage(coverage_json)
    rows: list[CrapRow] = []
    for root, _dirs, files in os.walk(source):
        for filename in sorted(files):
            if not filename.endswith('.py'):
                continue
            path = str(Path(root) / filename)
            if is_excluded(path, excludes):
                continue
            record = file_coverage(data, path)
            if not record:
                continue
            blocks, _error = radon_blocks(path)
            for block in blocks:
                if block.get('type') == 'class':
                    continue
                first = int(block.get('lineno', 0))
                last = int(block.get('endline', first))
                coverage = coverage_for_range(record, first, last)
                if coverage is None:
                    continue
                complexity = int(block.get('complexity', 0))
                uncovered = (1.0 - coverage / 100.0) ** 3
                rows.append(
                    CrapRow(
                        file=path,
                        name=block.get('name', '<unknown>'),
                        block_type=block.get('type', 'function'),
                        complexity=complexity,
                        coverage=round(coverage, 1),
                        crap=round(complexity * complexity * uncovered + complexity, 1),
                        lineno=first,
                    )
                )
    rows.sort(key=lambda row: (-row.crap, row.file, row.lineno))
    return rows


def git_churn(source: str, since: str | None, excludes: tuple[str, ...] = ()) -> dict[str, dict[str, int]]:
    """Count commits and changed lines per file inside the source tree."""
    command = ['git', 'log', '--numstat', '--format=']
    if since:
        command += [f'--since={since}']
    command += ['--', source]
    raw = _run(command)
    churn: dict[str, dict[str, int]] = {}
    for line in raw.splitlines():
        parts = line.split('\t')
        if len(parts) != NUMSTAT_COLUMNS:
            continue
        added, deleted, path = parts
        if not added.isdigit() or not deleted.isdigit():
            continue
        if is_excluded(path, excludes):
            continue
        entry = churn.setdefault(path, {'commits': 0, 'lines_changed': 0})
        entry['lines_changed'] += int(added) + int(deleted)
    for path, entry in churn.items():
        commit_command = ['git', 'log', '--format=%H']
        if since:
            commit_command += [f'--since={since}']
        commit_command += ['--', path]
        commits = _run(commit_command)
        entry['commits'] = len([line for line in commits.splitlines() if line.strip()])
    return churn


def compute_hotspots(source: str, since: str | None, excludes: tuple[str, ...] = ()) -> list[HotSpot]:
    """Rank files by churn multiplied by their worst function complexity."""
    churn = git_churn(source, since, excludes)
    complexity_by_file: dict[str, int] = {}
    for root, _dirs, files in os.walk(source):
        for filename in sorted(files):
            if not filename.endswith('.py'):
                continue
            path = str(Path(root) / filename)
            if is_excluded(path, excludes):
                continue
            blocks, _error = radon_blocks(path)
            blocks = [b for b in blocks if b.get('type') != 'class']
            if blocks:
                complexity_by_file[path] = max(int(b.get('complexity', 0)) for b in blocks)
    hotspots: list[HotSpot] = []
    for path, entry in churn.items():
        if not path.endswith('.py'):
            continue
        complexity = complexity_by_file.get(path, 0)
        hotspots.append(
            HotSpot(
                file=path,
                commits=entry['commits'],
                lines_changed=entry['lines_changed'],
                max_complexity=complexity,
                score=round(entry['lines_changed'] * complexity, 1),
            )
        )
    hotspots.sort(key=lambda spot: (-spot.score, spot.file))
    return hotspots


def render_table(rows: list[CrapRow], limit: int) -> str:
    """Render the CRAP ranking as a markdown table."""
    if not rows:
        return '_No CRAP data available._\n'
    lines = [
        '| CRAP | Complexity | Coverage | Function | Location |',
        '|---:|---:|---:|---|---|',
    ]
    for row in rows[:limit]:
        status = 'refactor now' if row.crap > CRAP_REFACTOR_NOW else ('monitor' if row.crap > CRAP_MONITOR else 'ok')
        lines.append(
            f'| {row.crap} | {row.complexity} | {row.coverage} % | `{row.name}` '
            f'| `{row.file}:{row.lineno}` ({status}) |'
        )
    return '\n'.join(lines) + '\n'


def render_hotspots(spots: list[HotSpot], limit: int) -> str:
    """Render the hot-spot ranking as a markdown table."""
    if not spots:
        return '_No churn data available (is this a git repository?)._\n'
    lines = [
        '| Score | Commits | Lines changed | Max complexity | File |',
        '|---:|---:|---:|---:|---|',
    ]
    lines.extend(
        f'| {spot.score} | {spot.commits} | {spot.lines_changed} | {spot.max_complexity} | `{spot.file}` |'
        for spot in spots[:limit]
    )
    return '\n'.join(lines) + '\n'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--coverage', default=DEFAULT_COVERAGE_JSON, help='coverage.py JSON report')
    parser.add_argument('--source', default='otlmow_model', help='package directory to rank')
    parser.add_argument(
        '--exclude',
        default=','.join(DEFAULT_EXCLUDES),
        help=(
            'comma separated paths that are left out of the ranking: the '
            'generated trees of this repository, which are rewritten by the '
            'daily auto_update workflow and are never refactored by hand'
        ),
    )
    parser.add_argument(
        '--churn-since',
        default='3 years ago',
        help=(
            'git --since window for churn. Three years, not one: the commits of '
            'the last year in this repository are the automatic model updates, '
            'which only touch the generated trees.'
        ),
    )
    parser.add_argument('--top', type=int, default=25, help='rows to print')
    parser.add_argument(
        '--json',
        dest='json_out',
        default=str(QUALITY_DIR / 'reports' / 'crap.json'),
        help='also write the full result as JSON',
    )
    args = parser.parse_args(argv)

    if not Path(args.coverage).exists():
        return 2

    excludes = tuple(item.strip() for item in args.exclude.split(',') if item.strip())
    rows = compute_crap(args.coverage, args.source, excludes)
    spots = compute_hotspots(args.source, args.churn_since, excludes)

    print('## CRAP ranking\n')
    print(render_table(rows, args.top))
    print('## Change hot spots (churn x complexity)\n')
    print(render_hotspots(spots, args.top))

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        with Path(args.json_out).open('w', encoding='utf-8') as handle:
            json.dump(
                {
                    'crap': [asdict(row) for row in rows],
                    'hotspots': [asdict(spot) for spot in spots],
                },
                handle,
                indent=2,
            )
        print(f'wrote {args.json_out}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
