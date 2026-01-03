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
make test          # Fast tests (default)
make test-fast     # Quick gate (CLI + themes)
```

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
- You'll be set up as a contributor on any appropriate repos (mostly `markashton480/sum-platform`) but consumers of the platform will have their own repos; we also have org `linteldigital` which may be used for projects, so double check if unclear in repo/task

## Announcements

You should regularly check GitHub Discussions, particularly announcements (`https://github.com/markashton480/sum-platform/discussions/categories/announcements`) and your GitHub notifications. You can do both by cURL/API/CLI. You'll find updates, announcements, Q&A, daily standups in Discussions, so check it out and feel free to contribute.

You should also add to the "What Broke Last Time" section with any issues you encountered during your work.

## Development Workflow

Our development is based on Version Declarations (VD), Work Orders (WO) and Tasks (TASK) and they're all organized as GitHub Issues. Each task will be a sub-task of a WO, and each WO will be a sub-task of a VD unless they're standalone tasks. You'll be able to understand a lot of context by finding relevant WOs, VDs and the linked PRs. You can use PRs and Git history to understand recent changes, and other relevant code.

## Testing and Linting

Try to follow TDD principles as much as possible.

**CRITICAL**: Tests require an activated virtual environment. They will NOT run without it.

Always run after completing coding tasks:
```bash
# REQUIRED: Activate .venv first
source .venv/bin/activate

# Then run tests and linting
make test
make lint
```

**For Agents**: Use the existing `.venv/` - no installation needed, just activation.

### Test Tiers

- `make test` — Fast tests (default, every push)
- `make test-integration` — Integration tests (seeders, webhooks)
- `make test-full` — All tests except E2E
- `make test-e2e` — Playwright browser tests

See `docs/dev/TESTING.md` for complete testing documentation.

## Feedback Loops

You work on full feedback loops: when pushing a PR, always check CI and ensure it's green, check for reviews and implement the feedback. Ensure that conversations are marked as "resolved". Decide whether feedback needs to be implemented or not, whether it's relevant to our codebase. Check documentation if you're unsure. Always write a comment explaining the rationale behind why not implemented if you choose not to implement.

If review feedback makes a suggestion which deserves its own task, please create it as a sub-task to the main WO or VD and tag as `deferred` with an importance tag - you should decide how important it is.

## Documentation

This project has extensive documentation, so much so that we made a Documentation Documentation Document (DDD) to document the documentation. This is a really good starting point (`docs/DDD.md`), we also have `docs/dev/master-docs/overview.md` and a Handbook (`docs/HANDBOOK.md`). You'll find more repo-specific info in `CLAUDE.md` / `AGENTS.md` (as appropriate).

## Key Docs

- `docs/GIT_STRATEGY.md` — Branch model
- `docs/PROJECT-PLANNING-GUIDELINES.md` — Issue workflow
- `docs/dev/HANDBOOK.md` — Platform guide
