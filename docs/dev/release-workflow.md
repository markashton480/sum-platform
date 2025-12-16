# SUM Platform: Release Workflow (v1)

This document defines the v1 release workflow for SUM Platform, using **git tag pinning** as the distribution method.

> [!NOTE]
> v1 does **not** use a package registry (e.g., PyPI). Distribution is via direct git tag references.

---

## Version Numbering

SUM Core uses semantic versioning: `v0.MINOR.PATCH`

| Increment | When to use                                         | Example             |
| --------- | --------------------------------------------------- | ------------------- |
| **PATCH** | Bug fixes, documentation updates, test-only changes | `v0.1.0` → `v0.1.1` |
| **MINOR** | Additive features, non-breaking changes             | `v0.1.1` → `v0.2.0` |
| **MAJOR** | Breaking changes (deferred for v1)                  | Not used yet        |

---

## Pre-Release Checklist

Before creating a new tag, **all** of the following must pass:

| Check                 | Command                      |
| --------------------- | ---------------------------- |
| Linting               | `make lint`                  |
| Tests                 | `make test`                  |
| Boilerplate drift     | `make check-cli-boilerplate` |
| All checks (combined) | `make release-check`         |

If any check fails, resolve the issue before proceeding.

---

## Release Workflow

### Step 1: Choose the next version

Determine the appropriate version increment based on changes since the last tag:

```bash
# View existing tags
git tag -l "v*" --sort=-version:refname

# View changes since last tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Decide on the next version (e.g., `v0.1.2`).

### Step 2: Update boilerplate pinning

Set the `SUM_CORE_GIT_REF` in the canonical boilerplate to the new tag:

```bash
make release-set-core-ref REF=v0.1.2
```

This command:

1. Updates `boilerplate/requirements.txt` with the new tag
2. Automatically syncs the CLI boilerplate
3. Verifies the drift check passes

### Step 3: Run release checks

Verify all release prerequisites are met:

```bash
make release-check
```

This runs:

- `make lint`
- `make test`
- `make check-cli-boilerplate`

### Step 4: Commit release changes

```bash
git add boilerplate/requirements.txt cli/sum_cli/boilerplate/
git commit -m "chore:release-prep v0.1.2 boilerplate pinning"
```

### Step 5: Create and push the tag

```bash
# Create annotated tag
git tag -a v0.1.2 -m "Release v0.1.2"

# Push tag
git push origin v0.1.2

# Push commits (if not already)
git push origin main
```

### Step 6: Verify the release

After tagging, verify a fresh project can be scaffolded:

```bash
# Create a test project using the CLI
cd /tmp
sum init test-release-project

# Navigate and check
cd clients/test-release-project
sum check
```

---

## Quick Reference: Make Targets

| Target                                | Description                                |
| ------------------------------------- | ------------------------------------------ |
| `make release-check`                  | Run all pre-release checks                 |
| `make release-set-core-ref REF=<tag>` | Update boilerplate to pin to specified tag |
| `make sync-cli-boilerplate`           | Copy canonical boilerplate to CLI package  |
| `make check-cli-boilerplate`          | Verify CLI boilerplate matches canonical   |

---

## Relationship Between CLI and sum_core

```
┌─────────────────────────────────────────────────────────────────┐
│                         SUM Platform                            │
├─────────────────────┬───────────────────┬───────────────────────┤
│     sum_core        │    boilerplate    │        CLI            │
│   (tagged v0.x.y)   │ (pins to v0.x.y)  │ (bundles boilerplate) │
└─────────────────────┴───────────────────┴───────────────────────┘
```

- **`sum_core`** is the primary product, versioned via git tags
- **`boilerplate/`** is the canonical client project template, pins to a specific `sum_core` tag
- **CLI** bundles a copy of boilerplate for standalone use outside the monorepo

When releasing:

1. Tag `sum_core` first (or simultaneously with other changes)
2. Update boilerplate to pin to the new tag
3. Sync CLI boilerplate to match canonical

---

## Placeholder Configuration

The boilerplate uses placeholders that must be configured for production use:

| Placeholder        | Location           | Client action                   |
| ------------------ | ------------------ | ------------------------------- |
| `ORG/REPO`         | `requirements.txt` | Replace with actual GitHub repo |
| `SUM_CORE_GIT_REF` | `requirements.txt` | Replaced by release script      |
| `project_name`     | Various files      | Replaced by `sum init`          |

Clients cloning the boilerplate directly (not via CLI) must update `ORG/REPO` to the correct repository URL.

---

## Troubleshooting

### Drift check fails after release

If `make check-cli-boilerplate` fails:

1. Ensure the canonical boilerplate is what you expect
2. Run `make sync-cli-boilerplate` to update the CLI copy
3. Re-run `make check-cli-boilerplate`

### Tag already exists

If you need to re-tag (only acceptable before pushing):

```bash
git tag -d v0.1.2  # Delete local tag
git tag -a v0.1.2 -m "Release v0.1.2"  # Re-create
```

> [!WARNING]
> Never force-push tags that have already been pushed. Create a new patch version instead.

### Client project fails sum check after update

1. Verify the tag exists: `git ls-remote --tags origin`
2. Check the pinned URL is correct in `requirements.txt`
3. Reinstall dependencies: `pip install -r requirements.txt`
