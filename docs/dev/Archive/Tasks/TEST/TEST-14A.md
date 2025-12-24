# TEST-014A — Close-out fixes for PR #16 (bidi unicode + conftest cleanup + follow-up accuracy)

## Goal
Fix the remaining merge blockers in PR #16 (TEST-014) so we can merge it cleanly with confidence:
1) Remove hidden/bidirectional Unicode characters flagged by GitHub
2) Make `tests/themes/conftest.py` unambiguous and correct (single REPO_ROOT, single sandbox creation, correct docstring position, no duplicate imports)
3) Ensure follow-up documentation ends with a truly clean repo state

## Context
PR #16 introduces theme fixtures and refactors theme tests to use centralized repo-root utilities. CI is green, but GitHub flags hidden/bidi Unicode text and the theme conftest diff shows duplicate/contradictory lines that reduce trust in the fixture. These must be fixed *inside the same PR* before merging.

## Scope (IN)
- ONLY changes required to:
  - remove bidi/unicode control characters
  - clean up `tests/themes/conftest.py` fixture implementation and imports
  - correct follow-up report to reflect actual “clean” status at the end
- Keep the fixture behavior the same (autouse sandbox protection remains)

## Scope (OUT)
- No new tests
- No refactors outside theme tests/conftest/docs related to this PR
- No CI workflow changes

---

## Required Fixes

### 1) Remove hidden/bidirectional Unicode characters (merge blocker)
GitHub UI shows “hidden or bidirectional Unicode text” warnings in PR #16.

**Action:**
- Scan the following files for bidi control chars and remove them:
  - `tests/themes/conftest.py`
  - `tests/themes/test_theme_a_guardrails.py`
  - `tests/themes/test_theme_a_contract.py`
  - `tests/themes/test_theme_a_tailwind.py`
  - `docs/dev/Tasks/TEST/TEST-014.md`
  - `docs/dev/Tasks/TEST/TEST-014_followup.md`

**How to scan (pick one):**
- Python one-liner (preferred):
  ```bash
  python - <<'PY'
  import pathlib, sys
  files = [
    "tests/themes/conftest.py",
    "tests/themes/test_theme_a_guardrails.py",
    "tests/themes/test_theme_a_contract.py",
    "tests/themes/test_theme_a_tailwind.py",
    "docs/dev/Tasks/TEST/TEST-014.md",
    "docs/dev/Tasks/TEST/TEST-014_followup.md",
  ]
  bad = []
  for f in files:
    p = pathlib.Path(f)
    t = p.read_text(encoding="utf-8")
    # common bidi control chars
    bidi = ["\u202A","\u202B","\u202C","\u202D","\u202E","\u2066","\u2067","\u2068","\u2069"]
    if any(ch in t for ch in bidi):
      bad.append(f)
  if bad:
    print("BIDI FOUND in:", *bad, sep="\n- ")
    sys.exit(1)
  print("No bidi chars found.")
  PY
```  
* If found:

  * Remove the characters manually (retype affected lines if needed).
  * Re-run the scanner until clean.

### 2) Clean up `tests/themes/conftest.py` (make it deterministic and readable)

Current PR diff suggests:

* duplicate repo_root resolution (both `Path(__file__).resolve().parents[2]` and `REPO_ROOT`)
* duplicate sandbox creation lines
* duplicate imports for `create_filesystem_sandbox`
* docstring not being the first statement in the fixture

**Target state:**

* Use **only** `REPO_ROOT` for repo root
* Import `create_filesystem_sandbox` **once** (prefer `from tests.utils import create_filesystem_sandbox, REPO_ROOT` if that’s the canonical API)
* `theme_filesystem_sandbox` fixture should:

  * have docstring as first statement
  * create sandbox once
  * register it cleanly (whatever pattern tests/utils expects)
  * be easy to audit at a glance

**Acceptance checks for this file:**

* No duplicate imports
* No dead variables (`repo_root = ...` not used)
* No duplicated sandbox call
* No docstring placed after code

### 3) Fix follow-up report so the end state is truly clean

The follow-up currently implies “expected modified files” which contradicts a clean close-out expectation.

**Action:**

* Ensure final verification section ends with:

  ```bash
  git status --porcelain
  ```

  showing **(empty output)** or explicit `(clean)` if your shell prints that.
* If intermediate steps had changes, keep them, but the final pasted output must reflect the real final state.

---

## Acceptance Criteria

* [ ] GitHub no longer shows “hidden/bidirectional Unicode text” warnings on the PR files
* [ ] `tests/themes/conftest.py` is unambiguous: single REPO_ROOT, single sandbox, proper docstring, no duplicate imports
* [ ] `make lint` passes
* [ ] `make test-themes` passes
* [ ] `make test-templates` passes (guard against incidental breakage)
* [ ] `make test` passes
* [ ] Final `git status --porcelain` is empty
* [ ] PR #16 updated with a final commit that clearly states it’s a close-out fix (e.g. `fix(TEST-014): remove bidi chars and cleanup theme conftest`)

---

## Verification Commands (must paste into follow-up)

```bash
make lint
make test-themes
make test-templates
make test
git status --porcelain
```

---

## Git hygiene (non-negotiable)

This is a fix-up on the existing PR branch.

1. Ensure you’re on the PR branch and up-to-date:

```bash
git fetch origin
git checkout test/TEST-014-theme-conftest
git pull --ff-only origin test/TEST-014-theme-conftest
git status
```

2. Make changes, then commit with a single clear message:

```bash
git add tests/themes/conftest.py tests/themes/*.py docs/dev/Tasks/TEST/TEST-014*.md
git commit -m "fix(TEST-014): remove bidi chars and cleanup theme conftest"
git push
```

3. Update `docs/dev/Tasks/TEST/TEST-014_followup.md` with final verification outputs (including clean git status) and push in the same commit if possible (or a second commit if necessary).

---

## Stop / Rollback Triggers

* Any new warnings/flakes introduced
* Any weakening/removal of sandbox protection
* Any changes that touch protected source dirs beyond imports/refactors (themes/ must remain read-only)

## Deliverables

* Updated PR #16 with the close-out fix commit(s)
* Follow-up doc updated with final verification outputs
* PR ready to merge once CI is green and GitHub warnings are gone

```
