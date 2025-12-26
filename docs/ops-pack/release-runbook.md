# Release Runbook

> **Single source of truth** for cutting releases.
>
> **Replaces:** `release-workflow.md`, `release-checklist.md`

---

## Overview

SUM Platform releases involve two repositories:

```
sum-platform (private)          sum-core (public)
       │                              │
       │  1. Prepare release          │
       │  2. PR develop → main        │
       │  3. Squash merge             │
       │                              │
       └──────── 4. Sync ────────────▶│
                                      │
                                      ▼
                              5. Tag (v0.6.0)
                                      │
                                      ▼
                              pip install works ✓
```

**Critical:** Tags are created on `sum-core` (public) because that's what `pip install` references.

---

## Pre-Flight Checklist

**Stop if any check fails.**

### 1. Environment Ready

```bash
# Activate virtualenv
source .venv/bin/activate

# Verify on develop branch
git branch --show-current
# Expected: develop

# Verify clean working tree
git status
# Expected: nothing to commit, working tree clean

# Pull latest
git pull origin develop
```

### 2. All Checks Pass

```bash
make release-check
```

This runs:
- `make lint` — Linting and type checking
- `make test` — Full test suite
- `make check-cli-boilerplate` — Boilerplate drift check

**Stop if any check fails.** Fix issues before proceeding.

---

## Version Selection

### 3. Determine Next Version

```bash
# View existing tags (from public repo)
git ls-remote --tags git@github.com:markashton480/sum-core.git | grep -o 'v[0-9]*\.[0-9]*\.[0-9]*' | sort -V | tail -10

# View changes since last release
git log $(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~20)..HEAD --oneline
```

### Version Rules

| Change Type | Increment | Example |
|-------------|-----------|---------|
| Bug fixes, docs, tests | PATCH | `v0.6.1` → `v0.6.2` |
| New features (non-breaking) | MINOR | `v0.6.0` → `v0.7.0` |
| Breaking changes | MAJOR | `v0.6.0` → `v1.0.0` |

**Decision:** `NEXT_VERSION=v0.6.0`

---

## Release Preparation

### 4. Update Boilerplate Pinning

```bash
make release-set-core-ref REF=v0.6.0
```

This command:
1. Updates `boilerplate/requirements.txt` to pin to `v0.6.0`
2. Syncs CLI boilerplate automatically
3. Verifies drift check passes

**Note:** The tag doesn't exist yet — this is intentional. The pinning is self-referential and resolves at install time.

### 5. Commit Release Prep

```bash
git add boilerplate/requirements.txt cli/sum_cli/boilerplate/
git commit -m "chore(release): prepare v0.6.0"
```

### 6. Push and Create PR

```bash
git push origin develop
```

Create PR: `develop` → `main`
- Title: `Release v0.6.0`
- Description: Summary of changes since last release

---

## Merge and Sync

### 7. Review and Merge PR

- Review changes
- CI must pass (`lint-and-test`)
- **Squash and merge**
- Commit message: `chore(release): v0.6.0`

### 8. Sync to Public Repository

After merge to main, the sync runs automatically via GitHub Actions.

**Manual trigger (if needed):**

```bash
# From sum-platform, on main branch
git checkout main
git pull origin main

# Run sync script
python scripts/sync_to_public.py --public-repo-url git@github.com:markashton480/sum-core.git --version v0.6.0
```

The sync:
1. Clones/updates `sum-core` locally (default working dir: `/tmp/sum-core-sync`, not inside the repo)
2. Copies allowed paths (`core/`, `boilerplate/`, `docs/public/` → `docs/`)
3. Commits changes
4. Pushes to `sum-core`

### 9. Create Tag on Public Repo

```bash
# Clone public repo (or cd to existing clone)
git clone git@github.com:markashton480/sum-core.git /tmp/sum-core-sync
cd /tmp/sum-core-sync

# Ensure on main and up to date
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.6.0 -m "Release v0.6.0"

# Push tag
git push origin v0.6.0
```

---

## Post-Release Verification

### 10. Verify Scaffolding Works

```bash
# Create test project
cd /tmp
sum init test-release-v0.6.0

# Verify project structure
cd test-release-v0.6.0
sum check
```

**Expected:** `sum check` passes with no errors.

### 11. Verify pip Install

```bash
# In a fresh virtualenv
python -m venv /tmp/test-venv
source /tmp/test-venv/bin/activate

# Install from tag
pip install "sum_core @ git+https://github.com/markashton480/sum-core.git@v0.6.0"

# Verify import
python -c "import sum_core; print(sum_core.__version__)"
```

### 12. Cleanup

```bash
# Remove test artifacts
rm -rf /tmp/test-release-v0.6.0
rm -rf /tmp/test-venv
rm -rf /tmp/sum-core-sync
```

---

## Record Keeping

### 13. Update Changelog

In `sum-platform`, update `CHANGELOG.md`:

```markdown
## [v0.6.0] - 2025-01-15

### Added
- Blog pages with categories
- Dynamic form builder

### Fixed
- Health endpoint Redis check

### Changed
- Updated Wagtail to 7.1
```

### 14. Update Private Repo Tag (Optional)

For reference, create matching tag on private repo:

```bash
cd /path/to/sum-platform
git checkout main
git pull origin main
git tag -a v0.6.0 -m "Release v0.6.0 (ref: sum-core)"
git push origin v0.6.0
```

---

## Rollback

### If Verification Fails After Tagging

**Never delete pushed tags.** Create a new patch version instead:

```bash
# Fix the issue
# Commit to develop
# PR to main
# Sync to public
# Tag as v0.6.1
```

### Emergency Rollback (Deployed Sites)

Redeploy previous known-good tag:

```bash
/srv/sum/bin/deploy.sh --site-slug mysite --ref v0.6.0 --domain example.com
```

---

## Checklist Summary

```
PRE-FLIGHT
[ ] Virtualenv activated
[ ] On develop branch, clean working tree
[ ] make release-check passes

VERSION
[ ] Next version decided: v_._._

PREPARATION
[ ] Boilerplate pinned: make release-set-core-ref REF=v_._._
[ ] Release prep committed
[ ] PR created: develop → main

MERGE & SYNC
[ ] PR reviewed and approved
[ ] CI passed
[ ] Squash merged to main
[ ] Sync to sum-core completed
[ ] Tag created on sum-core: git tag -a v_._._ -m "Release v_._._"
[ ] Tag pushed: git push origin v_._._

VERIFICATION
[ ] sum init test project works
[ ] sum check passes
[ ] pip install from tag works
[ ] Test artifacts cleaned up

RECORD
[ ] CHANGELOG.md updated
[ ] Private repo tag created (optional)
```

---

## Troubleshooting

### Drift Check Fails

```bash
make sync-cli-boilerplate
make check-cli-boilerplate
```

### Tag Already Exists

**Local only:**
```bash
git tag -d v0.6.0
git tag -a v0.6.0 -m "Release v0.6.0"
```

**Already pushed:** Create `v0.6.1` instead.

### Sync Fails

1. Check SSH access to both repos
2. Verify `sum-core` repo exists and you have push access
3. Check for merge conflicts in public repo
4. Run sync manually with verbose output

### sum init Fails After Release

1. Verify tag exists: `git ls-remote --tags origin | grep v0.6.0`
2. Check `boilerplate/requirements.txt` has correct URL
3. Verify public repo URL is correct (not private repo)

---

## Automation

Release automation is handled by:

- **GitHub Actions:** `.github/workflows/release-sync.yml` — Syncs to public repo on main merge
- **AI Agent:** See `RELEASE_AGENT_PROMPT.md` for Claude Code/Codex instructions

---

## Related Documents

- [`../dev/git_strategy.md`](../dev/git_strategy.md) — Branch model and conventions
- [`../release/prompts/release-prompt.md`](../release/prompts/release-prompt.md) — AI agent instructions
