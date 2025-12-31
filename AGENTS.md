# Repository Guidelines

SUM Platform is a Django/Wagtail monorepo. The primary product is the installable package in `core/sum_core`; everything else supports development, testing, or scaffolding.

## Project Structure

```
core/sum_core/           # Core platform (the product)
core/sum_core/test_project/  # Test harness for CI
cli/                     # sum CLI tool
clients/sum_client/      # Example consumer
tests/                   # Repo-level tests
themes/, media/          # Theme assets
boilerplate/             # Generated project templates (not linted)
docs/, scripts/          # Documentation, helpers
```

## Commands

```bash
make install-dev   # Editable install of core + dev tooling
make run           # Migrate and run test project
make lint          # Ruff + mypy + Black + isort
make format        # Auto-format
make test          # Full pytest suite
make test-fast     # Quick gate (CLI + themes)
make db-up         # Start PostgreSQL (Docker)
make db-info       # Check database status
```

## PostgreSQL Testing

Some tests require PostgreSQL. By default, tests use SQLite.

```bash
# Run full test suite with PostgreSQL
DJANGO_DB_NAME=sum_db \
DJANGO_DB_USER=sum_user \
DJANGO_DB_PASSWORD=sum_password \
DJANGO_DB_HOST=localhost \
SUM_TEST_DB=postgres \
make test
```

- `SUM_TEST_DB=postgres` — Forces PostgreSQL for pytest

## Git Model (5-Tier)

```
main                              # Production, tagged
  ↑
develop                           # Stable integration
  ↑
release/X.Y.0                     # Version staging
  ↑
feature/<scope>                   # Feature integration
  ↑
feature/<scope>/<seq>-<slug>      # Task branches
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Version | `release/X.Y.0` | `release/0.7.0` |
| Feature | `feature/<scope>` | `feature/forms` |
| Task | `feature/<scope>/<seq>-<slug>` | `feature/forms/001-definition` |
| Hotfix | `hotfix/<slug>` | `hotfix/security-fix` |

### PR Flow

| From | To | Strategy |
|------|----|----------|
| Task branch | Feature branch | Squash |
| Feature branch | Release branch | Merge --no-ff |
| Release branch | Develop | Squash |
| Develop | Main | Squash |

### Commits

Conventional format: `type(scope): summary`

```
feat(forms): add FormDefinition snippet
fix(leads): correct email validation
chore(deps): update wagtail to 7.1
```

### Rules

- ❌ Never commit directly to `main`, `develop`, or `release/*`
- ❌ Never force-push tags
- ✅ Always run `make lint && make test` before PR

## Issue Hierarchy

```
Milestone: v0.7.0
├── Version Declaration     ←→  release/0.7.0
│   ├── Work Order          ←→  feature/<scope>
│   │   └── Subtask         ←→  feature/<scope>/<task>
```

## Definition of Done

Subtask is Done when:
- Acceptance criteria met
- `make lint && make test` passes
- PR merged to feature branch
- `Model Used` field set + `model:*` label applied

## Code Style

- Python 3.12+, Black line length 88
- Linting: Ruff, type-checking: mypy
- Tests: `test_*.py`, classes `Test*`, functions `test_*`

## Agent Notes

- This is a **platform**, not a demo project
- Core behavior belongs in `core/sum_core/`, not just test harness
- Use `gh` CLI for PR creation and status checks

## Key Docs

- `docs/dev/GIT_STRATEGY.md` — Branch model
- `docs/dev/planning/PROJECT-PLANNING-GUIDELINES.md` — Issue workflow
- `docs/HANDBOOK.md` — Platform guide
