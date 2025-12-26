# CLAUDE.md

Guidance for Claude Code when working with this repository.

## What This Is

SUM Platform is a **reusable core platform** for lead-focused websites. It is NOT a single Django site.

**Primary product:** `core/sum_core/` — an installable Django/Wagtail package.

Everything else supports it:
- `test_project/` — pytest harness
- `boilerplate/` — starter template
- `cli/` — scaffolding tool
- `themes/` — visual rendering

**Rule:** If your change only works inside test_project, it's incomplete.

## Commands

```bash
source .venv/bin/activate

make install-dev    # Install core + dev deps
make run            # Migrate and start server
make lint           # Ruff, mypy, Black, isort
make format         # Auto-format
make test           # Full pytest suite
make test-fast      # Quick gate

# Single test
python -m pytest tests/path/to/test.py::test_method -v
```

## Git Model

```
main ← develop ← release/X.Y.0 ← feature/<scope> ← feature/<scope>/<task>
```

### Your Branch

```bash
# For a subtask under a Work Order
git checkout feature/<scope>
git pull origin feature/<scope>
git checkout -b feature/<scope>/<seq>-<slug>
```

### Your PR Target

- Task → `feature/<scope>` (squash)
- Feature → `release/X.Y.0` (merge --no-ff)

### Commits

```
feat(forms): add FormDefinition snippet

- Model for dynamic form configuration
- Admin registration

Closes #101
```

### Rules

- ❌ Never push directly to `main`, `develop`, or `release/*`
- ❌ Never skip `make lint && make test`
- ✅ Always include `Closes #NNN` in commits/PRs

## Code Reviews

When reviewing PRs:

1. **Check scope** — Does PR match acceptance criteria?
2. **Check boundaries** — Any files outside declared scope?
3. **Check other issues** — Is missing functionality planned elsewhere?

Don't complain about missing features unless explicitly required AND not planned.

## Architecture

### Core-Client Pattern

- `sum_core` installed via pip from git tags
- Client projects are thin shells consuming core
- Each client has its own database

### Theme System

- Block **definitions** in `core/sum_core/blocks/`
- Block **templates** in `themes/<theme>/templates/`

### Lead Pipeline

1. Form POST → `/forms/submit/`
2. Lead saved to Postgres (atomic)
3. Celery queues async side effects

## Key Modules

| Module | Purpose |
|--------|---------|
| `sum_core.pages` | Page models |
| `sum_core.blocks` | StreamField blocks |
| `sum_core.leads` | Lead persistence |
| `sum_core.forms` | Form handling |
| `sum_core.navigation` | Header/footer/CTA |
| `sum_core.branding` | SiteSettings |

## Key Docs

- `docs/GIT_STRATEGY.md` — Branch model
- `docs/PROJECT-PLANNING-GUIDELINES.md` — Issue workflow
- `docs/RELEASE_RUNBOOK.md` — Release process
- `docs/dev/HANDBOOK.md` — Platform guide
