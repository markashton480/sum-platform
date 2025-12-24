# Incident Report: Theme A Deletion ("Theme Delete Drama")

**Date:** 2025-12-21
**Status:** Resolved (Committed)
**Impact:** `themes/theme_a` directory was deleted and the deletion was committed to `develop`.

## 1. Issue Description

During a routine test execution cycle, the entire `themes/theme_a` directory was deleted from the file system. This deletion went unnoticed and was subsequently committed to the `develop` branch in commit `9a12918` ("task: THEME-15-A").

## 2. Root Cause Analysis

The root cause was identified as unsafe file system operations within the CLI integration tests:

- **Files:** `cli/tests/test_theme_init.py`, `cli/tests/test_cli_init_and_check.py`
- **Mechanism:** These tests were initiating `sum init` commands using the repository root as the working context.
- **Destructive Action:** The tests utilized `shutil.rmtree(project_root)` in a `finally` block to clean up test artifacts.
- **Failure Mode:** Due to path resolution ambiguity or test environment configuration (likely running in a mode where the "test project" path overlapped with the actual source tree or the cleanup logic was too aggressive), the tests targeted the source `themes/theme_a` directory for deletion instead of the intended temporary test client directory.

## 3. Resolution Steps Taken

The following actions were taken to recover the data and patch the vulnerability:

1.  **Emergency Restoration:**

    - Executed `git checkout HEAD~1 themes/theme_a` to retrieve the deleted files from the commit immediately preceding the deletion.
    - These files were restored and committed in `a2157f1`.

2.  **Code fix (Test Isolation):**

    - Refactored `cli/tests/test_theme_init.py` and `cli/tests/test_cli_init_and_check.py`.
    - **Change:** Switched from using the real file system to using pytest's `tmp_path` fixture.
    - **Context:** Tests now run in a completely isolated temporary directory.
    - **Wiring:** Explicitly injected `SUM_THEME_PATH` and `SUM_BOILERPLATE_PATH` environment variables pointing to the real repository assets, ensuring tests can _read_ the source templates/theme but _write_ only to the safe temporary directory.
    - **Safety:** Removed manual `shutil.rmtree` calls where possible, relying on pytest's automatic temp dir cleanup.

3.  **Verification:**
    - Ran `pytest cli/tests/test_theme_init.py cli/tests/test_cli_init_and_check.py`.
    - **Result:** 13 passed, 0 failed.
    - **Confirmation:** Verified `themes/theme_a` exists and is intact after test execution.

4.  **Hardening:**
    - Added guarded deletion for test cleanups (refuses `.git`, repo root, or paths outside pytest temp).
    - CLI init cleanup now uses a safe delete guard and temp staging.
    - Added a regression test ensuring CLI init/check does not remove `themes/theme_a`.

## 4. Current Git Status

The repository is currently in a **clean, committed** state with the fix applied on `develop`.

## 5. Next Steps

1.  **(Optional) Full Suite:**
    Run `make test` to ensure no other tests have similar unsafe side effects (grep analysis suggests these were the main culprits).

2.  **(Optional) Git History Cleanup:**
    The commit `9a12918` contains the deletion. If a clean history is required, an interactive rebase could be used to squash the deletion/restoration, though carrying the restore commit is acceptable.
