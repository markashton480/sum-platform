# Two-Repo Setup Guide

> **One-time setup** for the sum-platform / sum-core two-repository model.

---

## Overview

This guide walks through setting up:
1. The public `sum-core` repository
2. Deploy keys for automated sync
3. GitHub Actions secrets
4. Initial sync and verification

---

## Prerequisites

- Admin access to your GitHub organization
- SSH key generation capability
- `gh` CLI installed (optional but recommended)

---

## Step 1: Create Public Repository

### Via GitHub UI

1. Go to https://github.com/organizations/markashton480/repositories/new
2. Repository name: `sum-core`
3. Description: "SUM Platform Core - Wagtail site boilerplate framework"
4. Visibility: **Public**
5. Initialize with: README (optional, will be overwritten)
6. Create repository

### Via CLI

```bash
gh repo create markashton480/sum-core \
    --public \
    --description "SUM Platform Core - Wagtail site boilerplate framework"
```

---

## Step 2: Generate Deploy Key

The sync workflow needs push access to `sum-core`. A deploy key is more secure than a PAT.

```bash
# Generate dedicated key pair
ssh-keygen -t ed25519 -C "sum-core-deploy" -f ~/.ssh/sum-core-deploy -N ""

# Display public key (add to sum-core)
cat ~/.ssh/sum-core-deploy.pub

# Display private key (add to sum-platform secrets)
cat ~/.ssh/sum-core-deploy
```

### Add Public Key to sum-core

1. Go to `https://github.com/markashton480/sum-core/settings/keys`
2. Click "Add deploy key"
3. Title: `sum-platform-sync`
4. Key: Paste the **public** key (`.pub` file contents)
5. ☑️ Allow write access
6. Add key

### Add Private Key to sum-platform Secrets

1. Go to `https://github.com/markashton480/sum-platform/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `SUM_CORE_DEPLOY_KEY`
4. Secret: Paste the **private** key contents
5. Add secret

---

## Step 3: Create PAT for GitHub Releases (Optional)

If you want the workflow to create GitHub Releases on `sum-core`:

1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Name: `sum-core-releases`
4. Scopes: `repo` (full control)
5. Generate token
6. Add to sum-platform secrets as `SUM_CORE_PAT`

---

## Step 4: Update Configuration

### In `scripts/sync_to_public.py`

Replace `ORG` with your actual organization:

```python
# Line ~47
public_repo_url: str = "git@github.com:markashton480/sum-core.git"
```

### In `.github/workflows/release-sync.yml`

Replace `ORG` with your actual organization (multiple locations):

```yaml
# Search and replace "markashton480/sum-core" with "markashton480/sum-core"
```

### In `boilerplate/requirements.txt`

Ensure it references the public repo:

```
sum_core @ git+https://github.com/markashton480/sum-core.git@SUM_CORE_GIT_REF
```

---

## Step 5: Initial Sync

Perform the first sync manually to populate `sum-core`:

```bash
# From sum-platform root
cd /path/to/sum-platform

# Activate virtualenv
source .venv/bin/activate

# Run sync without tagging (initial population)
python scripts/sync_to_public.py --public-repo-url

# Verify
cd /tmp/sum-core-sync/sum-core
git log --oneline -5
ls -la
```

---

## Step 6: Create Initial Tag

```bash
# Still in sum-core directory
cd /tmp/sum-core-sync/sum-core

# Create initial tag
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

---

## Step 7: Verify End-to-End

```bash
# Test pip install
python -m venv /tmp/verify-sum
source /tmp/verify-sum/bin/activate
pip install "sum_core @ git+https://github.com/markashton480/sum-core.git@v0.1.0"
python -c "import sum_core; print('✅ Success')"

# Cleanup
deactivate
rm -rf /tmp/verify-sum
```

---

## Step 8: Test Automated Workflow

Trigger a test release:

```bash
# In sum-platform
git checkout develop
echo "# Test" >> README.md
git add README.md
git commit -m "chore(release): test v0.1.1"
git push origin develop

# Create PR and merge to main
gh pr create --base main --head develop --title "Test release v0.1.1"
# Merge via UI with squash

# Watch the action
gh run watch
```

---

## Troubleshooting

### "Permission denied (publickey)"

- Verify deploy key is added to `sum-core` with write access
- Verify private key is in `sum-platform` secrets as `SUM_CORE_DEPLOY_KEY`
- Check key format (should start with `-----BEGIN OPENSSH PRIVATE KEY-----`)

### "Repository not found"

- Verify `sum-core` exists and is public
- Check the URL in `sync_to_public.py` matches exactly

### Workflow doesn't trigger

- Ensure commit message contains `chore(release)`
- Check that changed files match the path filters in the workflow
- Try manual trigger via Actions tab

### Tag already exists

- Never delete pushed tags
- Use next patch version instead

---

## Files to Remove After Migration

Once the new workflow is verified, remove these obsolete files:

```bash
# From sum-platform root
rm docs/dev/git_strategy.md
rm docs/dev/git-policy.md
rm docs/dev/release-workflow.md
rm docs/dev/release-checklist.md

# Keep these (consolidated versions)
# docs/dev/GIT_STRATEGY.md (new)
# docs/dev/RELEASE_RUNBOOK.md (new)
# docs/dev/RELEASE_AGENT_PROMPT.md (new)
```

---

## Secrets Summary

| Secret | Repository | Purpose |
|--------|------------|---------|
| `SUM_CORE_DEPLOY_KEY` | sum-platform | SSH key to push to sum-core |
| `SUM_CORE_PAT` | sum-platform | (Optional) Create GitHub Releases |

---

## Repository Settings Summary

### sum-core (public)

- Visibility: Public
- Default branch: `main`
- Deploy keys: `sum-platform-sync` (write access)

### sum-platform (private)

- Visibility: Private
- Default branch: `develop`
- Branch protection on `main`:
  - Require PR
  - Require status checks (`lint-and-test`)
  - Require linear history
- Secrets: `SUM_CORE_DEPLOY_KEY`, `SUM_CORE_PAT`

---

