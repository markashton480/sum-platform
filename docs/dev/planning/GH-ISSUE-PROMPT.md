---
description: "Execute a GitHub Issue: resolve branch hierarchy → implement → PR → green CI"
argument-hint: "ISSUE=<number> [context]"
allowed-tools: "Bash(gh:*),Bash(git:*),Bash(make:*),Bash(grep:*),Bash(cat:*)"
---

# GitHub Issue Execution

Execute issue #$1 end-to-end.

Please note: $2

---

## 1) Load Issue & Resolve Branch Hierarchy

### 1.1 Load the Issue

```bash
ISSUE=$1
gh issue view $ISSUE --json number,title,body,labels,milestone
```

Extract from body:

- Acceptance criteria
- Boundaries (Do / Do NOT sections)
- **Parent reference** (look for "Part of: #NNN" or "Parent Work Order: #NNN" or "Work Order: #NNN")

### 1.2 Find Parent Work Order

Look in the issue body for "Part of: #NNN" or "Work Order: #NNN". If found, that's the parent WO.

### 1.3 Resolve Base Branch

**If parent WO exists:**

- Load the parent WO and get its `component:*` label — that's the scope
- Base branch: `feature/<scope>`
- Your branch: `task/<scope>/issue-$ISSUE-<slug>`

**If no parent found:**

- Check the issue for a `component:*` label — that's the scope
- Base branch: `feature/<scope>`
- Your branch: `task/<scope>/issue-$ISSUE-<slug>`
- If no feature branch exists, stop and ask — the feature branch needs to be created first

### 1.4 Create Branch

```bash
git fetch origin
git checkout <base-branch>
git pull origin <base-branch>
git checkout -b <your-branch>
git push -u origin <your-branch>
```

---

## 2) Open Draft PR

```bash
gh pr create --draft --base <base-branch> --title "GH-$ISSUE: <summary>" --body "Closes #$ISSUE"
```

---

## 3) Implement

1. Read the acceptance criteria carefully
2. Check the "Do NOT" boundaries — respect them
3. Follow existing patterns in the codebase
4. Add/update tests for new functionality
5. Stay focused on this issue only

---

## 4) Validate

```bash
make lint
make test
```

**Fix failures properly.** Do not weaken tests or skip linting.

---

## 5) Commit

```bash
git add -p  # Stage intentionally, review each hunk
git commit -m "<type>(<scope>): <summary>

- What changed
- Why it changed

Closes #$ISSUE"
```

**Commit message types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`

---

## 6) Push & Update PR

```bash
git push

# Convert draft to ready
gh pr ready

# Update PR description
gh pr edit --body "## Summary
<What changed>

## Testing
- \`make lint\` ✓
- \`make test\` ✓

Closes #$ISSUE"
```

---

## 7) Monitor CI

```bash
gh pr checks --watch
```

If failures:

```bash
gh run view <run-id> --log-failed
# Fix, commit, push, repeat
```

---

## 8) Handle Review Feedback

### 8.1 Check Copilot Feedback (if present)

- Review each suggestion
- Implement valid suggestions
- For deferrable items: create sub-issue with `deferred` label
- Resolve all conversations

### 8.2 Check Claude Feedback (if present)

- Review each suggestion
- Implement valid suggestions
- For deferrable items: create sub-issue with `deferred` label
- Reply to Claude explaining why if not implementing

### 8.3 Resolve Conversations

```bash
OWNER=markashton480
REPO=sum-platform
PR=$(gh pr view --json number --jq '.number')

# Get unresolved thread IDs
THREAD_IDS=$(gh api graphql -f query='
  query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        reviewThreads(first:100) {
          nodes { id isResolved }
        }
      }
    }
  }' -F owner="$OWNER" -F repo="$REPO" -F pr="$PR" \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false) | .id')

# Resolve them
for TID in $THREAD_IDS; do
  gh api graphql -f query='
    mutation($id:ID!) {
      resolveReviewThread(input:{threadId:$id}) {
        thread { id }
      }
    }' -F id="$TID" >/dev/null
done
```

---

## 9) Second Pass

After addressing feedback:

1. Push changes
2. Wait for CI: `gh pr checks --watch`
3. Check for new feedback
4. Repeat until no new feedback

---

## 10) Done Criteria

Issue is complete when:

- [ ] PR open with green CI
- [ ] `Closes #$ISSUE` in PR body
- [ ] First pass feedback addressed
- [ ] Second pass feedback addressed
- [ ] All conversations resolved
- [ ] Any follow-up issues created (with `deferred` label)
- [ ] Ready for review

**Do not merge** — reviewer or Work Order owner handles merge.

---

## Quick Reference

### Branch Resolution Summary

| Issue Type   | Parent  | Base Branch       | Task Branch Pattern               |
| ------------ | ------- | ----------------- | --------------------------------- |
| Subtask      | WO #100 | `feature/<scope>` | `task/<scope>/issue-<num>-<slug>` |
| Task (no WO) | None    | `feature/<scope>` | `task/<scope>/issue-<num>-<slug>` |

### Creating Sub-Issues

If you need to defer work:

```bash
# Ensure extension installed
gh extension list | grep -E "sub-issue" || gh extension install yahsan2/gh-sub-issue

# Create sub-issue
gh sub-issue create --parent $ISSUE --repo markashton480/sum-platform \
  --title "Follow-up: <description>" \
  --body "<details>"

# Add deferred label
gh issue edit <new-issue> --add-label "deferred"
```
