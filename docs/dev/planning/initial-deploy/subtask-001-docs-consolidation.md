# Subtask Template

**Title:** `GH-XXX: Consolidate deployment documentation into /infrastructure/`

---

## Parent

**Work Order:** #YYY — Initial Sage & Stone Deployment (v0.6.0)

---

## Branch

| Branch                             | Target                   |
| ---------------------------------- | ------------------------ |
| `feature/initial-deploy/001-docs`  | `feature/initial-deploy` |

```bash
git checkout feature/initial-deploy
git pull origin feature/initial-deploy
git checkout -b feature/initial-deploy/001-docs
git push -u origin feature/initial-deploy/001-docs
```

---

## Deliverable

This subtask will deliver:

- Move `docs/dev/deploy/vps-golden-path.md` to `infrastructure/docs/vps-golden-path.md`
- Create `infrastructure/docs/` directory if not exists
- Remove empty `docs/dev/deploy/` directory
- Update all internal documentation references to the new location
- Update `docs/ops-pack/deploy-runbook.md` reference path

---

## Boundaries

### Do

- Move vps-golden-path.md to infrastructure/docs/
- Create infrastructure/docs/ directory
- Update reference in deploy-runbook.md (line 4: `../dev/deploy/vps-golden-path.md`)
- Search for and update any other references to the old path
- Remove docs/dev/deploy/ directory after move

### Do NOT

- ❌ Do not modify the content of vps-golden-path.md (only move it)
- ❌ Do not change infrastructure/scripts/ or other infrastructure subdirectories
- ❌ Do not create new documentation — only reorganize existing
- ❌ Do not update SSH strategy — that's subtask #2

---

## Acceptance Criteria

- [ ] `infrastructure/docs/vps-golden-path.md` exists with identical content
- [ ] `docs/dev/deploy/` directory no longer exists
- [ ] `docs/ops-pack/deploy-runbook.md` references correct new path
- [ ] `grep -r "docs/dev/deploy" . --include="*.md"` returns no results (excluding this planning doc)
- [ ] `make lint` passes (no broken links in docs)

---

## Test Commands

```bash
make lint

# Verify no stale references
grep -r "docs/dev/deploy" . --include="*.md" | grep -v "initial-deploy"

# Verify file exists at new location
test -f infrastructure/docs/vps-golden-path.md && echo "OK" || echo "MISSING"

# Verify old directory removed
test -d docs/dev/deploy && echo "STILL EXISTS" || echo "OK - Removed"
```

---

## Files Expected to Change

```
infrastructure/docs/vps-golden-path.md      # New location
docs/dev/deploy/vps-golden-path.md          # Removed
docs/dev/deploy/                            # Directory removed
docs/ops-pack/deploy-runbook.md             # Reference update
```

---

## Dependencies

**Depends On:**

- [ ] None — this is the first subtask

**Blocks:**

- Subtask #2 (SSH strategy) can run in parallel
- Subtask #3 (VPS provisioning) should wait for docs to be finalized

---

## Risk

**Level:** Low

**Why:** Simple file move and reference updates. No code changes. Easy to verify.

---

## Labels

- [ ] `type:task`
- [ ] `agent:claude`
- [ ] `component:docs`
- [ ] `component:infrastructure`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.0`

---

## Project Fields

- [ ] Agent: claude
- [ ] Model Planned: claude-sonnet
- [ ] Component: docs, infrastructure
- [ ] Change Type: chore
- [ ] Risk: low
- [ ] Release: `v0.6.0`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
chore(docs): consolidate deploy docs into /infrastructure/

- Move vps-golden-path.md to infrastructure/docs/
- Update reference in deploy-runbook.md
- Remove empty docs/dev/deploy/ directory

Closes #XXX
```
