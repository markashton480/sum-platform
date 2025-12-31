# Task

**Title:** `WO-SS-004: Triage and prioritize issues`

---

## Parent

**Work Order:** WO: Sage & Stone Deployment Review (v0.6.1)

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/sage-stone-review/004-triage-issues` | `fix/sage-stone-review` |

```bash
git checkout fix/sage-stone-review
git pull origin fix/sage-stone-review
git checkout -b fix/sage-stone-review/004-triage-issues
git push -u origin fix/sage-stone-review/004-triage-issues
```

---

## Deliverable

This task will deliver:

- Triaged and prioritized issue list
- Clear assignment of issues to milestones
- Documented rationale for prioritization decisions
- Updated findings document with final triage

---

## Boundaries

### Do

- Review all created issues from WO-SS-003
- Assign final priority labels
- Assign to appropriate milestones:
  - Critical/High → v0.6.1 (if fixable in time)
  - Medium/Low → v0.7.0 or later
- Document triage decisions and rationale
- Update findings document with triage summary
- Consider dependencies between issues

### Do NOT

- ❌ Do not fix issues (triage only)
- ❌ Do not change scope of existing v0.6.1 work orders
- ❌ Do not create new issues in this task
- ❌ Do not modify code

---

## Acceptance Criteria

- [ ] All issues have final priority assigned
- [ ] All issues assigned to milestones
- [ ] Triage decisions documented
- [ ] v0.6.1 scope remains manageable
- [ ] Findings document updated with triage summary
- [ ] Any scope changes communicated

---

## Test Commands

```bash
make lint
make test
```

---

## Files Expected to Change

```
docs/dev/reports/sage-stone-review/
└── findings.md                     # Modified: add triage summary
```

---

## Dependencies

**Depends On:**
- [ ] WO-SS-001: Complete staging site review
- [ ] WO-SS-002: Fix footer duplication bug
- [ ] WO-SS-003: Document findings and create issues

**Blocks:**
- Nothing — this is the final task

---

## Risk

**Level:** Low

**Why:**
- Triage/documentation only
- May result in additional v0.6.1 work (manageable)

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
docs(sage-stone): complete issue triage for deployment review

- Document triage decisions and rationale
- Assign issues to appropriate milestones
- Add triage summary to findings document

Closes #TBD
```

---

## Triage Guidelines

### v0.6.1 Inclusion Criteria

Include in v0.6.1 if:
- **Critical:** Site is broken or unusable
- **High + Quick Fix:** Major issue but simple fix (< 2 hours)
- **Blocking:** Prevents client from using site effectively

### v0.7.0 Deferral Criteria

Defer to v0.7.0 if:
- **Medium Priority:** Affects user experience but site is usable
- **Complex Fix:** Requires significant development effort
- **Enhancement:** Not a bug, but an improvement suggestion

### Beyond v0.7.0

Defer further if:
- **Low Priority:** Minor cosmetic issues
- **Nice-to-Have:** Enhancement requests
- **Requires Planning:** Needs architectural consideration

---

## Triage Summary Template

```markdown
## Triage Summary

### Included in v0.6.1

| Issue | Title | Priority | Rationale |
|-------|-------|----------|-----------|
| #NNN | Footer duplication | Critical | Already fixed in WO-SS-002 |
| #NNN | [Issue title] | High | [Why included] |

### Deferred to v0.7.0

| Issue | Title | Priority | Rationale |
|-------|-------|----------|-----------|
| #NNN | [Issue title] | Medium | [Why deferred] |

### Deferred to Future

| Issue | Title | Priority | Rationale |
|-------|-------|----------|-----------|
| #NNN | [Issue title] | Low | [Why deferred] |

## Notes

[Any additional context about triage decisions]
```
