# TEST-008 — Follow-up Report

**Branch:** `test/TEST-008-ci-guard-unconditional`
**Completed:** 2025-12-21
**Assignee:** Antigravity (Senior Django QA/Testing Engineer)

## Objective

Ensure CI reliably fails on _any_ tracked or untracked artifacts under protected directories after tests, and remove "clever" cleanup logic from `test_safe_cleanup.py` so the tests prove what they claim.

## Findings

### 1. CI Guard Status

The CI protected-path guard was **already made unconditional** in commit `51ce12b` (TEST-007). The previous version used:

```bash
if ! git diff --quiet -- themes boilerplate core cli docs scripts infrastructure; then
```

This conditional only caught **tracked** file changes, missing untracked files.

The current implementation (as of develop @ ca0af06) already uses the unconditional pattern:

```bash
protected_paths=(themes boilerplate core cli docs scripts infrastructure clients design media)
status_output=$(git status --porcelain --untracked-files=all -- "${protected_paths[@]}")
if [ -n "$status_output" ]; then
  echo "Protected directories were modified or contain untracked files during tests" >&2
  echo "$status_output"
  exit 1
fi
```

**Conclusion:** The CI guard fix described in the ticket was already implemented. No CI workflow changes were required for TEST-008.

### 2. Safety Cleanup Test Simplification

**File:** `tests/utils/test_safe_cleanup.py`
**Test:** `test_safe_rmtree_rejects_outside_tmp_base`

**Problem:** The cleanup logic was widening safety boundaries to make deletion pass:

```python
finally:
    safe_rmtree(outside, repo_root=REPO_ROOT, tmp_base=outside.parent)
```

This undermined the invariant being tested by changing `tmp_base` to allow the deletion.

**Fix:** Relocate test-created directory into tmp, then cleanup within normal boundaries:

```python
finally:
    # Relocate into tmp, then cleanup within normal boundaries
    cleanup_dir = tmp_path_factory.mktemp("outside-cleanup") / "relocated"
    outside.rename(cleanup_dir)
    safe_rmtree(cleanup_dir, repo_root=REPO_ROOT, tmp_base=tmp_base)
```

This maintains the safety invariant while properly cleaning up the test artifact.

### 3. CLI CSS Test Isolation

**File:** `cli/tests/test_cli_init_and_check.py`
**Test:** `test_check_fails_when_theme_compiled_css_missing`

**Problem:** The test renamed CSS file to simulate missing CSS but didn't restore it in case of test failure:

```python
css_path.rename(missing_css_backup)

monkeypatch.chdir(project_root)
exit_code = run_check()
captured = capsys.readouterr()

assert exit_code == 1
assert "Theme compiled CSS" in captured.out
```

**Fix:** Wrapped operations in try/finally to ensure file restoration:

```python
css_path.rename(missing_css_backup)

try:
    monkeypatch.chdir(project_root)
    exit_code = run_check()
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Theme compiled CSS" in captured.out
finally:
    # Restore CSS file to maintain test isolation
    if missing_css_backup.exists():
        missing_css_backup.rename(css_path)
```

This ensures test isolation even if the test fails or is interrupted.

## Verification

### Lint Check

```bash
$ source .venv/bin/activate
$ make lint
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

### Test Suite

```bash
$ source .venv/bin/activate
$ pytest -q
== 751 passed, 45 warnings in 189.44s (0:03:09) ===
```

All tests passed, including:

- `tests/utils/test_safe_cleanup.py::test_safe_rmtree_rejects_outside_tmp_base`
- `cli/tests/test_cli_init_and_check.py::test_check_fails_when_theme_compiled_css_missing`

### Git Status

```bash
$ git status -sb
## test/TEST-008-ci-guard-unconditional
```

Clean working tree after all tests run.

## Commits

1. **f15f289** - `chore(docs): agent config updates - to be merged via TEST-008`

   - Cherry-picked from TEST-007 branch
   - Contains mistakenly modified agent config files (AGENTS.md, sum-core-rules.md, sumrule.mdc)

2. **2cf493d** - `docs(TEST-008): add task ticket`

   - Added TEST-008.md task description

3. **1bcaaea** - `test(TEST-008): simplify safety cleanup tests + add CLI CSS test isolation`
   - Refactored `test_safe_rmtree_rejects_outside_tmp_base` cleanup to maintain safety invariants
   - Added try/finally to `test_check_fails_when_theme_compiled_css_missing` for proper isolation

## Impact

### Safety Improvements

1. **Test cleanup logic now correctly proves safety boundaries** - The `test_safe_rmtree_rejects_outside_tmp_base` test no longer "cheats" by widening `tmp_base` during cleanup.

2. **CLI test isolation hardened** - The CSS rename test now properly restores files even on failure, preventing test pollution.

3. **CI guard already unconditional** - Confirmed that the protected-path guard reliably catches both tracked changes and untracked files.

## Notes

The primary goal of TEST-008 (making CI guard unconditional) was already accomplished in TEST-007 (commit 51ce12b). This ticket's implementation focused on the test cleanup refinements, which were still needed and valuable for maintaining test integrity.

The changes are minimal, focused, and all tests pass cleanly. The working tree remains clean after test execution, confirming no unintended side effects.

## References

- Task ticket: `docs/dev/Tasks/TEST/TEST-008.md`
- Prior work: TEST-007 (commit 51ce12b) - "audit filesystem safety + tighten CI untracked guard"
- Git log: `git log --oneline test/TEST-008-ci-guard-unconditional`
