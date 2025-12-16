# CM-008 Follow-up Report

**Task**: Make `sum check` contract and environment behavior explicit  
**Completed**: 2025-12-16

## Summary

This corrective mission resolved ambiguity around `sum check` execution modes and added a guardrail to prevent boilerplate drift between the canonical `/boilerplate/` and the CLI-bundled copy.

## Changes Implemented

### 1. Explicit Monorepo Detection in `check.py`

Added three new functions to handle monorepo mode:

- `_detect_monorepo_root()` - Traverses upward from CWD to find repo root (identified by `core/sum_core/__init__.py` and `boilerplate/manage.py` markers)
- `_setup_monorepo_core_import()` - Adds `core/` to `sys.path` when in monorepo context
- `_cleanup_monorepo_core_import()` - Removes the path after check completes

The `run_check()` function now:

- Detects monorepo context before attempting `sum_core` import
- Reports `[OK] sum_core import: monorepo mode` when in monorepo
- Provides friendly error `Install requirements first: pip install -r requirements.txt` in standalone mode

### 2. Test Refactoring

- Removed the test-only `_add_repo_core_to_syspath()` hack from `test_cli_init_and_check.py`
- Tests now rely on the CLI's own monorepo detection behavior
- Added `test_check_standalone_mode_fails_with_friendly_message` to verify standalone mode error messaging
- Fixed test isolation by using unique project names (`cli-check-{timestamp}`)

### 3. Boilerplate Drift Guard

Created `cli/scripts/sync_boilerplate.py` with:

- `--check` mode for CI that fails if boilerplate has drifted
- Sync mode to copy canonical boilerplate to CLI package

Added Makefile targets:

- `make sync-cli-boilerplate` - Syncs boilerplate
- `make check-cli-boilerplate` - CI guard for drift detection

### 4. Documentation Updates

Expanded `docs/dev/cli.md` with:

- Execution modes section explaining monorepo vs standalone behavior
- Table of what `sum check` validates
- List of what `sum check` does NOT validate
- Boilerplate sync instructions for maintainers

## Files Modified

| File                                   | Change                                                       |
| -------------------------------------- | ------------------------------------------------------------ |
| `cli/sum_cli/commands/check.py`        | Added monorepo detection and explicit mode logging           |
| `cli/tests/test_cli_init_and_check.py` | Removed sys.path hack, added standalone mode test            |
| `cli/scripts/sync_boilerplate.py`      | New file for boilerplate sync/check                          |
| `Makefile`                             | Added sync-cli-boilerplate and check-cli-boilerplate targets |
| `docs/dev/cli.md`                      | Expanded with execution modes and validation details         |

## Verification

- **Lint**: All checks pass (`ruff check`, `black --check`, `isort --check-only`)
- **Tests**: 652 tests passed
- **Boilerplate check**: `make check-cli-boilerplate` reports in sync

## Recommendations

1. **Add to CI pipeline**: Include `make check-cli-boilerplate` in CI to catch drift early
2. **Consider version marker**: For future releases, a version marker file in boilerplate could help track sync state

## No Remaining Issues

This corrective mission fully addresses the identified red flags from M5-003. The CLI now owns its monorepo detection behavior, tests no longer use hacks, and boilerplate drift is guarded.
