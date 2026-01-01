# Task

**Title:** `WO-CI-004: Update developer handbook`

---

## Parent

**Work Order:** #462 (WO: CI & Documentation Enhancements)
**Tracking Issue:** #476

---

## Branch

| Branch | Target |
|--------|--------|
| `chore/ci-docs-improvements/004-handbook-update` | `chore/ci-docs-improvements` |

```bash
git checkout chore/ci-docs-improvements
git pull origin chore/ci-docs-improvements
git checkout -b chore/ci-docs-improvements/004-handbook-update
git push -u origin chore/ci-docs-improvements/004-handbook-update
```

---

## Deliverable

This task will deliver:

- Updated developer handbook with current information
- Integrated Lead.form_data documentation
- Updated CI workflow documentation
- General documentation freshness check

---

## Boundaries

### Do

- Review and update HANDBOOK.md for accuracy
- Integrate Lead.form_data documentation
- Document CI fast-path behavior
- Document Claude review workflow
- Fix any outdated information
- Update code examples if needed

### Do NOT

- ❌ Do not restructure documentation
- ❌ Do not add new major sections
- ❌ Do not modify other docs files
- ❌ Do not change documentation tooling

---

## Acceptance Criteria

- [ ] HANDBOOK.md reviewed and updated
- [ ] Lead.form_data section integrated
- [ ] CI workflow changes documented
- [ ] No outdated information remains
- [ ] All code examples verified to work
- [ ] Documentation builds without errors

---

## Test Commands

```bash
make lint
make test

# Verify code examples work
# Run any code snippets from HANDBOOK.md
```

---

## Files Expected to Change

```
docs/
└── dev/
    └── HANDBOOK.md             # Modified
```

---

## Dependencies

**Depends On:**
- [ ] WO-CI-001: Implement docs-only CI fast-path
- [ ] WO-CI-002: Configure Claude review permissions
- [ ] WO-CI-003: Document Lead.form_data structure

**Blocks:**
- Nothing — this is the final task

---

## Risk

**Level:** Low

**Why:**
- Documentation only
- Consolidating existing work

---

## Labels

- [ ] `type:task`
- [ ] `component:docs`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

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
docs(dev): update developer handbook for v0.6.1

- Integrate Lead.form_data documentation
- Document CI fast-path for docs-only PRs
- Document Claude review workflow
- Update outdated sections

Closes #TBD
```
