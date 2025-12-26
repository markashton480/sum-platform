# Report: sum-core-public Directory Issue

**Date:** 2025-12-25
**Status:** Resolved
**Commits:** `d732730`, `626ff86`

---

## Summary

The `sum-core-public` directory was accidentally committed as a gitlink (submodule reference) to the `develop` branch, causing git divergence issues and a confusing rebase warning. This has been fixed and safeguards added.

---

## What Happened

### Symptoms

1. `git pull --ff-only` failed with divergence error (2 local vs 18 remote commits)
2. After `git rebase`, warning appeared: `unable to rmdir 'sum-core-public': Directory not empty`
3. Confusion about what `sum-core-public` is and why it exists

### Root Cause

Commit `a764ae8` ("docs: updated what broke last time") accidentally included `sum-core-public` as a gitlink:

```
160000 commit 45c203845d4cc4e79a9e08ecd7188cab93000978  sum-core-public
```

This happened because:
1. The `sum-core-public` directory existed (created by the sync script during v0.5.x releases)
2. It contains its own `.git` directory (it's a clone of the public repo)
3. A `git add` command picked it up and git tracked it as a submodule reference
4. There was no `.gitignore` entry to prevent this

---

## What is sum-core-public?

### Purpose

`sum-core-public` is a **working directory** created by `scripts/sync_to_public.py` during the release process. It's a local clone of the public `sum-core` repository used as a staging area for syncing files.

### How the Sync Works

```
sum-platform (private)              sum-core-public (local clone)         sum-core (public)
       │                                      │                                  │
       │  1. Copy files                       │                                  │
       │  (core/, boilerplate/, docs/public/) │                                  │
       └─────────────────────────────────────▶│                                  │
                                              │  2. Commit & push                │
                                              └─────────────────────────────────▶│
                                                                                 │
                                                                          3. Tag (vX.Y.Z)
```

### Directory Structure

```
sum-platform/                    ← private repo (.git → github.com/markashton480/sum-platform)
├── core/
├── boilerplate/
├── scripts/sync_to_public.py
│
└── sum-core-public/             ← separate repo (.git → github.com/markashton480/sum-core)
    ├── .git/                    ← different remote!
    ├── core/                    ← copied from sum-platform/core/
    ├── boilerplate/             ← copied from sum-platform/boilerplate/
    └── docs/                    ← copied from sum-platform/docs/public/
```

### Key Point

The `sum-core-public` directory is **not part of sum-platform's source tree**. It's a working artifact that:
- Is created by the sync script
- Has its own git history
- Pushes to a different remote (the public repo)
- Can be safely deleted and recreated

---

## Fixes Applied

### 1. Removed Gitlink from Git Tracking

```bash
git rm --cached sum-core-public
```

Commit: `d732730`

### 2. Added to .gitignore

```
sum-core-public/
```

This prevents accidental commits in the future.

### 3. Excluded from Linting Tools

Added `sum-core-public` to exclude patterns in `pyproject.toml`:

| Tool   | Config Key       | Purpose                              |
|--------|------------------|--------------------------------------|
| black  | `extend-exclude` | Skip formatting checks               |
| isort  | `skip_glob`      | Skip import sorting checks           |
| ruff   | `extend-exclude` | Skip linting (uses extend to keep defaults) |
| mypy   | `exclude`        | Skip type checking                   |

Commit: `626ff86`

---

## Current State

After fixes:
- `sum-core-public/` exists on disk (from v0.5.x releases)
- It is ignored by git (won't be accidentally committed)
- It is ignored by all linting tools (no duplicate checks)
- The sync script will continue to work normally

---

## Recommendations

### Option A: Keep sum-core-public (Current)

- Sync script reuses it on next release (faster)
- Takes up ~10MB disk space
- No action needed

### Option B: Delete and Let Sync Recreate

```bash
rm -rf sum-core-public
```

- Sync script will clone fresh on next release
- Slightly slower first sync
- Cleaner working directory

### Future Consideration

The sync script could be modified to use a temp directory or a location outside the repo (e.g., `/tmp/sum-core-sync`). This would avoid any confusion about the directory's purpose. See `scripts/sync_to_public.py` line 101:

```python
public_path = config.public_repo_path or (Path.cwd() / "sum-core-public")
```

Could be changed to:
```python
public_path = config.public_repo_path or (Path("/tmp") / "sum-core-public")
```

However, using `/tmp` has trade-offs (cleared on reboot, may cause permission issues in some environments).

---

## Related Files

- [scripts/sync_to_public.py](../../scripts/sync_to_public.py) - Sync script that creates sum-core-public
- [docs/dev/git_strategy.md](../git_strategy.md) - Branch model and conventions
- [docs/ops-pack/release-runbook.md](../../ops-pack/release-runbook.md) - Release process

---

## Lessons Learned

1. **Directories with `.git` subdirectories are dangerous** - Git will track them as submodule references if added
2. **Always check `git status` before committing** - The gitlink would have been visible
3. **Working artifacts should be in `.gitignore`** - Proactively ignore known build/sync artifacts
4. **Linting configs need to match `.gitignore`** - Otherwise tools may check ignored directories
