# Release Checklist

**Purpose:** Cut a new `sum_core` release and verify it works.  
**Frequency:** As needed (typically post-milestone or for critical fixes).  
**Reference:** [`docs/dev/release-workflow.md`](../dev/release-workflow.md)

---

## Pre-Flight Checks

**Stop here if any of these fail.**

### 1. Environment ready

```bash
# Activate virtualenv
source .venv/bin/activate

# Verify you're on main branch
git branch --show-current
# Expected: main

# Verify working directory is clean
git status
# Expected: nothing to commit, working tree clean
```

**Stop if:** not on `main`, or uncommitted changes exist (commit or stash first).

---

### 2. All checks pass

```bash
# Run release checks (lint + test + boilerplate drift)
# Note: make lint must provide a TRUTHFUL signal (no masked errors).
make release-check
```

**Stop if:** any check fails. Fix issues before proceeding. For non-blocking type debt, use `MYPY_SOFT=1 make release-check` only if explicitly approved for the release.

---

## Version Selection

### 3. Choose next version

**Versioning rules:**

- **PATCH** (e.g., `v0.5.1` → `v0.5.2`): Bug fixes, docs, test-only changes
- **MINOR** (e.g., `v0.5.2` → `v0.6.0`): Additive features, non-breaking changes
- **MAJOR** (deferred until 1.0+): Breaking changes

**View existing tags:**

```bash
git tag -l "v*" --sort=-version:refname | head -10
```

**View changes since last tag:**

```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

**Decide on next version:**  
Example: `v0.6.1`

**Write it down:**  
`NEXT_VERSION=v0.6.1`

---

## Frozen Line / Additive Evolution Guidance

**SUM Platform follows "frozen line" discipline:**

- **Frozen lines** (e.g., `0.5.x`): Only security/critical fixes allowed
- **Active line** (e.g., `0.6.x`): New features and non-breaking changes allowed
- **No backports** to frozen lines except security patches (requires explicit approval)

**When cutting a new MINOR version:**

- The previous MINOR line becomes **frozen**
- Example: Releasing `v0.6.0` freezes `0.5.x`

**When cutting a PATCH:**

- Must not introduce new features or breaking changes
- Bug fixes and documentation only

---

## Boilerplate Pinning

### 4. Update boilerplate to pin to new tag

```bash
# Set boilerplate core reference
make release-set-core-ref REF=v0.6.1
```

This command:

1. Updates `boilerplate/requirements.txt` with new tag
2. Syncs CLI boilerplate automatically
3. Verifies drift check passes

**Stop if:** drift check fails or errors occur.

---

### 5. Commit release prep

```bash
git add boilerplate/requirements.txt cli/sum_cli/boilerplate/
git commit -m "chore:release-prep v0.6.1 boilerplate pinning"
```

---

## Tagging

### 6. Create annotated tag

```bash
# Create tag
git tag -a v0.6.1 -m "Release v0.6.1"

# Verify tag exists locally
git tag -l "v0.6.1"
```

**Stop if:** tag creation fails or tag already exists remotely.

---

### 7. Push tag and commits

```bash
# Push tag
git push origin v0.6.1

# Push commits (if not already pushed)
git push origin main
```

**Stop if:** push fails (resolve conflicts or network issues).

---

## Post-Tag Verification

### 8. Verify fresh scaffolding works

```bash
# Create test project in /tmp
cd /tmp
sum init test-release-v0.6.1

# Navigate and check
cd test-release-v0.6.1
sum check
```

**Expected:**  
`sum check` passes with no errors.

**Stop if:** `sum check` fails or `sum init` errors.

---

### 9. Clean up test project

```bash
# Remove test project
cd /tmp
rm -rf test-release-v0.6.1
```

---

## Record Keeping

### 10. Update loop sites matrix

Open [`docs/ops-pack/loop-sites-matrix.md`](loop-sites-matrix.md) and record:

- Release version
- Release date
- What changed (brief summary)

---

### 11. Record what changed

**In release notes or internal log, document:**

- Version released: `v0.6.1`
- Date: `YYYY-MM-DD`
- Changes included:
  - Bug fixes / features / docs
  - Migration notes (if any)
  - Upgrade instructions (if special steps required)

**Optional:** Create a release note in `docs/dev/reports/releases/` if significant.

---

## Rollback (If Needed)

**If verification fails after pushing tag:**

❌ **DO NOT** delete or force-push tags that are already pushed.

✅ **DO** create a new patch version to fix the issue:

- Example: if `v0.6.1` is broken, release `v0.6.2` with fix

**Emergency rollback for deployed sites:**

- Use [`docs/ops-pack/rollback-runbook.md`](rollback-runbook.md)
- Redeploy previous known-good tag

---

## Checklist Summary

- [ ] Virtualenv activated
- [ ] On `main` branch, clean working tree
- [ ] `make release-check` passes
- [ ] Next version decided
- [ ] Boilerplate pinned: `make release-set-core-ref REF=vX.Y.Z`
- [ ] Release prep committed
- [ ] Tag created: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
- [ ] Tag pushed: `git push origin vX.Y.Z`
- [ ] Commits pushed: `git push origin main`
- [ ] Fresh project verified: `sum init` + `sum check` passes
- [ ] Test project cleaned up
- [ ] Loop sites matrix updated
- [ ] Release notes recorded

---

## Common Issues

### Drift check fails after `release-set-core-ref`

**Cause:** CLI boilerplate doesn't match canonical boilerplate.

**Fix:**

```bash
make sync-cli-boilerplate
make check-cli-boilerplate
```

---

### Tag already exists

**If you haven't pushed yet:**

```bash
git tag -d v0.6.1  # Delete local tag
git tag -a v0.6.1 -m "Release v0.6.1"  # Re-create
```

**If you already pushed:**  
❌ Never force-push. Create new patch version instead.

---

### `sum init` or `sum check` fails after release

**Possible causes:**

- Tag doesn't exist on remote: `git ls-remote --tags origin | grep v0.6.1`
- Pinned URL incorrect in boilerplate `requirements.txt`

**Fix:**

- Verify tag exists: `git push origin v0.6.1`
- Check `boilerplate/requirements.txt` has correct tag reference

---

**END OF CHECKLIST**
