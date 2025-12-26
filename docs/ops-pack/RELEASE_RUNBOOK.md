# Release Runbook

> **Step-by-step process** for releasing a version.
> Assumes the 5-tier branch model from [`GIT_STRATEGY.md`](GIT_STRATEGY.md).

---

## Overview

```
release/X.Y.0 ──PR (squash)──▶ develop ──PR (squash)──▶ main ──sync──▶ sum-core ──tag──▶ vX.Y.0
```

**Two-repo model:**
- `sum-platform` (private): Development
- `sum-core` (public): Distribution — tags created here

---

## Prerequisites

Before starting a release:

- [ ] All Work Orders for this version are Done
- [ ] All feature branches merged to `release/X.Y.0`
- [ ] Version Declaration updated and complete
- [ ] Release audit scheduled

---

## Phase 1: Prepare Release Branch

### 1.1 Verify Release Branch

```bash
git checkout release/X.Y.0
git pull origin release/X.Y.0
git status  # Must be clean
```

### 1.2 Run Release Checks

```bash
make release-check
```

This runs:
- `make lint`
- `make test`
- `make check-cli-boilerplate`

**Stop if any check fails.**

### 1.3 Update Version Numbers

```bash
make release-set-core-ref REF=vX.Y.0
```

This updates:
- `boilerplate/requirements.txt`
- `cli/sum_cli/boilerplate/requirements.txt`

**Manually update:**
- `core/pyproject.toml` → `version = "X.Y.0"`
- `core/sum_core/__init__.py` → `__version__ = "X.Y.0"`
- `pyproject.toml` (root) → `version = "X.Y.0"`
- `CHANGELOG.md` → Add release entry

### 1.4 Commit Release Prep

```bash
git add -A
git commit -m "chore(release): prepare vX.Y.0"
git push origin release/X.Y.0
```

---

## Phase 2: Release Branch → Develop

### 2.1 Create PR

```bash
gh pr create \
  --base develop \
  --head release/X.Y.0 \
  --title "Release vX.Y.0" \
  --body "## Release vX.Y.0

### Features
- [Feature 1] (#WO-NNN)
- [Feature 2] (#WO-NNN)

### Verification
- \`make release-check\` ✓
- All Work Orders complete

Refs #NNN (Version Declaration)
"
```

### 2.2 Run Release Audit

Before merging, run the release audit:

```
Audit PR #NNN against Version Declaration #NNN
```

**Must pass before merge.**

### 2.3 Merge to Develop

- Merge strategy: **Squash**
- Commit message: `chore(release): vX.Y.0`

---

## Phase 3: Develop → Main

### 3.1 Update Develop

```bash
git checkout develop
git pull origin develop
```

### 3.2 Create PR to Main

```bash
gh pr create \
  --base main \
  --head develop \
  --title "Release vX.Y.0" \
  --body "## Release vX.Y.0

Production release of vX.Y.0.

### Changes
- [Summary of changes]

### Pre-merge Verification
- \`make release-check\` ✓
- Release audit passed
"
```

### 3.3 Merge to Main

- Merge strategy: **Squash**
- Commit message: `Release vX.Y.0`

---

## Phase 4: Sync to Public Repository

### 4.1 Update Local Main

```bash
git checkout main
git pull origin main
```

### 4.2 Run Sync

```bash
python scripts/sync_to_public.py \
  --public-repo-url git@github.com:markashton480/sum-core.git \
  --version vX.Y.0
```

This:
1. Clones/updates `sum-core` to `/tmp/sum-core-sync`
2. Copies allowed paths
3. Commits and pushes
4. Creates annotated tag
5. Pushes tag

---

## Phase 5: Verification

### 5.1 Verify Tag

```bash
git ls-remote --tags git@github.com:markashton480/sum-core.git | grep vX.Y.0
```

### 5.2 Test Scaffolding

```bash
cd /tmp
sum init test-release-vX.Y.0
cd test-release-vX.Y.0
sum check
```

### 5.3 Test pip Install

```bash
python -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate
pip install "sum_core @ git+https://github.com/markashton480/sum-core.git@vX.Y.0"
python -c "import sum_core; print(sum_core.__version__)"
deactivate
```

### 5.4 Cleanup

```bash
rm -rf /tmp/test-release-vX.Y.0
rm -rf /tmp/test-venv
rm -rf /tmp/sum-core-sync
```

---

## Phase 6: Post-Release

### 6.1 Update Version Declaration

Mark Version Declaration issue as Done.

### 6.2 Update CHANGELOG

Ensure `CHANGELOG.md` has the release entry (should already be done in Phase 1).

### 6.3 Clean Up Branches

```bash
# Delete release branch (optional, keeps history clean)
git push origin --delete release/X.Y.0

# Delete feature branches
git push origin --delete feature/forms
git push origin --delete feature/blog
# etc.
```

### 6.4 Create GitHub Release (Optional)

```bash
gh release create vX.Y.0 \
  --repo markashton480/sum-core \
  --title "Release vX.Y.0" \
  --notes "## Changes
- Feature 1
- Feature 2

## Installation
\`\`\`bash
pip install \"sum_core @ git+https://github.com/markashton480/sum-core.git@vX.Y.0\"
\`\`\`
"
```

---

## Checklist Summary

```
PHASE 1: Prepare Release Branch
[ ] release/X.Y.0 up to date
[ ] make release-check passes
[ ] Version numbers updated
[ ] Release prep committed

PHASE 2: Release → Develop
[ ] PR created
[ ] Release audit passed
[ ] Squash merged to develop

PHASE 3: Develop → Main  
[ ] PR created
[ ] Squash merged to main

PHASE 4: Sync to Public
[ ] Sync script run
[ ] Tag created on sum-core

PHASE 5: Verification
[ ] Tag exists
[ ] sum init + sum check works
[ ] pip install works

PHASE 6: Post-Release
[ ] Version Declaration closed
[ ] Branches cleaned up
[ ] GitHub Release created (optional)
```

---

## Hotfix Release

For emergency fixes to production:

### 1. Create Hotfix Branch

```bash
git checkout main
git pull origin main
git checkout -b hotfix/X.Y.Z
```

### 2. Fix and Test

```bash
# Make fix
make lint && make test
git commit -m "fix(<scope>): <description>"
```

### 3. Update Versions

```bash
# Update to X.Y.Z (patch increment)
# Same files as Phase 1.3
git commit -m "chore(release): prepare vX.Y.Z"
```

### 4. PR to Main

```bash
gh pr create --base main --head hotfix/X.Y.Z --title "Hotfix vX.Y.Z"
```

### 5. After Merge

- Sync to public repo
- Tag vX.Y.Z
- Cherry-pick to develop and any active release branches

```bash
git checkout develop
git cherry-pick <hotfix-commit>
git push origin develop
```

---

## Troubleshooting

### Tag Already Exists

Never delete pushed tags. Create next patch version instead.

### Sync Fails

1. Check SSH access to sum-core
2. Verify sum-core repo exists
3. Check for conflicts
4. Run sync manually with `--no-push` to debug

### Verification Fails After Tag

Do NOT delete tag. Fix issue and release as X.Y.1.

---

## Related Documents

- [`GIT_STRATEGY.md`](GIT_STRATEGY.md) — Branch model
- [`VERSION_DECLARATION_TEMPLATE.md`](VERSION_DECLARATION_TEMPLATE.md) — Version planning
- [`RELEASE_AUDIT_AGENT_PROMPT.md`](prompts/RELEASE_AUDIT_AGENT_PROMPT.md) — Audit instructions
