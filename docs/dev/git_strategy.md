## Repository Model (Two-Repo)

SUM Platform uses a two-repository model:

| Repository | Visibility | Purpose |
|------------|------------|---------|
| `sum-platform` | **Private** | Development monorepo (CLI, docs, scripts, themes) |
| `sum-core` | **Public** | Distribution repo for `pip install` (core, boilerplate) |

```
┌─────────────────────────────────────┐     ┌─────────────────────────────────┐
│  sum-platform (PRIVATE)             │     │  sum-core (PUBLIC)              │
├─────────────────────────────────────┤     ├─────────────────────────────────┤
│  core/           ──────sync──────────────▶│  core/                          │
│  boilerplate/    ──────sync──────────────▶│  boilerplate/                   │
│  docs/public/    ──────sync──────────────▶│  docs/                          │
│                                     │     │                                 │
│  cli/             (excluded)        │     │  README.md                      │
│  docs/dev/        (excluded)        │     │  LICENSE                        │
│  docs/ops-pack/   (excluded)        │     │  pyproject.toml                 │
│  scripts/         (excluded)        │     │                                 │
│  .claude/         (excluded)        │     │  ◀── Tags: v0.5.0, v0.6.0      │
│  transcripts/     (excluded)        │     │                                 │
└─────────────────────────────────────┘     └─────────────────────────────────┘
```

**Critical:** Version tags are created on `sum-core` (public) because scaffolded projects pull from there.

---

## Branch Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Branch Flow                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   feat/*   ───PR───▶  develop  ───PR (squash)───▶  main  ───sync───▶ PUBLIC│
│   fix/*    ───PR───▶  develop                      ▲                       │
│   chore/*  ────────▶  develop (direct OK)          │                       │
│   docs/*   ────────▶  develop (direct OK)          │                       │
│                                                    tag                      │
│   hotfix/* ────────────────────PR──────────────────┘                       │
│            └──backport───▶ develop                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Branch Roles

| Branch | Protection | Purpose |
|--------|------------|---------|
| `main` | **Protected** (PR + CI required) | Stable, shippable, tagged releases |
| `develop` | Unprotected | Integration branch, staging for releases |
| `feat/*`, `fix/*`, etc. | N/A | Short-lived work branches |

### Protection Rules (GitHub)

**`main` branch:**
- ☑️ Require pull request before merging
- ☑️ Require status checks to pass (`lint-and-test`)
- ☑️ Require branches to be up to date
- ☑️ Require linear history (squash merges)
- ☑️ Do not allow bypassing

**`develop` branch:**
- No protection (intentional)
- Direct push allowed for chores, docs, transcripts
- PR by convention for code changes

---

## Naming Conventions

### Branch Names

Pattern: `<type>/<ticket>-<slug>`

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<ticket>-<slug>` | `feat/CM-042-blog-pages` |
| Bug fix | `fix/<ticket>-<slug>` | `fix/CM-051-health-check` |
| Chore | `chore/<slug>` | `chore/update-dependencies` |
| Docs | `docs/<slug>` | `docs/deployment-guide` |
| Refactor | `refactor/<scope>-<slug>` | `refactor/blocks-base-class` |
| Hotfix | `hotfix/<slug>` | `hotfix/xss-vulnerability` |

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

| Type | When to use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(blocks): add testimonial carousel` |
| `fix` | Bug fix | `fix(leads): correct email notification` |
| `chore` | Maintenance | `chore: update wagtail to 7.1` |
| `docs` | Documentation | `docs: add deployment guide` |
| `refactor` | Code restructure | `refactor(blocks): extract base class` |
| `test` | Test changes | `test(leads): add integration tests` |
| `ci` | CI/CD changes | `ci: add release sync workflow` |

**Release prep commits:** `chore(release): prepare v0.6.0`

---

## Day-to-Day Workflow

### Starting Work

```bash
# Update develop
git checkout develop
git pull origin develop

# Create feature branch
git checkout -b feat/CM-042-blog-pages
```

### During Development

```bash
# Make small, focused commits
git add -p
git commit -m "feat(blog): add listing page template"

# Push branch for backup/visibility
git push -u origin feat/CM-042-blog-pages
```

### Completing Work

```bash
# Update branch with latest develop
git fetch origin
git rebase origin/develop

# Push (force OK on feature branches)
git push --force-with-lease

# Open PR: feat/CM-042-blog-pages → develop
```

### Direct Push (Chores/Docs Only)

For non-code changes (transcripts, docs, minor config):

```bash
git checkout develop
git pull origin develop

# Make changes
git add .
git commit -m "docs: update readme"

git push origin develop
```

---

## Merge Strategy

### Feature → Develop

**Standard merge** (preserves commits):

```bash
# Via GitHub PR (recommended)
# Or locally:
git checkout develop
git merge --no-ff feat/CM-042-blog-pages
git push origin develop
```

### Develop → Main (Releases)

**Squash merge** (clean release history):

```bash
# Via GitHub PR with "Squash and merge"
# Commit message: "chore(release): v0.6.0"
```

### Hotfix → Main

**Standard merge** (preserves hotfix commit):

```bash
# Via GitHub PR
# Then backport to develop
git checkout develop
git cherry-pick <hotfix-commit>
git push origin develop
```

---

## Hotfix Process

For production emergencies only:

```bash
# 1. Branch from main
git checkout main
git pull origin main
git checkout -b hotfix/xss-vulnerability

# 2. Fix and commit
git commit -m "fix(security): patch XSS vulnerability"

# 3. PR to main (expedited review)
# 4. After merge, backport to develop
git checkout develop
git cherry-pick <hotfix-commit>
git push origin develop
```

---

## Version Tags

**Tags are created on `sum-core` (public repo)**, not `sum-platform`.

### Format

Semantic versioning: `v<MAJOR>.<MINOR>.<PATCH>`

| Increment | When | Example |
|-----------|------|---------|
| PATCH | Bug fixes, docs | `v0.5.1` → `v0.5.2` |
| MINOR | New features (non-breaking) | `v0.5.2` → `v0.6.0` |
| MAJOR | Breaking changes | `v0.6.0` → `v1.0.0` |

### Rules

- ✅ Tags are annotated: `git tag -a v0.6.0 -m "Release v0.6.0"`
- ✅ Tags point to commits on `main` (in public repo)
- ❌ Never delete or force-push tags once pushed
- ❌ Never create tags on `develop` or feature branches

---

## Recovery Procedures

### Committed to `main` by Accident

**If not pushed:**

```bash
git reset --soft HEAD~1
git checkout -b feat/accidental-work
git commit -m "feat(scope): description"
```

**If pushed:** Create revert commit (contact maintainer).

### Bad Commit Pushed

```bash
# Create revert commit
git revert <commit-hash>
git push origin develop
```

### Feature Branch Diverged

```bash
git checkout feat/my-feature
git fetch origin
git rebase origin/develop
# Resolve conflicts
git push --force-with-lease origin feat/my-feature
```

### Need to Re-tag (Local Only)

```bash
git tag -d v0.6.0
git tag -a v0.6.0 -m "Release v0.6.0"
```

**If tag already pushed:** Create new patch version instead (e.g., `v0.6.1`).

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start feature | `git checkout develop && git pull && git checkout -b feat/ticket-slug` |
| Update feature branch | `git fetch origin && git rebase origin/develop` |
| Push feature branch | `git push --force-with-lease origin feat/ticket-slug` |
| View recent tags | `git tag -l "v*" --sort=-version:refname \| head -10` |
| Changes since last tag | `git log $(git describe --tags --abbrev=0)..HEAD --oneline` |
| Check current branch | `git branch --show-current` |
| Check working tree | `git status` |

---

## Related Documents

- [`RELEASE_RUNBOOK.md`](RELEASE_RUNBOOK.md) — Complete release process
- [`RELEASE_AGENT_PROMPT.md`](RELEASE_AGENT_PROMPT.md) — AI agent instructions