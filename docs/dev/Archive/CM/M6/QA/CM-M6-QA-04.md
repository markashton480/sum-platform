# CM Task Ticket: CM-M6-QA-04 — Lint/Typecheck Contract Hardening

**Type:** Corrective Mission (QA)
**Milestone:** M6 / v0.6 stabilisation
**Owner role:** QA / Tooling + Type Safety
**Priority:** High (prevents repeat of “lint slipped through”)

## Objective

Make the repo’s **lint + typecheck pipeline deterministic and blocking**, so mypy/black/isort cannot pass locally yet fail later (or vice-versa), and so generated client scaffolds don’t poison checks.

## Context

- Mypy debt was addressed in CM-M6-QA-03 largely via boundary casts and small mechanical fixes.
- However, we still have evidence of inconsistent tooling behaviour (mypy scope differences, prior “Black sees no files”, duplicate module errors from `clients/*/tests`).
- We need a single authoritative “lint contract” that matches developer workflow and CI.

## Scope

**In scope**

- `pyproject.toml` lint/typecheck config (ruff, black, isort, mypy)
- `Makefile` targets (`make lint`, `make format`, etc.)
- Exclusions for generated scaffolds under `clients/` (especially `clients/*/tests`)
- Add/adjust CI guardrails if they exist in-repo (only config changes, no platform work)

**Out of scope**

- Refactoring application code for “perfect typing”
- Theme rendering work (this is QA/tooling only)

## Investigation checklist (must be written into CM report)

1. What exact commands does `make lint` run today (copy output)?
2. Does CI run the same commands (or different)?
3. Why did Black previously claim “No Python files” when run on `core cli tests`?
4. Which directories under `clients/` are:

   - checked into git vs generated at runtime by CLI tests
   - expected to be excluded from lint/typecheck

## Implementation tasks

1. **Mypy**

   - Decide and document the _canonical_ mypy invocation (recommendation: `mypy core cli tests --exclude '^clients/'` unless you want clients typed too).
   - Update `make lint` so mypy is **not** masked with `|| true`.
   - Add mypy config to avoid duplicate module problems:

     - exclude `^clients/` (or at minimum `^clients/.*/tests/`)
     - consider `explicit_package_bases = true` if appropriate.

2. **Black**

   - Confirm Black sees files when invoked on known python dirs.
   - Fix `pyproject` include/exclude so `black --check core cli tests` behaves as expected.

3. **isort**

   - Ensure `isort --check-only core cli tests` returns deterministic output (and matches pre-commit, if used).

4. **Ruff**

   - Resolve the deprecation warning by migrating top-level settings to `[tool.ruff.lint]` equivalents.

5. **Coverage warnings (optional but recommended)**

   - The CLI tests appear to generate temporary client folders (`clients/cli-check-*`). Exclude these from coverage collection/reporting so coverage isn’t trying to parse paths that no longer exist.

## Acceptance criteria

- `make lint`:

  - fails if mypy fails
  - black/isort run against intended python files (no “No Python files…” unless genuinely empty)
  - ruff deprecation warning removed

- Running locally and in CI produces the **same pass/fail result**.
- A short “Lint Contract” note is added to the CM report stating:

  - what dirs are in scope
  - what dirs are excluded and why (`clients/*` generated scaffolds)

## Verification steps

- Clean run:

  - `make lint`
  - `make test`

- Sanity checks:

  - `black --check core cli tests`
  - `isort --check-only core cli tests`
  - `mypy core cli tests --exclude '^clients/'` (or final canonical command)

## Deliverables

- CM report (`CM-M6-QA-04_followup.md`) including:

  - before/after snippets of `Makefile` + `pyproject.toml`
  - rationale for exclusions
  - proof logs of clean runs

---
