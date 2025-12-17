# Git Policy (Operational)

**Purpose:** One-page operational Git policy for day-to-day work.  
**Reference:** [`docs/dev/git_strategy.md`](../dev/git_strategy.md)

---

## Default Branch Strategy

**Main branch:** `main`

**Rules:**

- ✅ `main` is always stable and shippable
- ✅ All work happens on feature branches
- ❌ Never commit directly to `main`
- ✅ Merge to `main` only when work is done and tests pass

---

## Feature Branches

**Pattern:** `feat/<ticket-or-description>`

**Example:**

```bash
git checkout -b feat/m6-001-blog-pages
```

**For different work types:**

- Feature: `feat/blog-category-filter`
- Bug fix: `fix/health-endpoint-redis-check`
- Chore: `chore/update-dependencies`
- Docs: `docs/deployment-guide`
- Refactor: `refactor/blocks-base-class`

---

## Commit Messages

**Use prefixes for clarity:**

| Type         | Pattern                          | Example                               |
| ------------ | -------------------------------- | ------------------------------------- |
| **Feature**  | `feature:<scope>-<description>`  | `feature:blocks-testimonial-carousel` |
| **Bug Fix**  | `fix:<scope>-<description>`      | `fix:leads-email-notification`        |
| **Hotfix**   | `hotfix:<description>`           | `hotfix:xss-vulnerability`            |
| **Chore**    | `chore:<description>`            | `chore:update-wagtail-7.1`            |
| **Docs**     | `docs:<description>`             | `docs:deployment-guide`               |
| **Refactor** | `refactor:<scope>-<description>` | `refactor:blocks-base-class`          |

**Keep commits small and focused.**

---

## Tags (Releases)

**When tags are created:**  
Only when cutting an official release (see [`release-checklist.md`](release-checklist.md)).

**Tag format:** `vMAJOR.MINOR.PATCH`

**Examples:**

- `v0.5.1` — patch release
- `v0.6.0` — minor release (new features)
- `v1.0.0` — major release (breaking changes)

**Rules:**

- ✅ Tags are annotated: `git tag -a v0.6.0 -m "Release v0.6.0"`
- ❌ Never delete or force-push tags once pushed
- ✅ Tags must point to commits on `main`

---

## Safe to Ship

**A commit is safe to ship when:**

1. ✅ All tests pass: `make test`
2. ✅ Linting passes: `make lint`
3. ✅ Boilerplate drift check passes: `make check-cli-boilerplate`
4. ✅ Changes reviewed (if multi-person team)
5. ✅ Breaking changes documented (if applicable)

**Before creating a release tag:**

Run `make release-check` to verify all gates pass.

---

## Merge Strategy

**For feature branches → main:**

```bash
# Update main
git checkout main
git pull origin main

# Merge feature branch
git merge --no-ff feat/my-feature

# Push
git push origin main
```

**Use `--no-ff`** (no fast-forward) to preserve branch history.

**Alternative (squash for small changes):**

```bash
git merge --squash feat/my-feature
git commit -m "feature:scope-description (squashed)"
```

---

## Recovering from Common Mistakes

### Committed to `main` by accident

**If not pushed yet:**

```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Create feature branch
git checkout -b feat/my-feature

# Commit again
git commit
```

**If already pushed:**  
Contact maintainer. May require revert commit or new branch.

---

### Need to undo a bad commit

**If not pushed:**

```bash
# Undo last commit, discard changes
git reset --hard HEAD~1
```

**If already pushed:**

```bash
# Create revert commit
git revert <commit-hash>
git push origin main
```

---

### Accidentally created tag

**If not pushed:**

```bash
git tag -d v0.6.1  # Delete local tag
```

**If already pushed:**  
❌ DO NOT delete. Create new patch version instead (e.g., `v0.6.2`).

---

### Feature branch diverged from main

```bash
# Update feature branch with latest main
git checkout feat/my-feature
git fetch origin
git rebase origin/main

# Resolve conflicts if any
# Then force-push feature branch (safe because it's not main)
git push --force-with-lease origin feat/my-feature
```

---

## Branch Protection (Future)

**When team > 1:**

- Enable branch protection on `main`
- Require PR reviews before merge
- Require status checks (CI) to pass
- Prevent force-push to `main`

**For now (solo/small team):**  
Discipline-based: don't push broken code to `main`.

---

## Rollback Strategy

**For deployed sites:**

Rollback = redeploy a previous known-good tag.

**Example:**

```bash
# Deploy previous version
/srv/sum/bin/deploy.sh --site-slug mysite --ref v0.5.0 --domain example.com
```

See [`rollback-runbook.md`](rollback-runbook.md) for full process.

---

## Release Discipline

**Before creating a release tag:**

1. ✅ Run `make release-check`
2. ✅ Update boilerplate pinning: `make release-set-core-ref REF=vX.Y.Z`
3. ✅ Commit boilerplate changes
4. ✅ Create annotated tag
5. ✅ Push tag and commits
6. ✅ Verify via `sum init` + `sum check`
7. ✅ Update loop sites matrix

See [`release-checklist.md`](release-checklist.md) for complete workflow.

---

## Summary

**Daily workflow:**

1. Create feature branch
2. Make small commits with clear messages
3. Merge to `main` when done and tests pass
4. Never commit directly to `main`

**Release workflow:**

1. Follow [`release-checklist.md`](release-checklist.md)
2. Create annotated tag on `main`
3. Never delete pushed tags

**Rollback:**

1. Redeploy previous tag
2. Document in "what broke" log

---

**For detailed Git strategy, see:** [`docs/dev/git_strategy.md`](../dev/git_strategy.md)
