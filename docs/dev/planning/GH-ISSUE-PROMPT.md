---
description: "Execute a GitHub Issue: resolve branch hierarchy → implement → PR → green CI"
argument-hint: "<issue-number> [additional context]"
allowed-tools: "Bash(gh:*),Bash(git:*),Bash(make:*),Bash(grep:*)"
---

# GitHub Issue Execution

**Issue:** #$1
$2

---

## Step 1: Setup — Load Issue & Create Branch

Run this block to determine branch hierarchy and create your working branch.

```bash
set -euo pipefail
ISSUE="$1"

# Validate input
if ! [[ "$$ISSUE" =~ ^[0-9]+$$ ]]; then
  echo "❌ Issue must be numeric" >&2
  exit 1
fi

# Get repo context dynamically
REPO_FULL="$$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
OWNER="$${REPO_FULL%/*}"
REPO="$${REPO_FULL#*/}"

# Load issue details
TITLE="$$(gh issue view "$$ISSUE" --json title --jq '.title')"
SLUG="$$(gh issue view "$$ISSUE" --json title --jq '
  .title
  | ascii_downcase
  | gsub("[^a-z0-9]+"; "-")
  | gsub("(^-+|-+$$)"; "")
  | .[0:30]
')"

# Fallback if slug is empty
[ -z "$$SLUG" ] && SLUG="no-title"

# Find parent Work Order
PARENT_WO="$$(
  gh issue view "$$ISSUE" --json body --jq '.body // ""' \
  | grep -m1 -oE '(Part of|Parent Work Order|Work Order):?[[:space:]]*#?[0-9]+' \
  | grep -oE '[0-9]+' \
  || true
)"

# Fetch remote branches
git fetch origin --prune

# Helper function
remote_exists() {
  git show-ref --verify --quiet "refs/remotes/origin/$$1"
}

# Determine base branch and task branch
if [ -n "$$PARENT_WO" ]; then
  # Subtask under a Work Order
  SCOPE="$$(gh issue view "$$PARENT_WO" --json labels --jq '
    [.labels[].name | select(startswith("component:"))]
    | first // ""
    | sub("^component:"; "")
    | ascii_downcase
    | gsub("[^a-z0-9]+"; "-")
    | gsub("(^-+|-+$$)"; "")
  ')"

  if [ -z "$$SCOPE" ] || ! [[ "$$SCOPE" =~ ^[a-z0-9][a-z0-9-]*$$ ]]; then
    echo "❌ Could not determine valid scope from WO #$$PARENT_WO"
    exit 1
  fi

  BASE_BRANCH="feature/$$SCOPE"

  if ! remote_exists "$$BASE_BRANCH"; then
    echo "❌ Feature branch '$$BASE_BRANCH' does not exist"
    echo "Create it first from the release branch"
    exit 1
  fi

  BRANCH="task/$$SCOPE/issue-$$ISSUE-$$SLUG"
else
  # Standalone issue
  if remote_exists "develop"; then
    BASE_BRANCH="develop"
  else
    BASE_BRANCH="$$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')"
  fi

  SCOPE="$$(gh issue view "$$ISSUE" --json labels --jq '
    [.labels[].name | select(startswith("component:"))]
    | first // "component:core"
    | sub("^component:"; "")
    | ascii_downcase
    | gsub("[^a-z0-9]+"; "-")
  ')"

  [ -z "$$SCOPE" ] && SCOPE="core"

  IS_BUG="$$(gh issue view "$$ISSUE" --json labels --jq 'any(.labels[].name; . == "type:bug")')"

  if [ "$$IS_BUG" = "true" ]; then
    BRANCH="fix/$$SCOPE-issue-$$ISSUE-$$SLUG"
  else
    BRANCH="feat/$$SCOPE-issue-$$ISSUE-$$SLUG"
  fi
fi

# Idempotence: check if branch exists
if remote_exists "$$BRANCH"; then
  echo "ℹ️  Branch '$$BRANCH' already exists, checking out"
  git checkout "$$BRANCH"
  git pull origin "$$BRANCH"
else
  git checkout "$$BASE_BRANCH"
  git pull origin "$$BASE_BRANCH"
  git checkout -b "$$BRANCH"
  git push -u origin "$$BRANCH"
  echo "✅ Branch created: $$BRANCH"
fi

echo "   Base: $$BASE_BRANCH"
echo "   Issue: #$$ISSUE"
[ -n "$$PARENT_WO" ] && echo "   Work Order: #$$PARENT_WO"

# Idempotence: check if PR exists
EXISTING_PR="$$(gh pr list --head "$$BRANCH" --json url --jq '.[0].url // ""')"

if [ -n "$$EXISTING_PR" ]; then
  echo "ℹ️  PR already exists: $$EXISTING_PR"
else
  gh pr create \
    --draft \
    --base "$$BASE_BRANCH" \
    --title "GH-$$ISSUE: [WIP] $${TITLE:0:60}" \
    --body "Work in progress for #$$ISSUE

## Summary
<!-- To be completed -->

## Testing
- [ ] \`make lint\`
- [ ] \`make test\`

Closes #$$ISSUE"
  echo "✅ Draft PR created"
fi
```

---

## Step 2: Implement

1. Read acceptance criteria from the issue
2. Respect "Do NOT" boundaries
3. Follow existing codebase patterns
4. Add/update tests
5. Focus only on this issue

---

## Step 3: Validate

```bash
make lint
make test
```

Fix failures properly. Do not weaken tests.

---

## Step 4: Commit

```bash
git add -p
git commit -m "<type>(<scope>): <summary>

- What changed
- Why it changed

Closes #$1"
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

---

## Step 5: Push & Finalize PR

```bash
git push origin HEAD
gh pr ready
gh pr edit --body "## Summary
<What changed — be specific>

## Implementation Notes
<Decisions, tradeoffs, notes>

## Testing
- \`make lint\` ✓
- \`make test\` ✓

Closes #$1"
```

---

## Step 6: Monitor CI

```bash
gh pr checks --watch
```

If failures, check logs with `gh run view <run-id> --log-failed`, fix, and push.

---

## Step 7: Handle Review Feedback

For each comment: **Implement**, **Defer** (create sub-issue), or **Decline** (reply why).

Then resolve conversations:

```bash
REPO_FULL="$$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
OWNER="$${REPO_FULL%/*}"
REPO="$${REPO_FULL#*/}"
PR="$$(gh pr view --json number --jq '.number')"

THREAD_IDS="$$(gh api graphql -f query='
  query($$owner:String!, $$repo:String!, $$pr:Int!) {
    repository(owner:$$owner, name:$$repo) {
      pullRequest(number:$$pr) {
        reviewThreads(first:100) { nodes { id isResolved } }
      }
    }
  }' -F owner="$$OWNER" -F repo="$$REPO" -F pr="$$PR" \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false) | .id')"

for TID in $$THREAD_IDS; do
  gh api graphql -f query='
    mutation($$id:ID!) {
      resolveReviewThread(input:{threadId:$$id}) { thread { id } }
    }' -F id="$$TID" >/dev/null
done
```

---

## Step 8: Done Criteria

- [ ] PR targets correct base branch
- [ ] CI green
- [ ] `Closes #$1` in PR body
- [ ] All feedback addressed
- [ ] All conversations resolved

**Do not merge** — reviewer handles merge.

---

## Quick Reference

| Issue Type         | Base Branch       | Your Branch                 |
| ------------------ | ----------------- | --------------------------- |
| Subtask (has WO)   | `feature/<scope>` | `task/<scope>/issue-N-slug` |
| Standalone Bug     | `develop`         | `fix/<scope>-issue-N-slug`  |
| Standalone Feature | `develop`         | `feat/<scope>-issue-N-slug` |
