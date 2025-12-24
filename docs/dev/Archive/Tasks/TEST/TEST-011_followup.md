# TEST-011 Followup: CI Gate Split

## What Changed

Split the single `lint-and-test` job in `.github/workflows/ci.yml` into 4 separate jobs:

| Job           | Command            | Depends On |
| ------------- | ------------------ | ---------- |
| `lint`        | `make lint`        | –          |
| `test-full`   | `make test`        | `lint`     |
| `test-cli`    | `make test-cli`    | `lint`     |
| `test-themes` | `make test-themes` | `lint`     |

**Benefits:**

- Failures are localized to specific job names
- Test jobs run in parallel after lint passes (faster feedback)
- Each test job includes protected assets guard + theme check

## Housekeeping (per user request)

- Deleted all `*Zone.Identifier` files (Windows NTFS artifacts)
- Staged and committed the `docs/dev/Tasks/TEST/PR/` directory with TEST-010 evidence

---

## Local Verification Results

```
$ make lint
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 249 source files
black --check core cli tests
All done! ✅
230 files would be left unchanged.
isort --check-only core cli tests
Skipped 44 files
```

```
$ pytest -q
751 passed, 45 warnings in 188.22s (0:03:08)
```

```
$ make test-cli
16 passed, 7 warnings in 3.96s
```

```
$ make test-themes
69 passed, 7 warnings in 57.14s
```

---

## PR Link

https://github.com/markashton480/sum_platform/pull/new/test/TEST-011-ci-split-gates

---

## Commits

1. `docs(TEST-011): add task ticket` – Ticket + PR evidence directory
2. `ci(TEST-011): split CI into lint/full/cli/themes gates` – Workflow refactor
3. `docs(TEST-011): record CI gate split + results` – This followup
