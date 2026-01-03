# Task

**Title:** `WO-THEME-004: Visual regression testing and QA`

---

## Parent

**Work Order:** #461 (WO: Theme A Critical Fixes)
**Tracking Issue:** #466

---

## Branch

| Branch | Target |
|--------|--------|
| `task/theme-a-critical-issues/004-visual-qa` | `fix/theme-a-critical-issues` |

```bash
git checkout fix/theme-a-critical-issues
git pull origin fix/theme-a-critical-issues
git checkout -b task/theme-a-critical-issues/004-visual-qa
git push -u origin task/theme-a-critical-issues/004-visual-qa
```

---

## Deliverable

This task will deliver:

- Complete visual QA verification of all fixes
- Lighthouse audit results (≥90 all metrics)
- Cross-browser testing report
- Verification that no regressions were introduced
- Sign-off documentation for theme fixes

---

## Boundaries

### Do

- Run Lighthouse audits on key pages
- Test in Chrome, Firefox, Safari, Edge
- Verify all fixes from previous tasks
- Document any remaining issues
- Create visual QA sign-off report
- Test on staging environment

### Do NOT

- ❌ Do not make CSS fixes in this task (report issues for next iteration)
- ❌ Do not add new tests beyond visual verification
- ❌ Do not modify production code
- ❌ Do not deploy to production

---

## Acceptance Criteria

- [ ] Lighthouse Performance ≥90
- [ ] Lighthouse Accessibility ≥90
- [ ] Lighthouse Best Practices ≥90
- [ ] Lighthouse SEO ≥90
- [ ] Chrome testing passed
- [ ] Firefox testing passed
- [ ] Safari testing passed
- [ ] No visual regressions detected
- [ ] QA sign-off report created

---

## Test Commands

```bash
make lint
make test

# Lighthouse audit
npx lighthouse <staging-url> --output html --output-path ./lighthouse-report.html

# Or use Chrome DevTools Lighthouse panel
```

---

## Files Expected to Change

```
docs/dev/reports/theme-a-qa-signoff.md    # New: QA sign-off report
```

---

## Dependencies

**Depends On:**
- [ ] WO-THEME-001: Audit and document all critical CSS issues
- [ ] WO-THEME-002: Fix layout and spacing bugs
- [ ] WO-THEME-003: Fix responsive breakpoint issues

**Blocks:**
- Nothing — this is the final task

---

## Risk

**Level:** Low

**Why:**
- QA task only, no code changes
- May identify issues requiring follow-up

**Mitigation:**
- Document any issues found for future work
- Create issues for anything not addressed

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
docs(themes): add Theme A visual QA sign-off report

- Document Lighthouse audit results
- Include cross-browser testing verification
- Confirm all critical fixes verified
- Add QA sign-off for Theme A fixes

Closes #TBD
```
