# CM Task Ticket — CM-M6-QA-05 — CI Gate + Lint Contract Enforcement

**Type:** Corrective Mission (QA)
**Milestone:** M6 / v0.6 stabilisation
**Priority:** High (prevents regressions + “lint slipped through” repeats)
**Owner:** QA/Tooling Agent
**Related:** CM-M6-QA-04 (lint contract hardening)

---

## 1) Objective

Turn the **local lint/typecheck contract** into an **enforced, repeatable CI gate** so that:

- `make lint` + `make test` are **always executed** on PRs and on `main`
- CI starts from a clean state and doesn’t produce “ghost” failures (coverage DB corruption, generated scaffolds, etc.)
- The repo has a single, documented “truth” about what is linted/typed and what is excluded

---

## 2) Background / Context

CM-M6-QA-04 established a deterministic local contract:

- In-scope: `core/`, `cli/`, `tests/`
- Out-of-scope: `clients/` and boilerplate scaffolds (generated/transient; causes mypy duplicate module issues)

This CM is about _enforcement_ and _repeatability_.

---

## 3) Scope

### In scope

- Add GitHub Actions workflow(s) to run:

  - `make lint`
  - `make test`

- Ensure workflow uses a predictable environment:

  - Python version aligned with repo expectations
  - Dependency install that matches project (uv/pip/poetry—whatever repo actually uses)

- Reduce noise/flake:

  - Ensure coverage starts clean
  - Ensure generated scaffold dirs do not contaminate CI runs

- Update docs so the lint contract is explicit and discoverable

### Out of scope

- Refactoring application logic for typing “purity”
- Adding deployment workflows
- Changing theme rendering behavior (not a theming CM)
- Large test suite redesign

---

## 4) Non-negotiables (QA contract)

- CI must **fail** if `make lint` fails.
- CI must **fail** if `make test` fails.
- CI must run on:

  - PRs (targeting `main`)
  - pushes to `main`

- Every action taken must be traceable:

  - commit(s) reference this CM ID
  - report includes links/SHAs + a short “what changed / why” summary

---

## 5) Plan (short)

1. Inspect repo for existing CI config (confirm none / or replace minimal).
2. Create a minimal GitHub Actions workflow for Python that runs lint + tests.
3. Ensure dependency installation is correct and caches appropriately.
4. Ensure generated client scaffolds don’t break CI (esp. coverage + mypy).
5. Document the lint contract + CI gate in the appropriate docs/dev location.
6. Produce a clean audit trail with logs and before/after evidence.

---

## 6) Checklist & Commands (agent execution)

### A) Precheck (local)

Run locally and capture outputs in the report:

```bash
make lint
make test
python --version
pip --version
```

Also capture:

```bash
cat pyproject.toml | sed -n '1,220p'
cat Makefile
ls -la .github || true
```

### B) Add CI workflow

Create file:

`.github/workflows/ci.yml`

Workflow requirements:

- trigger: `pull_request` + `push` on `main`
- use `actions/checkout`
- setup python: use the project’s python version (if unclear, use 3.12.x consistent with your environment/output)
- install deps using the repo’s chosen method (must be derived from existing project files)

**If repo uses uv:** use uv install.
**If repo uses pip + requirements:** use `pip install -r ...`.
**If repo uses pyproject with editable install:** use `pip install -e ".[dev]"` or equivalent.

**Caching:**

- cache pip/uv wheels to speed runs (nice-to-have, not mandatory)

**Run steps:**

```bash
make lint
make test
```

### C) Coverage sanity

Your earlier runs showed `.coverage` parsing/db warnings. CI should be clean, but confirm:

- remove any persisted `.coverage` before running tests (CI should be fresh anyway, but add a defensive `rm -f .coverage`).
- if pytest-cov is configured to generate reports that choke on generated scaffolds, add a targeted exclusion in coverage config (prefer config, not ad-hoc ignores).

Suggested defensive step (only if needed):

```bash
rm -f .coverage
rm -rf .pytest_cache
```

### D) Generated scaffold isolation

If tests generate dirs like `clients/cli-check-*`, ensure:

- they don’t get committed (should already be true)
- they don’t poison coverage discovery/reporting

If needed, add `.coveragerc` or coverage config inside `pyproject.toml` to omit:

- `clients/cli-check-*`
- `clients/cli-theme-*`
- other transient CLI test output dirs

Do **not** broaden exclusions beyond transient dirs unless you can justify it.

### E) Docs update

Add a short “Lint & CI Contract” note in an appropriate place (choose whichever exists and matches current doc structure; likely under `docs/dev/` or `docs/ops-pack/` if that’s the home for operational truth).

Must include:

- Canonical commands: `make lint`, `make test`
- In-scope dirs: `core/ cli/ tests/`
- Out-of-scope dirs: `clients/` (generated/transient) + why
- How CI enforces it (workflow name, triggers)

---

## 7) Expected success signals

- GitHub Actions run shows:

  - ✅ `make lint` passes
  - ✅ `make test` passes

- Re-running locally still passes unchanged.
- No mypy duplicate module errors from scaffold dirs.
- No recurring coverage DB corruption warnings in CI output.
- Documentation clearly states the contract and the exclusions.

---

## 8) Stop / rollback triggers

Stop and report back (do not keep “fixing forward” blindly) if any of these occur:

- CI fails due to dependency install ambiguity (unclear package manager / missing lockfile)
- CI passes only by adding overly broad exclusions (e.g., excluding half the repo)
- New failures appear that indicate a hidden platform bug (not just tooling)
- The agent is tempted to re-scope lint targets beyond CM-M6-QA-04 without a documented reason

Rollback approach:

- revert workflow commit(s)
- revert coverage/config changes
- leave repo in pre-CM state but with report explaining why CI could not be added cleanly

---

## 9) Deliverables (mandatory)

### A) Work report

`CM-M6-QA-05_followup.md` must include:

- Summary of changes
- Links/SHAs to commits
- Final CI workflow file contents (or excerpt)
- Evidence:

  - local `make lint` / `make test` pass
  - CI run link or pasted success summary

- Any exclusions added + justification

### C) Code changes

- `.github/workflows/ci.yml` (or equivalent)
- any minimal config updates (`pyproject.toml` / `.coveragerc`) only if required

---

## 10) Notes / guidance for the agent

- Keep it minimal. The goal is **enforcement**, not perfection.
- Prefer fixing the root cause (scope + omit transient dirs) over “turning off coverage” or neutering tools.
- If you must add exclusions, make them **surgical** and documented.
- Assume this contract will be the basis for v1 hardening, so avoid hacks that will haunt you.
