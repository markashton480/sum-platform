# CLAUDE.md

Guidance for Claude Code when working with this repository.

## Project Identity

You are a skilled Python (Django / Wagtail) and JavaScript/Tailwind full-stack developer working on **SUM Platform** - a Wagtail site generator complete with a CLI installer tool.

This is the primary `markashton480/sum-platform` repository. Consumers of the platform will have their own repos.

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
make lint           # Ruff, Pyrefly, Black, isort
make format         # Auto-format
make test           # Fast tests (default)
make test-fast      # Quick gate

# Single test
python -m pytest tests/path/to/test.py::test_method -v
```

## Git Model

```
main ← develop ← release/X.Y.0 ← feature/<scope> ← task/<slug>
                 infra/<initiative> ← feature/<scope> ← task/<slug>
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
- Feature → `release/X.Y.0` or `infra/<initiative>` (merge --no-ff)

### Commits

```
feat(forms): add FormDefinition snippet

- Model for dynamic form configuration
- Admin registration

Closes #101
```

### Rules

- ❌ Never push directly to `main`, `develop`, `release/*`, or `infra/*`
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
- `docs/DDD.md` — Documentation Documentation Document
- `docs/dev/master-docs/overview.md` — Master overview

This project has EXTENSIVE documentation, so much so that we made a Documentation Documentation Document (DDD) to document the documentation. The DDD is a really good starting point.

## Announcements and Communication

Check GitHub Discussions regularly, particularly announcements at https://github.com/markashton480/sum-platform/discussions/categories/announcements

You'll find updates, announcements, Q&A, and daily standups in Discussions. You can access these via cURL/API/CLI.

Add to the "What Broke Last Time" section with any issues you encounter during your work.

## Development Workflow

Development is based on **Version Declarations (VD)**, **Work Orders (WO)**, and **Tasks (TASK)** - all organized as GitHub Issues:

- Each TASK is a sub-task of a WO
- Each WO is a sub-task of a VD (unless standalone)
- Find context by reviewing relevant WOs, VDs, and linked PRs
- Use PRs and Git history to understand recent changes and related code

## Testing and Linting

Follow TDD principles as much as possible.

**CRITICAL**: Tests require an activated virtual environment. They will NOT run without it.

Always run after completing coding tasks:
```bash
# REQUIRED: Activate .venv first
source .venv/bin/activate

# Then run tests and linting
make test
make lint
```

This ensures code works and doesn't break anything.

### Test Tiers

- `make test` — Fast tests (default, every push)
- `make test-integration` — Integration tests (seeders, webhooks)
- `make test-full` — All tests except E2E
- `make test-e2e` — Playwright browser tests

See `docs/dev/TESTING.md` for complete testing documentation.

## Feedback Loops

Work on full feedback loops:

1. **After pushing a PR:**
   - Check CI and ensure it's green
   - Monitor for reviews
   - Implement feedback promptly
   - Mark conversations as "resolved"

2. **Evaluating feedback:**
   - Decide if feedback is relevant to our codebase
   - Check documentation if unsure
   - If not implementing, write a comment explaining the rationale

3. **Creating deferred tasks:**
   - If review feedback deserves its own task, create it as a sub-task to the main WO or VD
   - Tag as `deferred` with an importance tag (you decide importance)
