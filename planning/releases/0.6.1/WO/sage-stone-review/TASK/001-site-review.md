# Task

**Title:** `WO-SS-001: Complete staging site review`

---

## Parent

**Work Order:** WO: Sage & Stone Deployment Review (v0.6.1)

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/sage-stone-review/001-site-review` | `fix/sage-stone-review` |

```bash
git checkout fix/sage-stone-review
git pull origin fix/sage-stone-review
git checkout -b fix/sage-stone-review/001-site-review
git push -u origin fix/sage-stone-review/001-site-review
```

---

## Deliverable

This task will deliver:

- Comprehensive review of Sage & Stone staging site
- Documented list of all identified issues
- Categorized issues by severity and type
- Screenshots/evidence for visual issues
- Review checklist completion

---

## Boundaries

### Do

- Review all pages on https://sage-and-stone.lintel.site
- Test all forms and interactive elements
- Check responsive behavior on mobile/tablet/desktop
- Verify navigation and linking
- Test accessibility basics
- Document all issues found
- Take screenshots of visual issues
- Categorize issues by severity (Critical/High/Medium/Low)

### Do NOT

- ❌ Do not fix issues in this task (document only)
- ❌ Do not modify any code
- ❌ Do not create GitHub issues yet (next task)
- ❌ Do not change staging environment

---

## Acceptance Criteria

- [ ] All pages reviewed
- [ ] All forms tested
- [ ] Responsive behavior checked
- [ ] Navigation verified
- [ ] All issues documented with severity
- [ ] Screenshots captured for visual issues
- [ ] Review findings report created

---

## Test Commands

```bash
make lint
make test

# Manual testing on staging site
# https://sage-and-stone.lintel.site
```

---

## Files Expected to Change

```
docs/dev/reports/sage-stone-review/
└── findings.md                     # New: review findings
```

---

## Dependencies

**Depends On:**
- [ ] None — this is the first task

**Blocks:**
- WO-SS-002: Fix footer duplication bug
- WO-SS-003: Document findings and create issues
- WO-SS-004: Triage and prioritize issues

---

## Risk

**Level:** Low

**Why:**
- Review task only, no code changes
- May identify more issues than expected

---

## Labels

- [ ] `type:task`
- [ ] `component:themes`
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
docs(sage-stone): add staging site review findings

- Document all identified issues from staging review
- Categorize by severity and type
- Include screenshots for visual issues
- Create comprehensive review report

Closes #TBD
```

---

## Review Checklist

### Pages to Review

- [ ] Homepage
- [ ] About page
- [ ] Services page(s)
- [ ] Portfolio/Work page
- [ ] Contact page
- [ ] Blog index
- [ ] Blog posts (sample)
- [ ] Legal pages (Privacy, Terms)

### Functionality to Test

- [ ] Contact form submission
- [ ] Navigation links
- [ ] CTA buttons
- [ ] Mobile menu
- [ ] Footer links
- [ ] Blog pagination/filtering
- [ ] Image loading

### Responsive Breakpoints

- [ ] Mobile (320px)
- [ ] Mobile (375px)
- [ ] Tablet (768px)
- [ ] Desktop (1024px)
- [ ] Large Desktop (1440px)

### Known Issues to Verify

- [ ] Footer duplication bug (already identified)
