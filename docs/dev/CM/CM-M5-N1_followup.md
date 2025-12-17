# **[CM-M5-N1 Follow-up] End-of-Milestone-5 Niggles & Release Hardening**

**Date:** 2025-12-16  
**Scope:** Correctness + clarity hardening only (no new features), per `docs/dev/CM/CM-M5-N1.md`.

---

## Summary of Outcomes

- **Health endpoint nuance implemented**: `/health/` now distinguishes **Celery not configured** vs **Celery configured but unreachable** exactly as specified, without affecting the critical DB/cache semantics.
- **Boilerplate completeness fixed**: the canonical boilerplate now includes a **real initial migration** for the client-owned `HomePage` app, so fresh clients don’t start in an ambiguous “blank tree” state.
- **Dependency pinning convergence validated**: boilerplate defaults to **git tag pinning** for `sum_core`, while still documenting monorepo dev mode separately.
- **Docs + CLI consistency sweep completed**: removed lingering ambiguity that could imply `test_project` is a production target; ensured the story across README/CLI/release workflow remains coherent.
- **Release readiness verified**: `make release-check` passes after the above fixes.

---

## 1) Health Endpoint Nuance (Ops Contract Hardening)

### Requirements Implemented

- **No Celery broker configured**:
  - Celery check returns `ok` with detail “Not configured (skipped)”
  - Overall status remains **`ok`**
- **Celery configured but unavailable**:
  - Celery check returns `fail`
  - Overall status becomes **`degraded`**
  - HTTP status remains **200**
- **Only DB/cache failures**:
  - Overall status becomes **`unhealthy`**
  - HTTP status becomes **503**

### Implementation Notes

- Updated core Celery health check to use a **lightweight broker reachability test** via `kombu.Connection` rather than relying on Celery control APIs.
  - This keeps behaviour deterministic across environments and avoids implicitly requiring running workers to consider the service “healthy”.
- Health HTTP status mapping remains centralized in `HealthCheckView` (only `unhealthy` → 503).

### Tests Added/Adjusted

- Added explicit unit coverage for:
  - Celery **skipped** when not configured
  - Celery **fail** when configured but unreachable
  - Overall status logic: celery failure → degraded; db/cache failure → unhealthy
- Release gate includes the full pytest run; these branches are now asserted explicitly.

### Files Touched (Health)

- `core/sum_core/ops/health.py`
- `tests/ops/test_health.py`

---

## 2) Client-Owned HomePage & Boilerplate Completeness

### Problem Resolved

Boilerplate shipped a client-owned `HomePage` model, but **did not ship the initial migration**, meaning new projects could require manual `makemigrations` before applying migrations cleanly. That’s exactly the kind of “invisible harness assumption” this CM is meant to eliminate.

### Fix

- Generated and committed `boilerplate/project_name/home/migrations/0001_initial.py`.
- Synced canonical boilerplate into the CLI’s bundled boilerplate copy so `sum init` produces consistent output in monorepo and standalone contexts.

### Files Touched (Boilerplate/HomePage)

- `boilerplate/project_name/home/migrations/0001_initial.py`
- `cli/sum_cli/boilerplate/project_name/home/migrations/0001_initial.py` (synced)

---

## 3) Dependency Pinning Convergence

### Confirmed Behaviour

- Canonical boilerplate pins `sum_core` via **git tag pinning only**, using:
  - `SUM_CORE_GIT_REF` placeholder in `requirements.txt`
  - `make release-set-core-ref REF=vX.Y.Z` to set it deterministically
- Monorepo dev mode remains explicitly documented as an optional override (editable install), but is not the default client story.

### Files Reviewed (and already consistent)

- `boilerplate/requirements.txt`
- `cli/sum_cli/boilerplate/requirements.txt`
- `docs/dev/release-workflow.md`
- `docs/dev/cli.md`

---

## 4) CLI & Docs Consistency Sweep

### Changes Made

- Updated `docs/dev/page-types-reference.md` to remove an example implying a hardcoded `home.HomePage` import path (which can suggest harness ownership).
- Updated repo `README.md` “Current Status” to reflect **Milestone 5** and to avoid claiming core scaffolding directories are stubs when they’re now real.

### Files Touched (Docs Sweep)

- `docs/dev/page-types-reference.md`
- `README.md`

---

## 5) Release-Readiness Verification

### Required Checks

- `make release-check` **passes** (runs `make lint`, `make test`, `make check-cli-boilerplate`).

### Notes / Known Non-Blocking Noise

- `mypy` currently reports a duplicate-module warning related to multiple `tests/` packages in the repo. The Makefile intentionally uses `mypy . || true`, so this does not block releases today.
  - This CM did **not** change that policy; it’s pre-existing repo configuration.

---

## Final State vs CM Acceptance Criteria

- **Health JSON semantics**: ✅ Matches required ok/degraded/unhealthy branches
- **Explicit tests per branch**: ✅ Added/confirmed
- **Boilerplate includes HomePage + initial migrations**: ✅ Added `0001_initial.py` and synced to CLI
- **Docs/code ownership clarity**: ✅ Reinforced (no implicit `test_project.home`)
- **Git tag pinning as the blessed client strategy**: ✅ Confirmed across boilerplate + docs
- **Release readiness gate**: ✅ `make release-check` passes



