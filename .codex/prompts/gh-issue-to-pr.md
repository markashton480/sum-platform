---
description: "End-to-end GitHub Issue execution: branch → implement → PR → green checks → address reviews → resolve threads"
argument-hint: "ISSUE=<number> [BASE=<branch>] [TYPE=feature|fix|chore|docs|refactor|hotfix] [SCOPE=<scope>] [DRAFT=true|false]"
---

You are working inside a git repo that uses GitHub Issues + PRs and the SUM Platform conventions:
- Default working branch is `develop` when present; branch naming: feature/<scope>-<description>, fix/<scope>-<description>, etc. :contentReference[oaicite:2]{index=2}
- Definition of Done includes: acceptance criteria met, tests passing, conventions respected, docs updated when needed. :contentReference[oaicite:3]{index=3}
- Run validation: `make test` and `make lint` (and fix failures; do not weaken tests to “make it green”). :contentReference[oaicite:4]{index=4}

Your task: Take GitHub Issue #$ISSUE and drive it to a PR with green checks and resolved review conversations.

## 0) Preconditions
1) Confirm we’re in the correct repo and working tree is clean:
   - `git status --porcelain` should be empty (or explicitly account for any changes before proceeding).
2) Ensure `gh` is authenticated and points at the right repo:
   - `gh auth status`
   - `gh repo view`

## 1) Load Issue Context (source of truth)
1) Fetch issue details:
   - `gh issue view $ISSUE --json number,title,body,labels,assignees,milestone,url --jq '.'`
2) Extract:
   - Problem statement + acceptance criteria (from body; if missing, infer minimal criteria and document assumptions in the PR).
   - Labels to help infer TYPE/SCOPE (bug → fix, docs → docs, etc.).
3) If issue is ambiguous, write a short plan first (bullets) before coding.

## 2) Choose base branch + create work branch
1) Determine base branch:
   - If BASE was provided, use `$BASE`.
   - Else prefer `develop` if it exists; otherwise use repo default branch:
     - `git show-ref --verify --quiet refs/remotes/origin/develop && echo develop || gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`
2) Determine TYPE:
   - If TYPE provided, use `$TYPE`.
   - Else infer from labels/title: bug/fix → `fix`, docs → `docs`, refactor → `refactor`, otherwise `feature`.
3) Determine SCOPE:
   - If SCOPE provided, use `$SCOPE`.
   - Else infer from code area mentioned in issue (e.g., blocks/pages/leads/cli/core) and keep it short and stable.
4) Create branch name using SUM naming conventions (keep it readable):
   - Pattern: `<TYPE>/<SCOPE>-issue-$ISSUE-<short-slug>`
   - Slugify from issue title (lowercase, hyphens).
5) Create branch from base and pull latest:
   - `git fetch origin`
   - `git checkout <base>`
   - `git pull --ff-only`
   - `git checkout -b <branch>`

## 3) Implement the issue
1) Locate relevant modules/files. Prefer existing patterns over inventing new ones.
2) Implement changes to satisfy acceptance criteria.
3) Add/update tests for non-trivial logic. Keep coverage expectations in mind (aim ≥80% on critical paths). :contentReference[oaicite:5]{index=5}
4) Update docs if needed (README/docs/*) when behavior/interfaces change. :contentReference[oaicite:6]{index=6}

## 4) Validate locally (must be green)
Run:
- `make test`
- `make lint` :contentReference[oaicite:7]{index=7}
Fix failures properly (do not delete/cripple tests just to pass).

## 5) Commit (conventional + closes issue)
1) Stage changes intentionally.
2) Commit message:
   - Use Conventional Commits and include scope where sensible. :contentReference[oaicite:8]{index=8}
   - Include `Closes #$ISSUE` in the commit body (or PR body).
Example:
- `feat($SCOPE): <short summary>`
Body includes:
- what changed
- how tested (`make test`, `make lint`)
- `Closes #$ISSUE`

## 6) Push + open PR
1) Push:
   - `git push -u origin HEAD`
2) Create PR targeting base branch:
   - If DRAFT=true → add `--draft`
   - `gh pr create --base <base> --head <branch> --title "<issue title>" --body "$(cat <<'BODY'
Summary:
- <what you changed>

Testing:
- make test
- make lint

Closes #$ISSUE
BODY
)"`
3) Capture PR number + URL for later steps:
   - `gh pr view --json number,url --jq '.'`

## 7) Monitor CI checks and fix until green
1) Watch checks:
   - `gh pr checks --watch`
2) If failures occur:
   - Inspect failing run: `gh run list --limit 5`
   - View logs: `gh run view <run-id> --log-failed`
   - Fix root cause, re-run local checks (`make test`, `make lint`), commit, push.
3) Repeat until all checks are green.

## 8) Address reviews + resolve conversations
1) Pull feedback:
   - `gh pr view --comments`
   - `gh pr view --json reviews,reviewRequests --jq '.'`
2) Apply requested changes, commit, push, re-check CI (`gh pr checks --watch`).
3) Resolve review threads where possible (GraphQL mutation exists: resolveReviewThread). :contentReference[oaicite:9]{index=9}
   - If thread resolution via CLI is blocked by permissions/ownership, leave a comment noting what was addressed and flag remaining threads for manual resolution in the UI.

Optional helper (attempt to resolve resolvable threads):
- Get PR number:
  - `PR_NUMBER=$(gh pr view --json number --jq .number)`
- Get owner/name:
  - `FULL=$(gh repo view --json nameWithOwner --jq .nameWithOwner)`  # e.g. owner/repo
- Then run a small script to resolve threads you can resolve:
  - Use `gh api graphql` to list `reviewThreads` on the PR and call `resolveReviewThread` for unresolved ones where `viewerCanResolve=true`.

## 9) Done criteria
You are finished when:
- PR is open and CI is green
- All review feedback is addressed (or explicitly documented if deferred)
- Conversations are resolved (or explicitly called out if they require manual UI resolution)
- The PR description includes what changed + how tested + `Closes #$ISSUE`
