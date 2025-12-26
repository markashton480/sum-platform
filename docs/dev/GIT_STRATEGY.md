# Git Strategy

> **Single source of truth** for branch model, naming conventions, and workflows.
> All other documentation references this document.

---

## Repository Model

SUM Platform uses a **two-repository model**:

| Repository | Visibility | Purpose |
|------------|------------|---------|
| [`sum-platform`](https://github.com/markashton480/sum-platform) | **Private** | Development monorepo |
| [`sum-core`](https://github.com/markashton480/sum-core) | **Public** | Distribution repo for `pip install` |

Releases sync from `sum-platform` to `sum-core`. Tags are created on `sum-core` because that's what client projects reference.

---

## Five-Tier Branch Model

```
main                              Stable, tagged releases
  ↑ PR (squash)
develop                           Stable integration, always deployable
  ↑ PR (squash)
release/X.Y.0                     Version integration, release candidate
  ↑ PR (merge --no-ff)
feature/<scope>                   Feature integration
  ↑ PR (squash)
feature/<scope>/<seq>-<slug>      Task branch (actual work happens here)
```

### Visual Flow

```
main ←────────────────────────────────────────────────────────────────┐
  │                                                                   │
  │                                                            PR (squash)
  │                                                                   │
develop ←─────────────────────────────────────────────────────┐       │
  │                                                           │       │
  │                                                    PR (squash)    │
  │                                                           │       │
release/0.7.0 ←───────────────────────────┐                   │       │
  │                                       │                   │       │
  │                              PR (merge --no-ff)           │       │
  │                                       │                   │       │
  ├── feature/forms ←──────────┐          │                   │       │
  │     │                      │          │                   │       │
  │     │              PR (squash)        │                   │       │
  │     │                      │          │                   │       │
  │     ├── feature/forms/001-definition ─┘                   │       │
  │     ├── feature/forms/002-fields                          │       │
  │     └── feature/forms/003-block                           │       │
  │                                                           │       │
  └── feature/blog ←───────────┐                              │       │
        │                      │                              │       │
        ├── feature/blog/001-category ─────────────────────────       │
        └── feature/blog/002-listing                                  │
                                                                      │
hotfix/security-fix ──────────────────────────────────────────────────┘
```

---

## Branch Roles

| Branch | Lifetime | Protection | Purpose |
|--------|----------|------------|---------|
| `main` | Permanent | PR + CI required | Production releases, tagged |
| `develop` | Permanent | PR + CI required | Stable integration, always deployable |
| `release/X.Y.0` | Per-version | PR + CI required | Version staging, release candidate |
| `feature/<scope>` | Per-feature | Unprotected | Feature integration point |
| `feature/<scope>/<task>` | Per-task | Unprotected | Actual implementation work |
| `hotfix/<slug>` | Per-fix | N/A | Emergency production fixes |

### Protection Rules (GitHub Settings)

**`main`:**
- ☑️ Require pull request before merging
- ☑️ Require status checks (`lint-and-test`)
- ☑️ Require linear history
- ☑️ Do not allow bypassing

**`develop`:**
- ☑️ Require pull request before merging
- ☑️ Require status checks (`lint-and-test`)
- ☑️ Require linear history

**`release/*`:**
- ☑️ Require pull request before merging
- ☑️ Require status checks (`lint-and-test`)

---

## Naming Conventions

### Branch Names

```
release/X.Y.0                           # Version branch (minor releases)
release/X.Y.Z                           # Patch release branch (if needed)

feature/<scope>                         # Feature integration branch
feature/<scope>/<seq>-<slug>            # Task branch

hotfix/<slug>                           # Emergency fix from main
```

**Examples:**

```
release/0.7.0
├── feature/forms
│   ├── feature/forms/001-definition
│   ├── feature/forms/002-fields
│   └── feature/forms/003-block
├── feature/blog
│   ├── feature/blog/001-category
│   └── feature/blog/002-listing
└── feature/legal
    └── feature/legal/001-cookies
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer: Closes #XXX]
```

| Type | When to use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(forms): add dynamic form block` |
| `fix` | Bug fix | `fix(leads): correct email validation` |
| `chore` | Maintenance | `chore(deps): update wagtail to 7.1` |
| `docs` | Documentation | `docs: add deployment guide` |
| `refactor` | Code restructure | `refactor(blocks): extract base class` |
| `test` | Test changes | `test(forms): add integration tests` |

---

## Merge Strategies

| From → To | Strategy | Rationale |
|-----------|----------|-----------|
| `feature/<scope>/<task>` → `feature/<scope>` | **Squash** | Clean feature history, one commit per task |
| `feature/<scope>` → `release/X.Y.0` | **Merge `--no-ff`** | Preserve feature boundary in history |
| `release/X.Y.0` → `develop` | **Squash** | One commit per version on develop |
| `develop` → `main` | **Squash** | Clean release history on main |
| `hotfix/*` → `main` | **Merge** | Preserve hotfix commit for cherry-pick |

---

## Workflow: Version Development

### 1. Start a Version

```bash
# From develop (must be up to date)
git checkout develop
git pull origin develop

# Create version branch
git checkout -b release/0.7.0
git push -u origin release/0.7.0
```

**GitHub:** Create milestone `v0.7.0` and Version Declaration issue.

### 2. Start a Feature

```bash
# From version branch
git checkout release/0.7.0
git pull origin release/0.7.0

# Create feature branch
git checkout -b feature/forms
git push -u origin feature/forms
```

**GitHub:** Create Work Order issue linked to milestone.

### 3. Start a Task

```bash
# From feature branch
git checkout feature/forms
git pull origin feature/forms

# Create task branch
git checkout -b feature/forms/001-definition
git push -u origin feature/forms/001-definition
```

**GitHub:** Create subtask issue linked to Work Order.

### 4. Complete a Task

```bash
# Ensure tests pass
make lint
make test

# Push and create PR
git push origin feature/forms/001-definition
```

**GitHub:** Create PR `feature/forms/001-definition` → `feature/forms` (squash merge).

### 5. Complete a Feature

When all tasks are merged to `feature/<scope>`:

```bash
git checkout feature/forms
git pull origin feature/forms
```

**GitHub:** Create PR `feature/forms` → `release/0.7.0` (merge `--no-ff`).

### 6. Complete a Version

When all features are merged to `release/X.Y.0`:

```bash
git checkout release/0.7.0
git pull origin release/0.7.0

# Run release checks
make release-check
```

**GitHub:** Create PR `release/0.7.0` → `develop` (squash merge).

### 7. Release to Production

When develop is ready for release:

```bash
git checkout develop
git pull origin develop
```

**GitHub:** Create PR `develop` → `main` (squash merge), then sync to public repo and tag.

---

## Workflow: Hotfix

For emergency production fixes:

```bash
# Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/security-fix

# Fix, test, commit
make lint && make test
git commit -m "fix(security): patch XSS vulnerability"

# PR to main
git push -u origin hotfix/security-fix
```

**After merge to main:**

```bash
# Backport to develop
git checkout develop
git cherry-pick <hotfix-commit>
git push origin develop

# Backport to active release branch (if exists)
git checkout release/0.7.0
git cherry-pick <hotfix-commit>
git push origin release/0.7.0
```

---

## Workflow: Patch Release

For non-emergency fixes to a released version:

```bash
# Branch from the tag
git checkout v0.7.0
git checkout -b release/0.7.1

# Fix, test, commit
# ... work ...

# PR to develop (patches go through develop first)
# Then PR develop → main
# Tag as v0.7.1
```

---

## GitHub Issue ↔ Branch Mapping

| Issue Type | Branch Pattern | PR Target |
|------------|----------------|-----------|
| Version Declaration | `release/X.Y.0` | `develop` |
| Work Order (Feature) | `feature/<scope>` | `release/X.Y.0` |
| Subtask (Task) | `feature/<scope>/<seq>-<slug>` | `feature/<scope>` |
| Bug (standalone) | `fix/<scope>-<slug>` | `develop` or `release/X.Y.0` |
| Hotfix | `hotfix/<slug>` | `main` |

---

## Version Tags

Tags are created on `sum-core` (public repo) after syncing.

### Format

Semantic versioning: `vMAJOR.MINOR.PATCH`

| Increment | When | Example |
|-----------|------|---------|
| PATCH | Bug fixes, docs | `v0.7.0` → `v0.7.1` |
| MINOR | New features | `v0.6.0` → `v0.7.0` |
| MAJOR | Breaking changes | `v0.9.0` → `v1.0.0` |

### Rules

- ✅ Tags are annotated: `git tag -a v0.7.0 -m "Release v0.7.0"`
- ✅ Tags point to commits on `main` (in public repo)
- ❌ Never delete or force-push tags once pushed
- ❌ Never create tags on feature or release branches

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start version | `git checkout develop && git checkout -b release/0.7.0` |
| Start feature | `git checkout release/0.7.0 && git checkout -b feature/forms` |
| Start task | `git checkout feature/forms && git checkout -b feature/forms/001-definition` |
| Update task branch | `git fetch origin && git rebase origin/feature/forms` |
| Push task | `git push --force-with-lease origin feature/forms/001-definition` |
| View version tags | `git tag -l "v*" --sort=-version:refname \| head -10` |

---

## Related Documents

- [`VERSION_DECLARATION_TEMPLATE.md`](VERSION_DECLARATION_TEMPLATE.md) — Milestone-level intent declaration
- [`PROJECT-PLANNING-GUIDELINES.md`](PROJECT-PLANNING-GUIDELINES.md) — Issue hierarchy and workflow
- [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md) — Release process
