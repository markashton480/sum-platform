# CM-M6-QA-06 Follow-up Report

**Task:** CI Enforcement + Branch Protection Gate  
**Status:** ✅ Complete (evidence backfill pending)  
**Date:** 2025-12-18

---

## Summary

This CM hardened the CI workflow and documented the branch protection runbook to make CI not just _present_ but _mandatory_ for merges to `main`.

---

## Changes Made

### 1. CI Workflow Hardening (`.github/workflows/ci.yml`)

| Change                              | Purpose                                       |
| ----------------------------------- | --------------------------------------------- |
| Added `workflow_dispatch:` trigger  | Enables manual CI runs for debugging          |
| Added `permissions: contents: read` | Minimal read-only access (security hardening) |
| Added `timeout-minutes: 15`         | Prevents hung/runaway jobs                    |
| Added cleanup step comments         | Documents why artifact removal is safe        |

**Commit:** `f21c316` on branch `cm/CM-M6-QA-06-ci-enforcement`

### 2. Documentation Updates (`docs/dev/hygiene.md`)

Added two new sections:

- **CI Hardening** — Table of all safety measures in the workflow
- **Branch Protection (Required Runbook)** — Step-by-step instructions for configuring branch protection on `main`

---

## Verification

| Check         | Result                             |
| ------------- | ---------------------------------- |
| `make lint`   | ✅ All checks passed               |
| `make test`   | ✅ 709 tests passed                |
| Branch pushed | ✅ `cm/CM-M6-QA-06-ci-enforcement` |

---

## Manual Steps (Evidence Capture)

The following steps require browser access and must be completed to finish the audit trail:

### Step 1: Create Pull Request

1. Go to: https://github.com/markashton480/sum_platform/pull/new/cm/CM-M6-QA-06-ci-enforcement
2. Title: `chore: harden CI workflow and add branch protection runbook`
3. Description:

   ```
   ## Summary
   - Add workflow_dispatch trigger for manual CI runs
   - Add minimal permissions (contents: read)
   - Add timeout-minutes: 15 to prevent hung jobs
   - Add CI Hardening section to hygiene.md
   - Add Branch Protection runbook to hygiene.md

   Ref: CM-M6-QA-06
   ```

4. Create the PR and observe CI checks

### Step 2: Verify CI Runs

Once the PR is created:

1. Navigate to the **Checks** tab on the PR
2. Confirm the `lint-and-test` job runs and passes
3. Note the workflow run URL for evidence

**Expected check name:** `lint-and-test`

### Step 3: Configure Branch Protection

After CI passes on the PR:

1. Go to **Settings → Branches** in the GitHub repository
2. Click **Add rule** (or edit existing `main` rule)
3. Set **Branch name pattern:** `main`
4. Enable:
   - ☑️ **Require a pull request before merging**
   - ☑️ **Require status checks to pass before merging**
     - Search and add: `lint-and-test`
   - ☑️ **Require branches to be up to date before merging** (recommended)
   - ☑️ **Require linear history** (optional)
5. Click **Create** or **Save changes**

### Step 4: Merge and Verify Gate

1. Merge the PR to `main`
2. Create a test branch with a deliberate failure
3. Open a PR — verify it's blocked from merging due to failing checks

**Note:** The explicit gate proof + evidence capture is tracked in CM-M6-QA-07.

---

## Contract Status

| Aspect                       | Status                                  |
| ---------------------------- | --------------------------------------- |
| CI workflow runs on PR/push  | ✅ Configured                           |
| CI workflow is hardened      | ✅ timeout, permissions, manual trigger |
| Branch protection documented | ✅ Runbook in `docs/dev/hygiene.md`     |
| Branch protection applied    | ⏳ **Evidence pending**                 |

---

## Evidence URLs (To Be Completed)

| Item                         | URL                                |
| ---------------------------- | ---------------------------------- |
| PR URL                       | _[paste merged PR URL]_             |
| CI Run URL                   | _[paste passing run URL]_           |
| Branch Protection Screenshot | _[optional link]_                   |
| Gate Proof PR (QA-07)        | _[paste QA-07 PR URL]_              |
| Gate Proof CI Run (QA-07)    | _[paste QA-07 failing/passing URLs]_ |

---

## Definition of Done

- [x] Workflow file updated with hardening measures
- [x] `make lint` passes
- [x] `make test` passes (709 tests)
- [x] Branch pushed to origin
- [x] Runbook documented in `docs/dev/hygiene.md`

- [ ] PR created (manual)
- [ ] CI runs and passes on PR (manual verification)
- [ ] Branch protection configured (manual)
- [ ] Evidence URLs filled

**Contract status: ENFORCED** once manual steps are complete.
