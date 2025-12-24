# TEST-003 — Fix CI lint/typecheck failures on develop (post TEST-002)

## Context

After TEST-002, the GitHub Actions run associated with this work shows a failing “lint checks” step (exit code 2). ([GitHub][2])
We need develop to be reliably green so subsequent TEST tickets don’t stack uncertainty.

This task is deliberately scoped: **no refactors unless required to satisfy lint/typecheck**.

## Goal

* Restore **green CI** on develop by resolving the lint/typecheck failures triggered/exposed after TEST-002.
* Ensure the work lands as **clean, auditable commits** (no leftover unstaged changes).

## Scope / Non-goals

**In scope**

* Identify the exact failing lint/typecheck command(s) used in CI and reproduce locally.
* Fix the underlying issues (formatting, unused imports, typing mismatches, unsafe patterns).
* Where applicable, adjust the test fixtures/settings overrides to be lint/type-safe *without changing runtime behaviour*.

**Out of scope**

* Large rework of theme tests to reduce brittleness (we can do that later as its own ticket).
* Changing the overall CI pipeline structure (unless required to make the current checks run correctly).

## Plan (short)

1. Pull latest develop.
2. Reproduce CI lint/typecheck locally using the repo’s documented commands (Makefile / pre-commit / CI workflow).
3. Fix issues with minimal diffs.
4. Re-run lint/typecheck + `pytest -q`.
5. Commit cleanly and push.

## Checklist & Commands

> Use whatever the repo defines as canonical (Makefile targets, pre-commit, or docs). Don’t guess—confirm via local docs/config.

### 1) Precheck

```bash
git checkout develop
git pull
git status -sb
```

### 2) Reproduce CI locally

Run the *exact* lint/type commands CI runs (likely one of these patterns; confirm in repo):

```bash
make lint
make typecheck
pre-commit run --all-files
ruff check .
mypy core/sum_core/ --ignore-missing-imports
```

### 3) Fix (common suspects in this diff set)

Focus areas to inspect first:

* `tests/conftest.py` and any fixture that mutates Django settings. ([GitHub][1])
  Typical fixes:

  * Keep `TEMPLATES[0]["DIRS"]` as `list[str]` (cast Paths to strings at assignment time).
  * Keep `THEME_TEMPLATES_DIR` consistently typed (either always `Path` or always `str`) and align annotations accordingly.
  * Prefer pytest-django’s `settings` fixture (parameter injection) if your lint rules dislike direct `django.conf.settings` mutation.
* Any new/changed imports that are now unused, or ordering issues.

### 4) Prove it’s fixed

```bash
# Lint/type check must pass
make lint || ruff check .
make typecheck || mypy core/sum_core/ --ignore-missing-imports

# Runtime sanity: full suite
pytest -q
git status -sb
```

## Expected success signals

* CI run for the pushed commit is fully green (at minimum: lint checks pass). ([GitHub][2])
* Locally:

  * Lint/typecheck commands exit 0
  * `pytest -q` passes
  * `git status -sb` clean

## Stop / rollback triggers

* If fixing lint/typecheck requires behavioural changes to template resolution or theme loading order, **stop** and split into a separate ticket (we don’t want to “fix CI” by subtly reintroducing the original test/prod divergence).

## Record-keeping (required)

* Add a short note to `docs/ops-pack/what-broke-last-time.md` describing:

  * what CI check was failing,
  * root cause (e.g. typing mismatch / invalid settings injection),
  * prevention (e.g. cast Paths to `str` when writing Django settings).
    (Only if something non-trivial is discovered.)

## Git / commits (must be clean)

* Branch: `test/TEST-003-ci-green` (or similar).
* **One code commit** preferred:

  * `test(TEST-03): fix CI lint/typecheck`
* If docs need updating, a second commit is ok:

  * `docs(TEST-03): note CI lint failure + fix`
* Before finishing:

  * `git status -sb` shows clean working tree
  * commits pushed
  * include links to the commit + CI run in the task report

**Complexity:** Medium (depends on whether this is a quick ruff cleanup or a mypy/type alignment pass).

[1]: https://github.com/markashton480/sum_platform/commit/d0e89c7b41a79133b42080dfa034d67ed311162e "test(TEST-02): deterministic template resolution; fix settings leakage · markashton480/sum_platform@d0e89c7 · GitHub"
[2]: https://github.com/markashton480/sum_platform/actions/runs/20413663782/workflow "docs/ci(TEST-02): document deterministic loader fix · markashton480/sum_platform@97e07e8  · GitHub"
