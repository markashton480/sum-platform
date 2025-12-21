
# TEST-007 — Enforce filesystem sandbox + guarded deletion for CLI/theme tests

**Branch:** `test/TEST-007-safe-cleanup` (from `origin/develop`)
**PR target:** `develop`
**Goal:** Prevent any test (especially CLI/theme tests) from deleting or writing to repo source assets by enforcing a tmp-path sandbox and using guarded deletion utilities everywhere.

### Context

We’ve had incidents where tests (or CLI-invoked tests) deleted or modified real repo directories (e.g. themes). Post-MVP theme work increases filesystem churn, so we need hard safety rails:

* **Read-only source assets** (themes, boilerplate)
* **Write-only sandbox** (`tmp_path`)
* **Safe cleanup only** (guarded `rmtree`)

### Scope

#### A) Introduce a canonical safe deletion helper

Create a shared helper (location flexible; suggested `tests/utils/safe_cleanup.py`) with:

* `UnsafeDeleteError`
* `safe_rmtree(path, repo_root, tmp_base, protected_paths=...)`:

  * resolve path
  * refuse deletion if:

    * path is repo root
    * path contains `.git`
    * path is inside protected dirs (`themes/`, `core/`, `cli/`, `docs/`, `boilerplate/`, `infrastructure/`, etc.)
    * path is **not** under `tmp_base` (pytest `tmp_path` base)
  * only then delete using `shutil.rmtree`

**Optional but recommended:** require a sentinel file (e.g. `.sum_test_sandbox`) in the sandbox root before allowing any deletion. This eliminates “tmp_path pointed somewhere unexpected” footguns.

#### B) Replace unsafe cleanup patterns in tests

* Search for direct destructive filesystem calls and replace with `safe_rmtree` (or sandbox fixture cleanup).
* Especially target `cli/tests/**` and `tests/themes/**`.

#### C) Enforce sandboxing with fixtures for CLI/theme tests

Add autouse fixture(s) in:

* `cli/tests/conftest.py`
* `tests/themes/conftest.py` (or equivalent)
  That:
* creates a sandbox root under `tmp_path`
* sets CLI-related env vars so `sum init` writes into sandbox only (agent to align with actual CLI env var names used in repo)
* ensures cleanup uses `safe_rmtree`

#### D) Add permanent regression “tripwire” test(s)

Add a small test that always asserts critical source assets exist post-run, e.g.:

* `themes/theme_a` exists
* `themes/theme_a/theme.json` exists

#### E) CI guard (lightweight)

Add a CI step after tests:

* fail if `themes/theme_a` missing
* fail if protected directories have tracked diffs after test run (use `git diff --exit-code -- <protected dirs>`)

### Non-goals

* No changes to template resolution logic (already handled by prior tickets).
* No large restructuring of test suite.

### Acceptance Criteria

* ✅ No test code directly deletes paths without going through `safe_rmtree` (or fixture-managed cleanup).
* ✅ CLI/theme tests write only into `tmp_path` sandbox.
* ✅ Regression tripwire exists and passes.
* ✅ `make lint` and `pytest -q` pass locally.
* ✅ CI on PR passes.

### Verification Commands

```bash
source .venv/bin/activate
make lint
pytest -q
pytest -q cli/tests tests/themes
```

### Git hygiene (mandatory)

* Start with clean tree (`git status --porcelain` empty).
* Ticket doc committed early: `docs/dev/Tasks/TEST/TEST-007.md`
* Final follow-up report: `docs/dev/Tasks/TEST/TEST-007_followup.md` with:

  * commands run + outputs
  * commit SHA(s)
  * summary of changed files
* End with clean tree.

**Commit plan (preferred 2 commits):**

1. `test(TEST-007): enforce tmp sandbox + guarded deletion for CLI/theme tests`
2. `docs(TEST-007): record safety rails + verification evidence`

**Complexity:** **High** (touches fixtures + filesystem safety; high impact, must be careful)

---
