# CM Task Report: CM-M6-QA-05 — CI Gate + Lint Contract Enforcement

**Date:** 2025-12-18  
**Status:** ✅ Complete

---

## Summary

This CM established an **enforced, repeatable CI gate** using GitHub Actions to run `make lint` and `make test` on all PRs targeting `main` and on all pushes to `main`. The lint contract from CM-M6-QA-04 is now codified in CI.

---

## Precheck Baseline

### Local Environment

```
Python 3.12.3
pip 25.3
```

### `make lint` — PASS

```
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 225 source files
black --check core cli tests
All done! ✨ 🍰 ✨
210 files would be left unchanged.
isort --check-only core cli tests
Skipped 40 files
```

### `make test` — PASS

```
709 passed, 45 warnings in 178.76s
Coverage: 82%
```

### Existing CI

No `.github/` directory existed prior to this CM.

---

## Implementation

### A) GitHub Actions Workflow

**File:** `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint-and-test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('core/pyproject.toml', 'pyproject.toml') }}
          restore-keys: |
            ${{ runner.os }}-pip-

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ./core[dev]

      - name: Clean stale artifacts
        run: |
          rm -f .coverage
          rm -rf .pytest_cache
          rm -rf clients/cli-check-* clients/cli-theme-*

      - name: Run lint checks
        run: make lint

      - name: Run tests
        run: make test
```

**Key decisions:**

| Feature                                 | Rationale                                                             |
| --------------------------------------- | --------------------------------------------------------------------- |
| `concurrency` with `cancel-in-progress` | Prevents zombie runs on rapid pushes                                  |
| Python 3.12                             | Matches repo's `requires-python = ">=3.12"` and local dev environment |
| `pip install -e ./core[dev]`            | Matches `make install-dev` flow exactly                               |
| Clean stale artifacts step              | Prevents `.coverage` DB corruption and transient scaffold pollution   |
| Separate lint/test steps                | Clear failure isolation in CI logs                                    |

### B) Documentation Update

**File:** `docs/dev/hygiene.md`

Added a comprehensive **Lint & CI Contract** section documenting:

- Canonical commands (`make lint`, `make test`, `make format`)
- In-scope directories: `core/`, `cli/`, `tests/`
- Out-of-scope directories: `clients/`, `boilerplate/` (with rationale)
- CI enforcement: workflow triggers, gate behavior

### C) Coverage Configuration

**No changes required.** The existing `pyproject.toml` already correctly omits:

```toml
[tool.coverage.run]
omit = [
    # ...
    "clients/*",
]
```

This covers all transient scaffold directories (`cli-check-*`, `cli-theme-*`, etc.).

---

## Verification

### Local Post-Implementation

```bash
$ make lint
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 225 source files
black --check core cli tests
All done! ✨ 🍰 ✨
210 files would be left unchanged.
isort --check-only core cli tests
Skipped 40 files
```

✅ **PASS**

### CI Run

The workflow will trigger on the next push to `main` or PR. The workflow file is syntactically valid and follows GitHub Actions best practices.

---

## Files Changed

| File                       | Action                                         |
| -------------------------- | ---------------------------------------------- |
| `.github/workflows/ci.yml` | **Created** — CI workflow                      |
| `docs/dev/hygiene.md`      | **Updated** — Added Lint & CI Contract section |

---

## Exclusions Added

No new exclusions were added. The existing configuration already correctly excludes:

- `clients/*` — transient CLI scaffolds
- `boilerplate/*` — template placeholders

---

## Expected Success Signals (Post-Merge)

Once merged to `main`:

- [ ] GitHub Actions shows ✅ for `make lint`
- [ ] GitHub Actions shows ✅ for `make test`
- [ ] No mypy duplicate module errors from scaffold dirs
- [ ] No coverage DB corruption warnings in CI output
- [ ] PRs now show required checks for lint and test

---

## Notes

- The workflow uses `actions/checkout@v4`, `actions/setup-python@v5`, and `actions/cache@v4` (current stable versions as of 2025-12).
- Pip caching is keyed on both `pyproject.toml` files to invalidate on dep changes.
- The `concurrency` block prevents duplicate runs on rapid-fire pushes (common during PR iteration).

---

_Signed-off by QA / Tooling Engineer_
