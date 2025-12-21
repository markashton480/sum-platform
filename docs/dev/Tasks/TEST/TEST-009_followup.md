# TEST-009 Follow-up — CLI/Themes Test Slices Fix

**Date:** 2025-12-21  
**Status:** ✅ Complete

## Summary

Fixed the `ModuleNotFoundError: No module named 'tests.utils'` that prevented running CLI tests in isolation via `pytest cli/tests`. Added Makefile targets for convenient slice-based test execution.

## Root Cause

When running `pytest cli/tests` from repo root (without the full test collection), Python's `sys.path` did not include the repo root directory. This meant the `tests.utils.safe_cleanup` module—located at `tests/utils/safe_cleanup.py`—was not importable.

The full test suite (`pytest` or `make test`) worked because pytest's root-level collection ensured the repo root was on `sys.path`.

## Fix Applied

### A) CLI conftest.py import path fix

**File:** `cli/tests/conftest.py`

Added a minimal `sys.path` insertion before the problematic import:

```python
import sys
from pathlib import Path

# Ensure repo root is on sys.path so 'tests.utils' is importable
# when running `pytest cli/tests` in isolation (sliced runs).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pytest  # noqa: E402

from tests.utils.safe_cleanup import create_filesystem_sandbox  # noqa: E402
```

The `# noqa: E402` comments suppress Ruff's "module level import not at top of file" warnings, which are expected and intentional here.

### B) Makefile test slice targets

**File:** `Makefile`

Added three new targets:

```makefile
test-cli: ## Run CLI test slice only
	python -m pytest cli/tests -q

test-themes: ## Run themes test slice only
	python -m pytest tests/themes -q

test-fast: ## Run high-signal test slices (CLI + themes)
	python -m pytest cli/tests tests/themes -q
```

Also updated `.PHONY` to include these targets.

## Verification Commands & Outputs

All acceptance criteria verified ✅

### 1. `make lint`

```
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 249 source files
black --check core cli tests
All done! ✨ 🍰 ✨
230 files would be left unchanged.
isort --check-only core cli tests
Skipped 44 files
```

### 2. `pytest -q` (full suite)

```
751 passed, 45 warnings in 162.22s (0:02:42)
Exit code: 0
```

### 3. `pytest -q cli/tests` (CLI slice)

```
16 passed, 7 warnings in 3.68s
Exit code: 0
```

### 4. `pytest -q tests/themes` (themes slice)

```
69 passed, 7 warnings in 44.66s
Exit code: 0
```

### 5. `make test-cli`

```
16 passed, 7 warnings in 3.59s
Exit code: 0
```

### 6. `make test-themes`

```
69 passed, 7 warnings in 47.98s
Exit code: 0
```

### 7. `git status -sb`

```
## test/TEST-009-test-slices-runnable...origin/test/TEST-009-test-slices-runnable
 M Makefile
 M cli/tests/conftest.py
```

## Files Changed

| File                                       | Change                                                                 |
| ------------------------------------------ | ---------------------------------------------------------------------- |
| `cli/tests/conftest.py`                    | Added `sys.path` insertion for repo root + noqa comments               |
| `Makefile`                                 | Added `test-cli`, `test-themes`, `test-fast` targets; updated `.PHONY` |
| `docs/dev/Tasks/TEST/TEST-009.md`          | Task ticket (committed first)                                          |
| `docs/dev/Tasks/TEST/TEST-009_followup.md` | This document                                                          |

## Confirmation

- ✅ Test slices are now reliably runnable from repo root
- ✅ Full suite remains green
- ✅ Lint passes without warnings
- ✅ No protected directory artifacts left behind
- ✅ Makefile targets provide repeatable, agent-proof workflow
