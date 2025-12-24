# TEST-015 Follow-up

## Summary
- Audited CLI tests for init/check usage and unsafe cleanup patterns.
- Added isolated CLI env fixtures and theme snapshots to enforce safe output boundaries.
- Refactored CLI tests to use tmp output roots and verify source immutability.
- Added explicit CLI safety regression tests and registered the regression marker.

## Audit
- Files audited: `cli/tests/conftest.py`, `cli/tests/test_theme_init.py`, `cli/tests/test_cli_init_and_check.py`, `cli/tests/test_themes_command.py`.
- `sum init` usage: `cli/tests/test_theme_init.py`, `cli/tests/test_cli_init_and_check.py`.
- `sum check` usage: `cli/tests/test_cli_init_and_check.py`.
- File writes/deletes: init creates client projects; tests write minimal project files in tmp paths; CSS file rename in compiled CSS failure test.
- Unsafe cleanup patterns: no `shutil.rmtree` or `Path.unlink` found under `cli/tests/`.
- Repo-relative working directory reliance: themes list tests used repo root CWD; init tests relied on CWD + repo paths.

## Changes
- Added `isolated_theme_env`, `apply_isolated_theme_env`, and `theme_snapshot` helpers to `cli/tests/conftest.py` for consistent CLI isolation and snapshotting.
- Updated `cli/tests/test_theme_init.py` and `cli/tests/test_cli_init_and_check.py` to:
  - Use `SUM_CLIENT_OUTPUT_PATH` as the working directory.
  - Assert output boundaries and source theme immutability after init.
  - Verify source theme files (at least `theme.json`) remain present.
- Updated `cli/tests/test_themes_command.py` to run under isolated env rather than repo root.
- Added `cli/tests/test_cli_safety.py` regression coverage for init boundaries, source immutability (themes + boilerplate), cleanup guardrails, and repeated init safety.
- Registered `regression` marker in `pyproject.toml`.

## Commands run
- `rg --files cli/tests`
  Output: listed CLI test files.
- `git grep -n "shutil\.rmtree" cli/tests || true`
  Output: no matches.
- `git grep -n "unlink(" cli/tests || true`
  Output: no matches.
- `source .venv/bin/activate && make lint`
  Output: ruff + mypy succeeded; timed out while running Black.
- `source .venv/bin/activate && black --check core cli tests`
  Output: timed out.
- `source .venv/bin/activate && make test`
  Output: 755 passed (warnings about Django URLField scheme, pytest collection, and Sentry deprecations).
- `source .venv/bin/activate && make test-cli`
  Output: 19 passed (Django URLField scheme warnings).
- `source .venv/bin/activate && make test-themes`
  Output: 69 passed (Django URLField scheme warnings).
- `source .venv/bin/activate && make test-templates`
  Output: 4 passed (Django URLField scheme warnings).

## Tests not run
- None.

## Caveats
- `make lint` did not complete because `black --check` timed out.
