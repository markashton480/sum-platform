# TEST-015 — CLI Safety Refactor + Explicit CLI Safety Regression Tests

## Context

We’ve implemented foundational safety rails, shared fixtures, theme/template slices, and theme conftest refactors through **TEST-014B**. The next aligned step in the post-MVP test strategy is **Phase 5: CLI Safety Refactor**: refactor `cli/tests` to use isolation fixtures + guarded deletion patterns, then add explicit CLI safety tests to prevent repeat “source deletion” incidents.  

## Goal

Make **CLI tests safe by design**:

* All filesystem writes happen under `tmp_path`
* CLI subprocess calls run with an isolated env (e.g. `SUM_CLIENT_OUTPUT_PATH`)
* **No raw `shutil.rmtree`** (or equivalent) in `cli/tests/*`
* Source assets (especially `themes/` and `boilerplate/`) are verified **unchanged** after CLI operations
* Add explicit regression tests covering the dangerous failure modes (init output boundaries, source immutability, repeated init, cleanup safety)

This corresponds to Phase 5 tasks 5.1–5.4 in the implementation plan. 

---

## 1. Branch

1. Ensure you are on `develop` and up to date:

   * `git checkout develop`
   * `git pull origin develop`
   * `git branch --show-current` (must show `develop`)

2. Create a working branch:

   * `git checkout -b test/TEST-015-cli-safety-refactor`
   * `git branch --show-current` (must show `test/TEST-015-cli-safety-refactor`)

---

## 2. Task Work

### 2.1 Audit existing CLI tests (Phase 5.1)

1. Enumerate CLI test files (likely `cli/tests/test_*.py`) and document in the follow-up report:

   * Which tests invoke `sum init` / `sum check`
   * Which tests write files / delete directories
   * Any direct uses of `shutil.rmtree`, `Path.unlink`, `rm -rf`, or similar
   * Any patterns that rely on repo-relative working directories or mutable source paths

2. Add a quick guard check during the audit:

   * `git grep -n "shutil\.rmtree" cli/tests || true`
   * `git grep -n "unlink\(" cli/tests || true`
   * Note: we’re only policing `cli/tests/` here (the safe cleanup utility may legitimately use `shutil.rmtree` elsewhere).

### 2.2 Confirm / improve isolation fixtures in `cli/tests/conftest.py`

Ensure there is a single, consistent way for CLI tests to run in an isolated sandbox, per strategy guidance. 

Minimum expectations:

* `isolated_theme_env(tmp_path) -> dict[str, str]` provides:

  * `SUM_THEME_PATH` pointing to **repo source** themes (read-only intent)
  * `SUM_BOILERPLATE_PATH` pointing to **repo source** boilerplate (read-only intent)
  * `SUM_CLIENT_OUTPUT_PATH` pointing to a **tmp_path subdir** (write location)
  * `SUM_TEST_MODE=1`
* Prefer “no manual cleanup”: rely on `tmp_path` lifecycle. Only delete if you must; if you must, use the guarded deletion utility (safe_rmtree) rather than raw `shutil.rmtree`. 
* Add (or reuse) a helper to snapshot **source theme state** (e.g. contents/hash, or at least key files + template count) so tests can assert “unchanged after init”.

If you can reuse the shared helpers introduced earlier (e.g. protected-path assertions in `tests/utils/fixtures.py`), do so — but keep imports robust for `cli/tests` runs. If importing shared helpers is brittle, implement a small local snapshot helper inside `cli/tests` to avoid slice breakage.

### 2.3 Refactor `cli/tests/test_theme_init.py` (Phase 5.2)

Refactor to align with the strategy:

* Use `tmp_path` for all working directories and outputs
* Use `isolated_theme_env` for subprocess calls
* Remove ad-hoc `finally` cleanups and any raw deletions
* After each test that calls `sum init`, assert:

  * Output was created under `SUM_CLIENT_OUTPUT_PATH` (not repo root)
  * Source `themes/theme_a` exists and required files exist (at minimum `theme.json`)
  * If snapshotting is implemented: snapshot before/after is identical

### 2.4 Refactor `cli/tests/test_cli_init_and_check.py` (Phase 5.3)

Apply the same refactor principles:

* All outputs under `tmp_path`
* All subprocess calls use the isolated env
* Assert output boundaries
* Assert source themes unchanged
* Avoid manual deletion unless strictly required (and then only via guard utilities)

### 2.5 Add `cli/tests/test_cli_safety.py` (Phase 5.4)

Create explicit safety regression tests that cover:

* **Init output boundary:** init creates project only under `SUM_CLIENT_OUTPUT_PATH`
* **Source immutability:** theme source files unchanged after init
* **Cleanup safety:** any cleanup performed in tests never targets source paths
* **Multiple inits:** repeated init runs don’t corrupt source themes/boilerplate

Mark these tests with `@pytest.mark.regression` (and any other markers already used in the suite).

Implementation guidance can follow the test strategy’s CLI isolation model and safety checks. 

---

## 3. Documentation Updates

1. Ensure this task ticket is saved at:

* `docs/dev/Tasks/TEST/TEST-015.md`

2. Create and fill in the work report:

* `docs/dev/Tasks/TEST/TEST-015_followup.md`

The follow-up must include:

* What was audited (files + findings)
* Exactly what was changed (high level + any tricky bits)
* Commands run + outcomes
* Any remaining tech debt / known caveats (if any)

**Both documents must be included in the commit(s).**

---

## 4. Commit + Push

Make commits with messages that include the ticket ID, for example:

* `refactor(TEST-015): harden cli tests to use isolated env + tmp_path`
* `test(TEST-015): add explicit cli safety regression tests`
* `docs(TEST-015): add task ticket and followup report`

Then:

* `git push -u origin test/TEST-015-cli-safety-refactor`

---

## Verification

Run:

1. `make lint`
2. `make test`
3. `make test-cli`
4. (If available in your repo) run the other slices you’ve been maintaining:

   * `make test-themes`
   * `make test-templates`

Then **always finish** with:

* `git status --porcelain`

“Clean” means:

* **No output**, OR
* Only intentionally untracked files that are explicitly documented in `TEST-015_followup.md` (prefer: no untracked artifacts).

---

