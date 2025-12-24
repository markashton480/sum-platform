## TEST-007R — Filesystem safety audit and gap closure for tests/CI

**Branch:** `test/TEST-007-safe-cleanup` (from `origin/develop`)
**PR target:** `develop`
**Goal:** Confirm filesystem safety is *complete and enforced everywhere*, and fix any remaining gaps. No new safety architecture.

### Scope

1. **Audit: eliminate any remaining unsafe deletion**

* `rg` for direct destructive calls in `tests/` and `cli/tests/` (e.g. `shutil.rmtree`, `rm -rf`, `Path.unlink`, etc.).
* Replace with the existing safe cleanup utilities / fixtures.

2. **Audit: prove CLI tests write only to tmp**

* Confirm all CLI tests that run `sum init` (or similar) set output paths to `tmp_path` and do not touch repo source trees.

3. **CI gap closure: catch untracked junk in protected dirs**
   Your current CI guard in TEST-007 only mentions tracked diffs (`git diff --exit-code`). That *won’t* catch untracked files. 
   Add a CI step that fails if `git status --porcelain` reports **any** changes (tracked or untracked) under protected dirs (`themes/`, `core/`, `cli/`, `boilerplate/`, etc.).

4. **Remove “optional sentinel” from scope**
   No sentinel additions in this ticket. If you later decide you want one, it gets its own dedicated ticket with clear justification.

### Acceptance Criteria

* ✅ No raw destructive deletes remain in test code (outside the safe helper module).
* ✅ CLI/theme tests create outputs only under tmp.
* ✅ CI fails if tests leave *any* artifacts in protected dirs (tracked or untracked).
* ✅ `make lint`, `pytest -q`, and `pytest -q cli/tests tests/themes` pass.
* ✅ Working tree clean; commit(s) clean; PR green.

### Complexity

**Medium** (audit + small targeted fixes + CI tweak)

---

