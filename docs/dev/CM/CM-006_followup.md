## **[CM-006 Follow-up]: Resolve M5-001 red flags (health contract, HomePage ownership, docs & tests alignment)**

**Task**: `docs/dev/CM/CM-006.md`  
**Status**: ✅ Complete  
**Date**: 2025-12-16  

---

## Summary

This change set removes the three “shape risks” called out in CM-006 by:

- Making the `/health/` contract explicit and **authoritatively enforced in `sum_core.ops`**
- Clarifying that **HomePage is client-owned** (with `sum_client` as the canonical example) while keeping `test_project` as a harness-only fixture
- Aligning docs + consumer tests to the new health contract and the “real client consumer” narrative

---

## 1) Health endpoint contract (core + consumer tests)

### Decision (authoritative contract)

- **Overall JSON `status` values**: `ok`, `degraded`, `unhealthy`
- **HTTP mapping**:
  - `ok` -> **200**
  - `degraded` -> **200**
  - `unhealthy` -> **503**

### Severity rules (baseline)

- **Critical**: DB, cache  
  If either fails -> overall `unhealthy` (503)
- **Non-critical**: Celery  
  If it fails (and is configured) -> overall `degraded` (200)

### Implementation notes

- The contract is documented directly in `core/sum_core/ops/health.py` module docstring.
- The status→HTTP mapping is centralized in `core/sum_core/ops/views.py` so consumer projects don’t re-implement semantics.

### Tests updated

- Core integration tests now assert:
  - `degraded` -> 200
  - `unhealthy` -> 503
- `sum_client` integration tests mirror the same expectations and stay focused on **shape + contract**, not internal check ordering.

---

## 2) HomePage ownership + duplication guardrails

### Decision (source of truth)

- **HomePage is client-owned** for M5 (content layer belongs to the consumer project).
- `sum_client` is the canonical example implementation: `clients/sum_client/sum_client/home/models.py`.
- `core/sum_core/test_project/home/` remains **harness-only** (dev/CI validation of templates/blocks).

### What changed

- README no longer presents the harness HomePage as the platform’s canonical HomePage location.
- Page types docs now explicitly call out client ownership and point to the canonical example.

---

## 3) Documentation alignment (“stop implying test harness is the product”)

### What changed

- README now includes a dedicated **Quick Start for `clients/sum_client/`** as the recommended “real client consumer” path, while still preserving `test_project` as the contributor harness.
- Wiring inventory health docs now match the new `/health/` contract and real-world monitoring expectations.

---

## 4) Dependency pinning clarity

### What changed

- `clients/sum_client/requirements.txt` keeps the monorepo editable install for development, but now documents the intended **external client** approach:
  - pin `sum-core==X.Y.Z`, or
  - pin to a git tag/commit (if distributing via git)

---

## Files changed

### Core (`sum_core`)

- `core/sum_core/ops/health.py`
- `core/sum_core/ops/views.py`
- `tests/ops/test_health.py`

### Consumer (`sum_client`)

- `clients/sum_client/tests/test_health.py`
- `clients/sum_client/requirements.txt`

### Docs

- `README.md`
- `docs/dev/WIRING-INVENTORY.md`
- `docs/dev/page-types-reference.md`

---

## Verification

- Core health tests:
  - `pytest tests/ops/test_health.py`
- `sum_client` health tests (run from `clients/sum_client/`):
  - `pytest tests/test_health.py`



