# Work Order

**Title:** `WO: CLI v2 Enhanced Architecture`

---

## Parent

---

## Branch

| Branch        | Target          |
| ------------- | --------------- |
| `feature/cli` | `release/0.6.0` |

```bash
git checkout release/0.6.0
git checkout -b feature/cli
git push -u origin feature/cli
```

---

## Objective

- [ ] Transform 9-step manual project setup into single `sum init --full` command
- [ ] Deliver fully-functioning themed site ready for testing in <2 minutes
- [ ] Eliminate AI agent friction (no manual intervention required)
- [ ] Maintain backward compatibility with v1 `sum init` behavior
- [ ] Achieve >80% test coverage for new modules
- [ ] Ensure 100% idempotency (all operations can be safely re-run)

---

## Scope

### In Scope

- Enhanced `sum init` command with `--full`, `--quick`, `--ci`, `--no-prompt`, `--skip-*`, `--run` flags
- New `sum run` command with port conflict handling
- Enhanced `sum check` command with additional validations
- Setup modules: venv, deps, database, auth, seed, orchestrator
- Utility modules: environment, output, prompts, django, validation
- `seed_homepage` management command in sum_core
- Configuration system (SetupConfig dataclass)
- Exception hierarchy for error handling
- Comprehensive test suite

### Out of Scope

- Per-client seed presets (Phase 4 - future work)
- Database backend selection (SQLite vs PostgreSQL)
- Parallel operation optimization
- `sum init --undo` rollback functionality
- Setup operation logging to file

---

## Subtasks

| #   | Title                        | Branch                              | Status |
| --- | ---------------------------- | ----------------------------------- | ------ |
| 1   | Foundation Utilities         | `task/cli/issue-N-foundation-utils` | 🔲     |
| 2   | Django Execution & Config    | `task/cli/issue-N-django-config`    | 🔲     |
| 3   | Environment Setup Modules    | `task/cli/issue-N-env-setup`        | 🔲     |
| 4   | Database & Auth Modules      | `task/cli/issue-N-db-auth`          | 🔲     |
| 5   | seed_homepage Command        | `task/cli/issue-N-seed-homepage`    | 🔲     |
| 6   | Seeding & Orchestrator       | `task/cli/issue-N-orchestrator`     | 🔲     |
| 7   | Enhanced Init Command        | `task/cli/issue-N-enhanced-init`    | 🔲     |
| 8   | Run Command & Enhanced Check | `task/cli/issue-N-run-check`        | 🔲     |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

_Note: `N` will be replaced with actual issue numbers after creation_

---

## Merge Plan

### Order

```
                    ┌─────────────────────────────────────────────────┐
                    │              MERGE DEPENDENCY GRAPH              │
                    ├─────────────────────────────────────────────────┤
                    │                                                 │
                    │   #CLI-001 Foundation Utilities                 │
                    │        │                                        │
                    │        ▼                                        │
                    │   #CLI-002 Django & Config                      │
                    │        │                                        │
                    │   ┌────┴────┐                                   │
                    │   ▼         ▼                                   │
                    │ #CLI-003  #CLI-004   #CLI-005 (parallel)        │
                    │ Env Setup DB & Auth  seed_homepage              │
                    │   │         │            │                      │
                    │   └────┬────┴────────────┘                      │
                    │        ▼                                        │
                    │   #CLI-006 Seeding & Orchestrator               │
                    │        │                                        │
                    │        ▼                                        │
                    │   #CLI-007 Enhanced Init                        │
                    │        │                                        │
                    │        ▼                                        │
                    │   #CLI-008 Run & Check                          │
                    │                                                 │
                    └─────────────────────────────────────────────────┘
```

1. **#CLI-001** — establishes base utilities all modules depend on
2. **#CLI-002** — Django execution layer, depends on #CLI-001
3. **#CLI-003** — Venv/deps setup, depends on #CLI-002
4. **#CLI-004** — Database/auth setup, depends on #CLI-002 (can parallel with #CLI-003)
5. **#CLI-005** — sum_core command, independent of CLI (can parallel with #CLI-003/#CLI-004)
6. **#CLI-006** — Orchestrator integrates all setup modules, depends on #CLI-003, #CLI-004, #CLI-005
7. **#CLI-007** — Init command uses orchestrator, depends on #CLI-006
8. **#CLI-008** — Polish layer, depends on #CLI-007

### Hot Files

| File                        | Owner                        | Notes                             |
| --------------------------- | ---------------------------- | --------------------------------- |
| `cli/sum/utils/__init__.py` | #CLI-001, #CLI-002           | Export consolidation across tasks |
| `cli/sum/setup/__init__.py` | #CLI-003, #CLI-004, #CLI-006 | Export consolidation across tasks |
| `cli/sum/commands/init.py`  | #CLI-007                     | Complete rewrite, single owner    |
| `cli/sum/cli.py`            | #CLI-007, #CLI-008           | Command registration              |

---

## Affected Paths

```
cli/
├── sum/
│   ├── __init__.py
│   ├── cli.py                    # Modified: register new commands
│   ├── config.py                 # New: SetupConfig dataclass
│   ├── exceptions.py             # New: Exception hierarchy
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── init.py               # Modified: enhanced with new flags
│   │   ├── check.py              # Modified: enhanced validation
│   │   └── run.py                # New: sum run command
│   ├── setup/
│   │   ├── __init__.py           # New
│   │   ├── orchestrator.py       # New
│   │   ├── venv.py               # New
│   │   ├── deps.py               # New
│   │   ├── database.py           # New
│   │   ├── seed.py               # New
│   │   └── auth.py               # New
│   └── utils/
│       ├── __init__.py           # New
│       ├── environment.py        # New
│       ├── prompts.py            # New
│       ├── output.py             # New
│       ├── django.py             # New
│       └── validation.py         # New
└── tests/
    ├── test_init.py              # Modified: new flag tests
    ├── test_check.py             # Modified: new validation tests
    ├── test_run.py               # New
    ├── test_orchestrator.py      # New
    ├── test_venv.py              # New
    ├── test_prompts.py           # New
    └── fixtures/

core/sum_core/
└── management/
    └── commands/
        └── seed_homepage.py      # New
```

---

## Verification

### After Each Task Merge

```bash
git checkout feature/cli
git pull origin feature/cli
make lint && make test
```

### Before Feature PR

```bash
git fetch origin
git rebase origin/release/0.6.0
make lint && make test

# Full integration test
sum init test-project --full --ci
cd clients/test-project
sum check
curl http://127.0.0.1:8000/ | grep "Welcome"
```

---

## Risk

**Level:** Medium

**Factors:**

- Orchestrator is central coordinator — errors cascade to all dependent operations
- Cross-component work (sum_core ↔ CLI) for seed_homepage command
- Mode detection complexity (monorepo vs standalone execution)
- Many integration points in enhanced init command

**Mitigation:**

- Comprehensive unit tests for each module before integration
- Integration tests run after each task merge
- Clear error handling with recovery suggestions
- Idempotent operations allow safe re-runs
- CI mode (`--ci`) for automated testing with fail-fast behavior

**Key Design Decisions:**

- **Monorepo root detection:** All path resolution walks upward to find repo root (markers: `core/` + `boilerplate/`), ensuring commands work from any directory within the monorepo
- **Python interpreter:** Django commands ALWAYS run under the project's `.venv/bin/python`, regardless of execution mode. Mode only affects PYTHONPATH injection.
- **Idempotency definition:** "Safe to re-run" means no corruption, no duplicates, no misleading output. Superuser creation checks by username first; `.env.local` only written when credentials are actually set.
- **"<2 minutes" target:** Assumes warm pip cache. First-time installs may take longer due to network.

---

## Labels

- [ ] `type:work-order`
- [ ] `component:cli`
- [ ] `risk:medium`
- [ ] Milestone: `v0.6.0`

---

## Definition of Done

- [ ] All 8 subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] `sum init project --full --ci` creates working project in <2 minutes
- [ ] `sum run` works from anywhere in monorepo
- [ ] `sum check` catches common configuration issues
- [ ] All error messages have clear next steps
- [ ] Test coverage >80% for new modules
- [ ] Documentation updated (README.md, cli.md, CONTRIBUTING.md)
- [ ] Feature branch merged to release branch (PR approved)
- [ ] Version Declaration updated
