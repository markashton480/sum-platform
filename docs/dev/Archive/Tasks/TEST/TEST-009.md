# TEST-009 — Fix CLI test slice imports + add test slice make targets

**ID:** TEST-009
**Branch:** `test/TEST-009-test-slices-runnable`
**Base branch:** `origin/develop`
**PR target:** `develop`

### ⚠️ Context from previous task

The agent tried to run the “slice” verification (`pytest -q cli/tests tests/themes`) and hit a **real import-path problem** (`ModuleNotFoundError: No module named 'tests.utils'`). They hand-waved it away as “full suite already covers it”, but that’s _not the point_ — the whole reason you’re formalising this is so you can run targeted slices reliably. (This also matches exactly the kind of “looks fine in CI, annoying locally” friction you’re trying to kill.)

So: **TEST-008 is mergeable**, but it also **revealed the next real problem** to fix.

### Minor nit (not urgent)

Copilot flagged that the `finally` restore can be fragile if the target file unexpectedly exists (or if the temp dir disappears). It’s not failing now, but it’s worth hardening while you’re in this area. ([GitHub][1])

## Context

In TEST-008, the full suite passed, but running the intended verification slice failed:

- `pytest -q cli/tests` (or `pytest -q cli/tests tests/themes`) raised `ModuleNotFoundError: No module named 'tests.utils'`.

This blocks the post-MVP goal of fast, reliable iteration via test slices (CLI vs themes vs full).

## Objective

Make CLI and theme test slices runnable directly from repo root, and codify them as Makefile targets so the workflow is repeatable and agent-proof.

## Scope

### A) Fix CLI slice import path

- Ensure **`pytest -q cli/tests` works when run from repo root**.
- Do **not** “solve” by saying “full suite already runs them” — this ticket exists specifically to enable sliced runs.
- Prefer a minimal, explicit fix:

  - Example acceptable approaches:

    - Add a small `sys.path` insertion in `cli/tests/conftest.py` that anchors to repo root (test-only, explicit).
    - Or refactor the shared helper import so it doesn’t depend on `tests.utils` being importable in that context.

  - Avoid large refactors or moving lots of files unless unavoidable.

### B) Add Makefile targets for slices

Add targets (names can vary slightly if project conventions exist):

- `make test-cli` → runs CLI test suite slice only
- `make test-themes` → runs themes test suite slice only
- (Optional) `make test-fast` → runs the “high signal” slices you actually use day-to-day

### C) (Small hardening, if touched anyway)

If you touch the CLI CSS-missing test again, harden the restore so it can’t fail if the target path exists unexpectedly (only if this is genuinely trivial and doesn’t widen scope).

## Acceptance Criteria

- From repo root:

  - `source .venv/bin/activate && make lint` ✅
  - `source .venv/bin/activate && pytest -q` ✅
  - `source .venv/bin/activate && pytest -q cli/tests` ✅
  - `source .venv/bin/activate && pytest -q tests/themes` ✅
  - `source .venv/bin/activate && make test-cli` ✅
  - `source .venv/bin/activate && make test-themes` ✅

- No changes leave artifacts behind in protected directories (CI guard should remain satisfied).

## Required Work Log

Create/update:

- `docs/dev/Tasks/TEST/TEST-009.md` (task ticket added early)
- `docs/dev/Tasks/TEST/TEST-009_followup.md` including:

  - commands run + outputs
  - what was changed + why (esp. import-path fix)
  - confirmation that slice runs are now reliable

## Git Hygiene Rules (mandatory)

1. Create branch from `origin/develop`.
2. **Commit `TEST-009.md` first**, then **push immediately**:

   - `git push -u origin HEAD`

3. Implement changes.
4. Ensure `git status -sb` is clean.
5. Commit with:

   - `test(TEST-009): make cli/themes test slices runnable`

6. If docs follow-up added:

   - `docs(TEST-009): record slice-run fix`

7. Push after each commit; PR must show all commits pushed.

## Verification Commands

```bash
source .venv/bin/activate
make lint
pytest -q
pytest -q cli/tests
pytest -q tests/themes
make test-cli
make test-themes
git status -sb
```

**Complexity:** Medium (import-path + small build tooling changes)

---

[1]: https://github.com/markashton480/sum_platform/pull/7/commits/1bcaaeaf93b34a61fe86bf69d22ae8863842416f "Test/test 008 ci guard unconditional by markashton480 · Pull Request #7 · markashton480/sum_platform · GitHub"
