# Repository Guidelines

SUM Platform is a Django/Wagtail monorepo. The primary product is the installable
package in `core/sum_core`; everything else supports development, testing, or
scaffolding.

## Project Structure & Module Organization

- `core/sum_core/`: core platform apps and reusable features.
- `core/sum_core/test_project/`: test harness used by CI and local dev.
- `cli/`: `sum` CLI and its test suite.
- `clients/sum_client/`: canonical consumer example.
- `tests/`: repo-level tests for core and templates.
- `themes/`, `media/`: theme assets and fixtures.
- `boilerplate/`: generated project templates (not linted).
- `docs/`, `infrastructure/`, `scripts/`: documentation, ops tooling, helpers.

## Build, Test, and Development Commands

```bash
make install-dev   # editable install of core + dev tooling
make run           # migrate and run the test project
make lint          # ruff + mypy + black + isort checks
make format        # auto-format (black + isort)
make test          # full pytest suite with coverage
make test-fast     # CLI + themes slices
make db-up         # start local Postgres via docker-compose
```

## Configuration & Environment

- Use the repo-root `.venv` for all commands; activate it or call
  `./.venv/bin/python -m pytest` to ensure the right dependencies.
- Store local settings in a repo-root `.env` (DB credentials, secrets).
- For Postgres dev, set `DJANGO_DB_*` in `.env` and run `make db-up`.

## Coding Style & Naming Conventions

- Python 3.12+, 4-space indentation, Black line length 88.
- Linting: Ruff (`ruff check . --config pyproject.toml`), type-checking: mypy.
- Formatting: Black + isort (`make format`).
- Tests: `test_*.py` or `*_test.py`, classes `Test*`, functions `test_*`.

## Testing Guidelines

- Framework: pytest with pytest-cov; HTML coverage output in `htmlcov/`.
- Test locations: `tests/` and `cli/tests/` (configured in `pyproject.toml`).
- Use markers when appropriate (e.g., `unit`, `integration`, `requires_themes`).

## Commit & Pull Request Guidelines

- Commit style follows a conventional pattern: `type: summary` or
  `type(SCOPE): summary` (e.g., `fix:forms-atomic-rate-limit`).
- Integration branch is `develop`; PRs typically merge into `develop`.
- `main` is protected; release PRs go `develop -> main` and must pass
  the `lint-and-test` CI check.
- PRs should include a brief summary, testing notes, and links to relevant issues.
- GitHub CLI (`gh`) is authenticated here; agents should use it for PR creation,
  updates, and status checks instead of the web UI.

## Agent-Specific Notes

- This is a platform, not a demo project. Avoid implementing features only in the
test harness; core behavior should live in `core/sum_core/`. See
`docs/dev/AGENT-ORIENTATION.md` for the rationale.
- When unsure, the main documentation entrypoint is `docs/dev/DDD.md`.
