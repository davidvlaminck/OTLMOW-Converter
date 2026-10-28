# Python anti-patterns

Banned constructs, each mapped to the ruff rule that detects it. Every rule listed
here is enabled in `pyproject.toml` — verify with:

```bash
ruff rule T201        # shows the rule and its selector
ruff check --select T201 <src>
```

If a rule below does not fire, the selector is missing from `[tool.ruff.lint] select`
in `pyproject.toml`.

---

## Correctness and safety

| Anti-pattern | Why it hurts | Ruff rule | Fix |
|---|---|---|---|
| Bare `except:` | swallows `KeyboardInterrupt` and `SystemExit` | `E722` | `except Exception:` |
| `except Exception: pass` | hides every failure, including real bugs | `S110` | log and re-raise, or narrow the exception |
| `except Exception:` around a whole block | converts a crash into wrong data | `BLE001` | catch the specific exception |
| `eval(` / `exec(` | arbitrary code execution | `S307` / `S302` | `ast.literal_eval`, or a parser |
| `assert` in library code | stripped when Python runs with `-O` | `S101` | raise an exception |
| `== True` / `== False` | breaks for numpy/pandas truthiness | `E712` | `if value:` / `if not value:` |
| `type(x) == int` | misses subclasses | `E721` | `isinstance(x, int)` |
| Mutable default argument (`def f(x=[])`) | shared mutable state across calls | `B006` | `def f(x=None):` then `x = x or []` |
| `getattr(o, "attr")` with a constant | hides typos | `B009` | `o.attr` |
| `setattr(o, "attr", v)` with a constant | hides typos | `B010` | `o.attr = v` |
| `raise ValueError("...")` without `from` | loses the original cause | `B904` | `raise MyError(...) from exc` |
| Bare string in `raise` | not a dedicated exception type | `TRY003` | define an exception class |
| `try:` / `except` / `else` mix-up | the `else` branch is skipped wrongly | `TRY300` | use `try/except/else` correctly |
| `import *` | namespace pollution, hides origin of names | `F403` / `F401` | explicit imports |
| Relative imports beyond the package root | breaks packaging | `TID252` | absolute imports |
| `os.path` string concatenation | breaks on Windows paths | `PTH` | `pathlib.Path` |

## Logging

| Anti-pattern | Why it hurts | Ruff rule | Fix |
|---|---|---|---|
| `print()` in library code | breaks logging, breaks capture, pollutes stdout | `T201` | `logging.getLogger(__name__)` |
| f-string in a logging call | eagerly formats, even when the level is disabled | `G004` | lazy `%`-formatting: `log.debug("x %s", x)` |
| `logging.warn(...)` | deprecated in favour of `logging.warning` | `G010` | `logging.warning(...)` |
| Root logger calls (`logging.info(...)`) | uses the root logger instead of a module logger | `LOG015` | `logger = logging.getLogger(__name__)` |
| `exc_info=True` outside an `except` block | raises `SyntaxError` at runtime | `LOG014` | move it inside the handler |
| `logging.info(..., extra=...)` clashing with a LogRecord attribute | raises at runtime | `G101` | rename the extra key |

## Typing and API

| Anti-pattern | Why it hurts | Ruff rule | Fix |
|---|---|---|---|
| Implicit optional (`x: Path = None`) | the annotation lies about the type | `RUF013` | `x: Optional[Path] = None` |
| Missing type parameters (`def f(x: list)`) | the element type is unknown | `UP006` / `PYI` | `def f(x: list[str])` |
| Mutable class attribute | shared between instances | `RUF012` | `ClassVar`, or set it in `__init__` |
| Unnecessary `object` base | pre-3 style inheritance | `UP004` | drop the base class |
| Deprecated `typing` import | `typing.List` instead of `list` | `UP035` / `UP006` | use the builtin generics |
| Global variable mutated in a function | hidden shared state | `PLW0602` | pass it as a parameter |

## Design smells worth flagging in review

These are not ruff rules — they are review prompts, listed here so they are not
forgotten.

| Smell | Signal | Fix |
|---|---|---|
| Function with 12+ arguments | `PLR0913` / `PLR0917` | group into an options object |
| Function with 10+ returns | `PLR0911` | extract per-case helpers |
| Duplicate sync/async implementation | `jscpd` | one implementation, one wrapper |
| Speculative `**kwargs` | `ARG001` | remove the unused pass-through |
| Silent `return None` / `return []` on failure | review every early return | raise, or return a result object |
| Unbounded `while True` retry | review every loop | add a maximum attempt count |
| Function that only calls other functions | review | inline it, or it is a naming layer |

---

## Exceptions to the rules

`# noqa: RULE` is allowed **with a reason on the same line**:

```python
result = subprocess.run(cmd, shell=True)  # noqa: S602 - required for the legacy batch job
```

A `# noqa` without a reason is a review rejection.

See `MANUAL-CONVENTIONS.md` for conventions that have no ruff rule (e.g.
membership tests). That file is the append-only log for new manual rules.
