## TEST-01 — Safe Deletion Guards + Source Asset Protection in Tests

**Branch:** `develop`
**Goal:** Make it *impossible* for test cleanup (or CLI-driven test runs) to delete/modify repo source assets (themes, boilerplate, core, etc.). This prevents repeats of the “Theme Delete Drama” class of incident.

### Context

We have tests that run destructive filesystem operations (directly or via CLI like `sum init`). Cleanup has previously used unsafe deletion (e.g. `shutil.rmtree` on a path that can resolve to real repo directories). Post-MVP themes make this risk worse because tests touch theme assets and template trees more often.

This task implements **guardrails that fail fast** if anything tries to delete outside pytest’s sandbox.

---

## Scope

### A) Add a shared safe cleanup utility

Create a reusable helper (location flexible; suggested `tests/utils/safe_cleanup.py` or equivalent):

* `UnsafeDeleteError(Exception)`
* `PROTECTED_PATHS` list (at least: `.git`, `themes`, `boilerplate`, `core`, `cli`, `docs`, `scripts`, `infrastructure` — agent to align with actual repo layout)
* `safe_rmtree(path, repo_root, tmp_base)`:

  * resolves paths
  * refuses deleting:

    * repo root
    * anything containing `.git`
    * any protected dir or anything under it
    * anything not under `tmp_base` (pytest `tmp_path` root)
  * performs `shutil.rmtree(path, ignore_errors=False)` only if safe

Also add `register_cleanup(...)` helper if you want a neat fixture pattern.

### B) Replace unsafe cleanup usage in the test suite

* Find and replace direct destructive operations in tests (common offenders: `shutil.rmtree`, `rm -rf`, homegrown cleanup functions).
* Ensure CLI/theme tests write to `tmp_path` (or a subdir) and only delete under `tmp_path`.
* If there are tests that genuinely need a writable theme tree, they must copy into `tmp_path` first.

### C) Enforce via pytest fixtures

Add fixture(s) so tests can’t “forget” the sandbox:

* A fixture (or autouse fixture for CLI/theme test packages) that provides:

  * `repo_root` (detected safely)
  * `tmp_base` (pytest tmp root)
  * standard cleanup registration

### D) Add permanent regression tripwires

Add at least one test that will fail loudly if source assets disappear, e.g.:

* Assert `themes/theme_a` exists (and optionally `themes/theme_a/theme.json`).

### E) Add CI guardrails (minimal, high-value)

In the CI workflow(s) that run tests:

* After test run: fail if `themes/theme_a` is missing.
* Fail if protected directories changed (example approach: `git status --porcelain` must be clean, or `git diff --exit-code -- themes boilerplate core cli`).

(Exact CI implementation depends on your current workflow files; agent to integrate cleanly.)

---

## Non-goals

* Refactoring the whole test suite structure or reworking template-resolution logic (that’s later tickets).
* Changing production CLI behaviour unless it’s clearly sharing unsafe deletion code paths (agent can flag if discovered).

---

## Acceptance Criteria

* ✅ `safe_rmtree` exists and refuses deletion outside `tmp_path` with clear error messages.
* ✅ No tests in CLI/theme areas directly call `shutil.rmtree` (or equivalent) on non-sandbox paths.
* ✅ CLI/theme tests run entirely inside `tmp_path` for write/delete operations.
* ✅ Regression test(s) guarantee `themes/theme_a` cannot “vanish silently”.
* ✅ CI fails if theme source assets are missing or protected paths are modified by the test run.

---

## Verification Steps (local)

* `pytest` for the affected test groups passes.
* Run full suite and confirm `git status --porcelain` is clean afterwards.
* Add/keep a unit test that intentionally attempts unsafe deletion and asserts `UnsafeDeleteError` is raised.

---

## Record-keeping

* Update `test-strategy-post-mvp-v1.md` if implementation details differ materially from the draft.
* Append a short entry to `docs/ops-pack/what-broke-last-time.md` capturing the original incident pattern + the new enforced guardrails (so it doesn’t recur).

---

**Complexity:** **Medium** (filesystem + pytest fixture wiring + CI edits; contained, but needs care)
