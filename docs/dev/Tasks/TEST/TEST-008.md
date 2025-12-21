# TEST-008 — Make CI protected-path guard unconditional + simplify safety test cleanup

**Branch:** `test/TEST-008-ci-guard-unconditional` (from `origin/develop`)
**PR target:** `develop`
**Goal:** Ensure CI reliably fails on _any_ tracked or untracked artifacts under protected directories after tests, and remove “clever” cleanup logic from `test_safe_cleanup.py` so the tests prove what they claim.

## Context

PR #6 introduced a `git status --porcelain --untracked-files=all` protected-path guard, but it appears to be gated behind a `git diff` conditional, which can prevent catching untracked files. Also, `tests/utils/test_safe_cleanup.py` cleanup logic is currently structured in a way that may weaken the safety boundaries it intends to test.

## Plan (short)

1. Fix `.github/workflows/ci.yml` so the protected-path check uses **only** `git status --porcelain` and runs **unconditionally**.
2. Simplify `tests/utils/test_safe_cleanup.py` cleanup: avoid changing `tmp_base` to “make deletion pass.” If a test creates a path outside allowed deletion boundaries, cleanup should be done by **relocating into tmp** then calling `safe_rmtree`, or by a clearly-labeled minimal cleanup approach that does not undermine the invariant being tested.
3. Ensure CLI test simulating missing CSS restores state (use `try/finally` around rename if applicable).
4. Update follow-up doc with the _actual_ audit output and verification evidence.
5. Keep commits clean and working tree clean.

## Checklist & Commands

### 0) Start clean

```bash
git switch develop
git pull
git switch -c test/TEST-008-ci-guard-unconditional
git status --porcelain
```

### 1) CI guard: make it unconditional

- Edit `.github/workflows/ci.yml`:

  - Remove/avoid the `if ! git diff --quiet ...; then ... fi` wrapper.
  - Use a single guard like:

**Implementation shape (agent can adapt):**

```bash
protected_paths=(themes boilerplate core cli docs scripts infrastructure)
status_output=$(git status --porcelain --untracked-files=all -- "${protected_paths[@]}")
if [ -n "$status_output" ]; then
  echo "Protected directories were modified or contain untracked files during tests" >&2
  echo "$status_output"
  exit 1
fi
```

### 2) Simplify `test_safe_cleanup.py`

- Make cleanup logic align with the test’s intent:

  - Don’t widen safety boundaries (e.g., don’t set `tmp_base=outside.parent` just to delete it).
  - Preferred: relocate test-created dirs into a known tmp cleanup dir, then `safe_rmtree` within the normal boundary.

### 3) CLI missing CSS test: ensure isolation

- In `cli/tests/test_cli_init_and_check.py`, if simulating missing CSS via rename:

  - Ensure it’s wrapped in `try/finally` and restores original file name.

### 4) Verification

```bash
source .venv/bin/activate
make lint
pytest -q
pytest -q cli/tests tests/themes
git status -sb
```

### 5) Commit hygiene (mandatory)

- Commit 1:

  - `test(TEST-008): unconditional CI protected-path guard; simplify safety cleanup tests`

- Commit 2 (docs only, if changed):

  - `docs(TEST-008): record CI guard + cleanup rationale`

Include:

- `docs/dev/Tasks/TEST/TEST-008.md` (ticket, committed early)
- `docs/dev/Tasks/TEST/TEST-008_followup.md` (commands run + outputs + SHAs)

## Expected success signals

- CI passes on the PR.
- The protected-path guard fails CI if you intentionally create an untracked file under a protected dir.
- `test_safe_cleanup.py` reads simply and does not “cheat” the boundaries it is testing.
- Working tree clean at end.

## Stop / rollback triggers

- Any change that touches real `themes/` source assets during tests.
- CI guard becomes flaky (false positives on clean runs).
- Tests start relying on side effects from renamed/deleted files.

## Record-keeping

- Append any surprises to `docs/ops-pack/what-broke-last-time.md` (only if something genuinely noteworthy happens again).
- Keep `docs/dev/Tasks/TEST/` tidy: TEST-007 remains “cancelled/superseded”, TEST-008 is the finalizer.

**Complexity:** **Medium** (small code changes, high leverage)

---

[1]: https://github.com/markashton480/sum_platform/actions/runs/20415712183/job/58659041700?pr=6 "Test/test 007 safe cleanup · markashton480/sum_platform@a8a41ab · GitHub"
[2]: https://github.com/markashton480/sum_platform/pull/6/commits/51ce12b2b1d6457c3a582429697229f5ca8956f4 "Test/test 007 safe cleanup by markashton480 · Pull Request #6 · markashton480/sum_platform · GitHub"
[3]: https://github.com/markashton480/sum_platform/pull/6/commits/a8a41ab4241d08fe3dd76d98e4f9e2a832dc8fb8 "Test/test 007 safe cleanup by markashton480 · Pull Request #6 · markashton480/sum_platform · GitHub"
