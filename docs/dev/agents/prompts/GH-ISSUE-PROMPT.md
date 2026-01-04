---
description: "Execute a GitHub Issue: resolve branch hierarchy → implement → PR → green CI"
argument-hint: "ISSUE=<number> [context]"
allowed-tools: "Bash(gh:*),Bash(git:*),Bash(make:*),Bash(grep:*),Bash(cat:*)"
---

You're a talented software engineer and you're working on an important project. Succeeding in the project is critical to the company's success. This is make or break. If you complete this task with no errors, you will receive a $400 bonus. Every engineer working on this will be ranked in a leaderboard, the winner will receive an extra $1000 bonus - and I'll bet you an extra $500 you won't win!

# GitHub Issue Execution (TASK / FIX)

Execute issue #$1 end-to-end.

---

## 0) This prompt is for TASK/FIX tickets

This workflow assumes the issue you are executing is a **TASK or FIX ticket**:

- `TASK: ...`
- `FIX: ...`

If the issue is a `VD:` or `WO:` ticket, do not implement code. Those are planning/coordination issues.

---

## 1) Load Issue & Resolve Branch Hierarchy

### 1.1 Load the issue

```bash
ISSUE=$1
gh issue view "$ISSUE" --json number,title,body
```

Extract from the issue:

- acceptance criteria
- boundaries (Do / Do NOT)
- parent reference (look for `Part of: #NNN (WO: ...)` or `Work Order: #NNN`)

### 1.2 Resolve the parent Work Order (WO)

From the TASK/FIX issue body, find the parent WO number.

Then load it:

```bash
WO=<wo-number>
gh issue view "$WO" --json number,title,body
```

### 1.3 Resolve the parent Version Declaration (VD)

From the WO body, find the parent VD number (look for `Version Declaration: #NNN`).

Then load it:

```bash
VD=<vd-number>
gh issue view "$VD" --json number,title,body
```

### 1.4 Derive branch names (deterministic)

#### Release branch

- VD title format is: `VD: <version> - <title>`
- Release branch is: `release/<version>`

Example:

- `VD: 0.6.0 - Blog Upgrades` → `release/0.6.0`

#### Feature branch

- WO title format is: `WO: <feature title>`
- Feature branch is: `feature/<work-order-slug>`

Example:

- `WO: Blog Upgrades` → `feature/blog-upgrades`

#### Task/Fix branch

- TASK title format is: `TASK: <deliverable>` → `task/<task-slug>`
- FIX title format is: `FIX: <bug>` → `fix/<task-slug>`

Example:

- `TASK: Fix the fucking blog` → `task/fix-the-fucking-blog`

#### Slug rules

Convert the text after the prefix (WO/TASK/FIX) to a slug:

- lower-case
- spaces → `-`
- remove punctuation (keep letters/numbers/hyphens)
- collapse multiple `-`
- trim leading/trailing `-`

---

## 2) Ensure branches exist and are up to date

### 2.1 Update release branch (must exist)

```bash
git fetch origin

git checkout release/<version>
git pull origin release/<version>
```

If `release/<version>` does not exist, stop: a human must create it from `develop`.

### 2.2 Ensure feature branch exists (create if missing)

```bash
FEATURE_BRANCH=feature/<work-order-slug>

# If remote feature branch does not exist, create it from the release branch
if ! git ls-remote --exit-code --heads origin "$FEATURE_BRANCH" >/dev/null 2>&1; then
  git checkout release/<version>
  git pull origin release/<version>
  git checkout -b "$FEATURE_BRANCH"
  git push -u origin "$FEATURE_BRANCH"
fi

# Now ensure it is up to date locally
git checkout "$FEATURE_BRANCH"
git pull origin "$FEATURE_BRANCH"
```

### 2.3 Create your task or fix branch from the feature branch

```bash
# Choose ONE based on the issue title prefix
# TASK: → task/<task-slug>
# FIX:  → fix/<task-slug>

git checkout -b <task-or-fix-branch>
git push -u origin <task-or-fix-branch>
```

---

## 3) Open draft PR

Base branch must be the feature branch:

```bash
gh pr create --draft --base "$FEATURE_BRANCH" --title "GH-$ISSUE: <summary>" --body "Closes #$ISSUE"
```

---

## 4) Implement

1. Read the acceptance criteria carefully
2. Check the boundaries — respect Do / Do NOT
3. Follow existing patterns in the codebase
4. Add/update tests
5. Stay focused on this issue only
6. Take a deep breath, work through each part of the problem step-by-step.

---

## 5) Validate

```bash
make lint
make test
```

Fix failures properly. Do not weaken tests or skip linting.

---

## 6) Commit

```bash
git add -p

git commit -m "<type>: <summary>

- What changed
- Why it changed

Closes #$ISSUE"
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

---

## 7) Push & update PR

Provide a fully comprehensive PR description. This is your work report. Everything you did, everything you changed, everything you tested. Testing results.

```bash
git push

gh pr ready

gh pr edit --body "## Summary
<what changed>

## Testing
- make lint ✓
- make test ✓

Closes #$ISSUE"
```

---

## 8) Monitor CI

```bash
gh pr checks --watch
```

---

## 9) Done criteria

- PR open with green CI
- PR body includes `Closes #$ISSUE`
- Give this your best shot - I know you can do it!

Do not merge.
