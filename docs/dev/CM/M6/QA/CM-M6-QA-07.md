## CM-M6-QA-07 — CI Gate Proof + Evidence Completion + Cleanup

**Type**: Corrective Mission (QA)
**Milestone**: M6 / M6-A (process + QA hardening)
**Status**: Ready
**Owner**: QA Agent
**Priority**: High (closes the loop on “branch protection is real”)

### Context

We’ve now:

* Hardened CI workflow and documented branch protection setup in `docs/dev/hygiene.md`.
* Enabled branch protection on GitHub for `main` with **required check**: `lint-and-test`, and “require branch up to date” + “require conversation resolution”.

However, the CM-M6-QA-06 follow-up still has **missing evidence links** (PR + CI run) and we haven’t yet done a **deliberate failing PR** to *prove* the gate blocks merges.

This CM is about **closing that audit trail** and **proving enforcement**.

---

## Objective

1. Prove branch protection is genuinely enforcing CI by attempting to merge a PR with a failing `lint-and-test` check.
2. Backfill evidence in the CM trail (PR URL, CI run URL(s), screenshots if helpful).
3. Clean up any leftover branches / docs inconsistencies so the paper trail matches reality.

---

## Scope

### In scope

* Creating a small “intentional failure” PR (reversible, minimal blast radius)
* Confirming GitHub blocks merge until `lint-and-test` passes and branch is up to date
* Capturing URLs + screenshots and updating the CM follow-up report
* Optional: delete the test branch after completion

### Out of scope

* Fixing Copilot review findings (that’s a separate CM)
* Refactoring / linting / typing improvements beyond what’s required to prove the gate
* Any theme/rendering contract changes

---

## Preconditions

* You have GitHub access to the repo and can create PRs.
* Branch protections are already configured for `main` (they are, but we’re proving it).
* Local environment is working (`make test` currently passes).

---

## Plan (short)

1. Create a branch that introduces a **guaranteed CI failure** in the simplest possible way.
2. Open PR → verify merge is blocked by required status check.
3. Fix failure → push → verify merge becomes allowed only after checks pass and branch is up to date.
4. Close the loop in docs: fill evidence, update “manual step required” → “applied”, record outcomes.
5. Cleanup: delete the test branch.

---

## Checklist & Commands

### A) Create a “fail CI on purpose” PR (minimal + safe)

**Preferred method (non-code): break the workflow file temporarily.**
This guarantees `lint-and-test` fails, without touching Python logic.

1. Create a branch:

```bash
git checkout main
git pull
git checkout -b cm/CM-M6-QA-07-ci-gate-proof
```

2. Introduce a *small intentional syntax error* in `.github/workflows/ci.yml`
   Example: remove a colon, mess indentation, or change `runs-on:` to `runs-on` (no colon). Keep it obviously reversible.

3. Commit and push:

```bash
git add .github/workflows/ci.yml
git commit -m "test(ci): intentionally break workflow to prove branch protection gate"
git push -u origin cm/CM-M6-QA-07-ci-gate-proof
```

4. Open a PR to `main` (GitHub UI is fine).

**Success signal:**

* The PR shows the `lint-and-test` check as failed (or workflow error)
* Merge button is blocked with messaging like “Required status check ‘lint-and-test’ is expected/pending/failed”.

### B) Capture evidence (do this while it’s failing)

Record:

* PR URL
* The failing CI run URL
* Screenshot of merge blocked state (optional but very useful for audit trail)

### C) Fix the workflow + prove recovery

1. On the same branch, revert the workflow break (restore the file):

```bash
git checkout -- .github/workflows/ci.yml
# or manually fix back to previous correct state
git add .github/workflows/ci.yml
git commit -m "fix(ci): restore workflow after gate proof"
git push
```

2. Confirm:

* CI reruns
* `lint-and-test` is green
* Merge becomes allowed *only after* checks pass
* If “Require branch up to date” is enabled, confirm GitHub requires update/rebase/merge from latest `main` when applicable.

### D) Optional: prove “conversation resolution” is enforced

1. Add a PR comment thread (e.g., “TODO: confirm X”).
2. Don’t resolve it → verify merge blocked.
3. Resolve conversation → verify merge allowed (assuming checks pass).

### E) Merge + cleanup

* Merge PR once it’s green and all conversations are resolved.
* Delete branch `cm/CM-M6-QA-07-ci-gate-proof` in GitHub.

---

## Expected success signals

* GitHub blocks merging while:

  * `lint-and-test` is failing OR missing
  * branch is behind `main` (if “up to date before merging” is enabled)
  * code review conversations are unresolved (if enabled)

* After fix:

  * `lint-and-test` passes
  * merge becomes possible (subject to branch-up-to-date + conversations resolved)

---

## Stop / rollback triggers

Stop the CM and report immediately if:

* A PR with failing `lint-and-test` can still be merged into `main`
* Required check name mismatch (e.g., GitHub expects a check that never appears)
* CI doesn’t run at all on PRs from branches
* Branch protection rules appear applied to the wrong branch or not applied to admins (if you intended admin enforcement)

Rollback path:

* Revert any changes to `.github/workflows/ci.yml` immediately
* Close the PR without merging if you accidentally touched application code
* Restore repo to last known good state on `main`

---

## Record-keeping / Audit Trail updates (mandatory)

Update these files:

1. **Fill in evidence in**
   `docs/dev/CM/M6/QA/CM-M6-QA-07_followup.md` (create if not present yet)

* PR URL
* CI run URL(s) for failing and passing runs
* Brief “gate proof” narrative (what failed, what blocked, what unlocked)

2. **Backfill missing evidence in CM-M6-QA-06 follow-up**

* Add the merged PR URL + CI run URL that correspond to the branch protection work.

3. **Update docs/dev/hygiene.md if wording is now stale**

* If it still says “manual step required” for protections, update to “applied” (and note date + which checks).

---

## Definition of Done

* [ ] A PR with an intentionally broken CI workflow is **blocked** from merging into `main`
* [ ] After restoring workflow, PR becomes mergeable only when `lint-and-test` is green
* [ ] Evidence URLs recorded (PR + CI run URLs, ideally for both fail and pass)
* [ ] Docs updated so they match actual GH settings (no “manual step required” leftovers)
* [ ] Test branch deleted

---

## Notes / Guardrails

* Keep the intentional failure confined to `.github/workflows/ci.yml` to avoid contaminating product code.
* Don’t “fix” extra lint/type issues in this CM. This is a **process proof + paperwork closure** mission.

