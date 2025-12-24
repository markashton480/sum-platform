## CM-M6-QA-08 — Establish `develop` Branch Workflow + Protections + Documentation

**Type:** Corrective Mission (QA)
**Milestone:** M6 / v0.6 stabilization
**Owner:** Agent (Ops/QA)
**Priority:** High (blocks clean QA + future CMs)
**Status:** Ready
**Related:** `git_strategy.md` update, branch protection rollout, CI required checks already configured on `main` (`lint-and-test`).  

---

### 1) Objective

Move SUM Platform from “branching off `main`” to a controlled workflow:

* `main` stays protected + stable
* `develop` becomes the default integration branch
* all ticket branches cut from `develop` and PR back into `develop`
* releases are promoted `develop → main` via PR
* document the workflow so every future ticket follows one standard path

This ticket is purely workflow + governance + documentation. No feature work.

---

### 2) Context / Why

* The repo is already at the point where “ad-hoc branching off `main`” causes confusion and weakens the value of branch protection and CI gates.
* You’ve started enforcing “Require status checks” and required check selection (`lint-and-test`) on `main`. This is good, but it needs a coherent branching model so work doesn’t pile directly onto `main`. 
* The existing `git_strategy.md` is explicitly lightweight and now outdated vs how you’re operating. 

---

### 3) Scope

#### In scope

1. Create `develop` from `main` and push to origin.
2. Set GitHub repo defaults:

   * make `develop` the default branch
   * protect `develop` with required checks + review gates (matching `main`, unless explicitly loosened)
3. Update `git_strategy.md` to define the new flow (develop integration model).
4. Add a short “How to work” snippet somewhere obvious (recommend: `README.md` or `docs/dev/README.md` if you have it).
5. Verify the workflow works end-to-end with a tiny “no-op” change PR into `develop`.

#### Out of scope (explicitly)

* Fixing the 40MB push issue / `.gitignore` hygiene (create a follow-on ticket once this is done)
* Any mypy/ruff/type cleanup beyond what’s needed for CI to function
* Theme/rendering work (M6-A), leads, etc.

---

### 4) Assumptions / Inputs Needed

If any of these are unknown during execution, the agent should **gather evidence** (commands/screenshots/links) and proceed safely:

* Current protected branch settings for `main`
* Current required check name(s) (expected: `lint-and-test`)
* Whether you want **squash merges** as the standard merge method (recommended)

---

### 5) Plan (Short)

1. Create and push `develop` from `main`.
2. Configure GitHub: default branch = `develop`; add branch protection for `develop` (CI + approvals + conversation resolution + up-to-date requirement).
3. Update `git_strategy.md` to the new model and commit it.
4. Create a small PR (from a branch off `develop`) into `develop` to validate gates behave as expected.
5. Record what changed (docs + ops notes).

---

### 6) Checklist & Commands

#### A) Preflight (local)

```bash
git status
git fetch --all --prune
git branch -vv
git log --oneline -n 20
```

**Evidence to capture in follow-up:** paste outputs of the above.

---

#### B) Create `develop` from `main`

```bash
git checkout main
git pull
git checkout -b develop
git push -u origin develop
```

**Success signal:** `origin/develop` exists and matches `main` HEAD.

---

#### C) GitHub configuration (manual steps, must be recorded)

In GitHub repo settings:

1. **Set default branch**

* Settings → Branches → Default branch → set to `develop`

2. **Branch protection for `develop`**
   Create a protection rule for `develop` with:

* ✅ Require a pull request before merging
* ✅ Require status checks to pass before merging

  * Required checks: **`lint-and-test`** (match what you enforced on `main`)
* ✅ Require branches to be up to date before merging
* ✅ Require conversation resolution before merging
* ✅ (Recommended) Require approvals (at least 1)

Optional but recommended:

* ✅ Restrict who can push to matching branches (ideally nobody, only PR merges)
* ✅ Do not allow force pushes

**Evidence to capture:** screenshots or a written list of toggles enabled + required check names.

> Note: Keep `main` protections as-is. This ticket does not loosen `main`.

---

#### D) Update `git_strategy.md`

* Replace the current lightweight contents with the new policy (develop integration model).
* Ensure naming patterns include your CM ticket IDs (e.g. `cm/CM-M6-QA-08-...`).

Commands:

```bash
git checkout develop
git pull

# edit git_strategy.md

git add git_strategy.md
git commit -m "docs(git): establish develop branch workflow and protections"
git push
```

---

#### E) Add “How we work” quick reference (pick one)

**Option 1 (recommended):** add to top of `README.md` a short section:

* “Branch from develop”
* “PR into develop”
* “Release PR develop → main”
* “Hotfix main → main then backport to develop”

Commands (if doing this):

```bash
git add README.md
git commit -m "docs(readme): add develop-based contribution flow"
git push
```

---

#### F) Validate the workflow with a tiny PR

1. Create a small branch from `develop`:

```bash
git checkout develop
git pull
git checkout -b chore/CM-M6-QA-08-validate-develop-flow
```

2. Make a tiny harmless change (example: add a dated line to a dev log, or a comment in docs).
3. Push:

```bash
git push -u origin chore/CM-M6-QA-08-validate-develop-flow
```

4. Open PR → **target `develop`**

* Confirm required checks run
* Confirm merge is blocked until checks pass + conversation resolved + up-to-date
* Merge using your chosen merge strategy (recommend squash)

**Evidence:** PR link + confirmation of check status + merge outcome.

---

### 7) Expected Success Signals

* `develop` exists on origin and is the default branch
* `develop` is protected and enforces:

  * `lint-and-test` passing
  * branch up-to-date before merge
  * conversation resolution
  * PR-only merges
* `git_strategy.md` clearly documents:

  * branch model (`main`, `develop`, feature/fix/chore/cm, hotfix)
  * release promotion `develop → main`
  * hotfix backport requirement
* A test PR into `develop` successfully demonstrates the gates working.

---

### 8) Stop / Rollback Triggers

Stop if any of these occur:

* `develop` protection prevents merging *everything* due to a misnamed/missing required check.
* CI is not firing on PRs to `develop` (workflow config might be branch-filtered).
* Setting `develop` as default breaks automation that assumes `main` (rare, but possible).

Rollback options:

* Revert default branch back to `main` temporarily.
* Disable `develop` protection rule temporarily **only long enough** to fix configuration (do not disable `main` protections).

---

### 9) Record-Keeping Requirements

Update/append these artefacts after completion:

* `docs/dev/CM/CM-M6-QA-08.md` (ticket spec — this text)
* `docs/dev/CM/CM-M6-QA-08_chat.md` (agent transcript)
* `docs/dev/CM/CM-M6-QA-08_followup.md` (work report) including:

  * command outputs from preflight
  * exact GitHub toggles enabled for `develop`
  * required check names
  * PR link used for validation
  * any surprises (“what broke / what was confusing / what to automate next”)

Also append to:

* `what-broke-last-time.md` if anything surprising happens during protection rollout (misnamed checks, blocked merges, etc.). 

---

### 10) Notes for the Agent

* Keep changes minimal and traceable.
* Don’t “fix extra stuff” while you’re in here.
* If CI doesn’t run on `develop` PRs, inspect `ci.yml` for branch filters (e.g., `on: push: branches:` or `pull_request:` restrictions) and propose a targeted follow-up ticket rather than making sweeping edits in this one. 

---

