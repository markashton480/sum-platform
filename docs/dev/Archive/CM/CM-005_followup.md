# CM-005 Follow-up Report

## Overview

CM-005 successfully established a cleaner baseline for the repository.
- **Dependencies**: Audited and confirmed clean.
- **Linting**: Enforced via `make lint`.
- **Warnings**: Duplicate `navigation_tags` warning resolved.
- **Testing**: Added `caplog_propagate` fixture to simplify logging tests.

## Remaining Technical Debt (M5+)

### 1. Mypy Strictness
`make lint` currently suppresses mypy errors (`|| true`). There are ~28 mypy errors remaining, mostly related to:
- `[no-any-return]`
- `[union-attr]`
- `[index]`
- Missing type annotations in `sum_core` modules.

**Recommendation**: Create a dedicated task to fix strict mypy errors and remove `|| true` from `Makefile`.

### 2. Pre-commit Sync
Verify `pre-commit` config aligns perfectly with `Makefile` commands to ensure local DX matches CI exactly.

### 3. Pytest Deprecation Warnings
While system check warnings are gone, pytest output may still contain deprecation warnings from third-party packages that should be monitored.
