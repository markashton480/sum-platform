---
description: "Execute a GitHub Issue: resolve branch hierarchy → implement → PR → green CI"
argument-hint: "<issue-number> [additional context]"
allowed-tools: "Bash(gh:*),Bash(git:*),Bash(make:*),Bash(grep:*)"
---

# GitHub Issue Execution

**Issue:** #$1
$2

---

## 1) Setup: Load Issue & Create Branch

Run this entire block — it determines the correct branch hierarchy and creates your working branch.

```bash
set -euo pipefail
ISSUE="$1"

# Validate input
if ! [[ "$ISSUE" =~ ^[0-9]+$ ]]; then
  echo "❌ Issue must be numeric (got: $ISSUE)" >&2
  exit 1
fi

# Get repo context dynamically
REPO_FULL="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
OWNER="${REPO_FULL%/*}"
REPO="${REPO_FULL#*/}"

# Load issue details
TITLE="$(gh issue view "$ISSUE" --json title --jq '.title | gsub("[\\r\\n]+"; " ")')"
SLUG="$(gh issue view "$ISSUE" --json title --jq '
  .title
  | ascii_downcase
  | gsub("[^a-z0-9]+"; "-")
  | gsub("(^-+|-+$)"; "")
  | .[0:30]
')"

# Fallback if slug is empty (title was only symbols)
[ -z "$SLUG" ] && SLUG="no-title"

# Find parent Work Order (check body for "Part of: #NNN" pattern)
PARENT_WO="$(
  gh issue view "$ISSUE" --json body --jq '.body // ""' \
  | grep -m1 -oE '(Part of|Parent Work Order|Work Order):?[[:space:]]*#?[0-9]+' \
  | grep -oE '[0-9]+' \
  || true
)"

# Fetch remote branches
git fetch origin --prune

# Helper function
remote_exists() {
  git show-ref --verify --quiet "refs/remotes/origin/$1"
}

# Determine base branch and task branch
if [ -n "$PARENT_WO" ]; then
  # This is a subtask under a Work Order
  SCOPE="$(gh issue view "$PARENT_WO" --json labels --jq '
    [.labels[].name | select(startswith("component:"))]
    | first // ""
    | sub("^component:"; "")
    | ascii_downcase
    | gsub("[^a-z0-9]+"; "-")
    | gsub("(^-+|-+$)"; "")
  ')"

  # Validate scope
  if [ -z "$SCOPE" ] || ! [[ "$SCOPE" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    echo "❌ Could not determine valid scope from WO #$PARENT_WO"
    echo "   Work Order must have a component:* label (got: '$SCOPE')"
    exit 1
  fi

  BASE_BRANCH="feature/$SCOPE"

  if ! remote_exists "$BASE_BRANCH"; then
    echo "❌ Feature branch '$BASE_BRANCH' does not exist"
    echo ""
    echo "Create it first from the release branch:"
    echo "  git checkout release/X.Y.0"
    echo "  git checkout -b $BASE_BRANCH"
    echo "  git push -u origin $BASE_BRANCH"
    exit 1
  fi

  # Task branches use task/<scope>/... to avoid Git ref conflict with feature/<scope>
  BRANCH="task/$SCOPE/issue-$ISSUE-$SLUG"

else
  # Standalone issue — branch from develop (or default branch)
  if remote_exists "develop"; then
    BASE_BRANCH="develop"
  else
    BASE_BRANCH="$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')"
  fi

  SCOPE="$(gh issue view "$ISSUE" --json labels --jq '
    [.labels[].name | select(startswith("component:"))]
    | first // "component:core"
    | sub("^component:"; "")
    | ascii_downcase
    | gsub("[^a-z0-9]+"; "-")
    | gsub("(^-+|-+$)"; "")
  ')"

  # Fallback if scope is empty or invalid
  if [ -z "$SCOPE" ] || ! [[ "$SCOPE" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
    SCOPE="core"
  fi

  IS_BUG="$(gh issue view "$ISSUE" --json labels --jq 'any(.labels[].name; . == "type:bug")')"

  if [ "$IS_BUG" = "true" ]; then
    BRANCH="fix/$SCOPE-issue-$ISSUE-$SLUG"
  else
    BRANCH="feat/$SCOPE-issue-$ISSUE-$SLUG"
  fi
fi

# Idempotence: check if branch already exists
if remote_exists "$BRANCH"; then
  echo "ℹ️  Branch '$BRANCH' already exists, checking out"
  git checkout "$BRANCH"
  git pull origin "$BRANCH"
else
  # Create and push branch
  git checkout "$BASE_BRANCH"
  git pull origin "$BASE_BRANCH"
  git checkout -b "$BRANCH"
  git push -u origin "$BRANCH"
  echo ""
  echo "✅ Branch created: $BRANCH"
fi

echo "   Base: $BASE_BRANCH"
echo "   Issue: #$ISSUE"
[ -n "$PARENT_WO" ] && echo "   Work Order: #$PARENT_WO"
echo ""

# Idempotence: check if PR already exists for this branch
EXISTING_PR="$(gh pr list --head "$BRANCH" --json number,url --jq '.[0].url // ""')"

if [ -n "$EXISTING_PR" ]; then
  echo "ℹ️  PR already exists: $EXISTING_PR"
else
  # Create draft PR
  gh pr create \
    --draft \
    --base "$BASE_BRANCH" \
    --title "GH-$ISSUE: [WIP] ${TITLE:0:60}" \
    --body "Work in progress for #$ISSUE

## Summary
<!-- To be completed -->

## Testing
- [ ] \`make lint\`
- [ ] \`make test\`

Closes #$ISSUE"

  echo ""
  echo "✅ Draft PR created"
fi
```

---

## 2) Implement

1. Read acceptance criteria from the issue carefully
2. Respect "Do NOT" boundaries — stay in scope
3. Follow existing codebase patterns
4. Add/update tests for new functionality
5. Focus only on this issue

---

## 3) Validate

```bash
make lint
make test
```

**Fix failures properly.** Do not weaken tests.

---

## 4) Commit

```bash
git add -p
git commit -m "<type>(<scope>): <summary>

- What changed
- Why it changed

Closes #$1"
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

---

## 5) Push & Finalize PR

```bash
git push origin HEAD

gh pr ready

gh pr edit --body "## Summary
<What changed — be specific>

## Implementation Notes
<Decisions, tradeoffs, things to note>

## Testing
- \`make lint\` ✓
- \`make test\` ✓

Closes #$1"
```

---

## 6) Monitor CI

```bash
gh pr checks --watch
```

If failures:

```bash
gh run view <run-id> --log-failed
# Fix, commit, push, repeat
```

---

## 7) Handle Review Feedback

For each review comment (Copilot, Claude, human):

- **Implement** if valid and in scope
- **Defer** if valid but out of scope → create sub-issue with `deferred` label
- **Decline** if not applicable → reply explaining why

Resolve conversations after addressing:

```bash
REPO_FULL="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"
OWNER="${REPO_FULL%/*}"
REPO="${REPO_FULL#*/}"
PR="$(gh pr view --json number --jq '.number')"

THREAD_IDS="$(gh api graphql -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:100) {
          nodes { id isResolved }
        }
      }
    }
  }' -F owner="$OWNER" -F repo="$REPO" -F pr="$PR" \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false) | .id')"

for TID in $THREAD_IDS; do
  gh api graphql -f query='
    mutation($id:ID!) {
      resolveReviewThread(input:{threadId:$id}) { thread { id } }
    }' -F id="$TID" >/dev/null
done
```

---

## 8) Second Pass

After addressing feedback:

1. Push changes
2. `gh pr checks --watch`
3. Check for new feedback
4. Repeat until clean

---

## 9) Done Criteria

- [ ] PR targets correct base branch
- [ ] CI green
- [ ] `Closes #$1` in PR body
- [ ] All feedback addressed
- [ ] All conversations resolved
- [ ] Follow-up issues created if needed

**Do not merge** — reviewer or WO owner handles merge.

**Note:** `Closes #` only auto-closes when merged to the default branch. Ensure the final PR to `develop`/`main` includes the closing reference.

---

## Quick Reference

### Branch Naming

| Issue Type         | Parent  | Base Branch                   | Your Branch                       |
| ------------------ | ------- | ----------------------------- | --------------------------------- |
| Subtask            | WO #NNN | `feature/<scope>`             | `task/<scope>/issue-<num>-<slug>` |
| Standalone Bug     | None    | `develop` (or default branch) | `fix/<scope>-issue-<num>-<slug>`  |
| Standalone Feature | None    | `develop` (or default branch) | `feat/<scope>-issue-<num>-<slug>` |

**Why `task/` not `feature/<scope>/`?** Git cannot have both `feature/forms` (branch) and `feature/forms/001-...` (sub-branch) — they conflict as ref paths. Task branches use `task/<scope>/...` to avoid this.

**Standalone base branch:** Uses `develop` if it exists, otherwise falls back to the repo's default branch.

### Creating Sub-Issues

```bash
REPO_FULL="$(gh repo view --json nameWithOwner --jq '.nameWithOwner')"

gh extension list | grep -q "sub-issue" || gh extension install yahsan2/gh-sub-issue

gh sub-issue create \
  --parent "$1" \
  --repo "$REPO_FULL" \
  --title "Follow-up: <description>" \
  --body "<details>"

gh issue edit <new-issue-number> --add-label "deferred"
```
