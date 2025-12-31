# Task

**Title:** `WO-THEME-002: Fix layout and spacing bugs`

---

## Parent

**Work Order:** WO: Theme A Critical Fixes (v0.6.1)
**Tracking Issue:** #292

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/theme-a-critical-issues/002-layout-fixes` | `fix/theme-a-critical-issues` |

```bash
git checkout fix/theme-a-critical-issues
git pull origin fix/theme-a-critical-issues
git checkout -b fix/theme-a-critical-issues/002-layout-fixes
git push -u origin fix/theme-a-critical-issues/002-layout-fixes
```

---

## Deliverable

This task will deliver:

- Fixed layout bugs identified in audit
- Corrected spacing issues (margins, padding, gaps)
- Proper grid/flexbox alignment
- Consistent component sizing

---

## Boundaries

### Do

- Fix layout bugs documented in audit report
- Correct spacing issues (margins, padding)
- Fix grid and flexbox alignment problems
- Ensure consistent component sizing
- Test fixes across major browsers
- Maintain existing visual design intent

### Do NOT

- ❌ Do not change responsive breakpoints (separate task)
- ❌ Do not add new CSS features or utilities
- ❌ Do not refactor CSS architecture
- ❌ Do not modify JavaScript functionality
- ❌ Do not change typography (unless layout-related)

---

## Acceptance Criteria

- [ ] All critical layout bugs from audit fixed
- [ ] All high-priority spacing issues fixed
- [ ] Visual appearance matches design intent
- [ ] No CSS regressions introduced
- [ ] `make lint && make test` passes
- [ ] Cross-browser testing completed

---

## Test Commands

```bash
make lint
make test

# Visual testing
# Open staging site and verify layouts
```

---

## Files Expected to Change

```
themes/theme_a/static/css/main.css              # Modified
themes/theme_a/static/css/components/*.css      # Modified
themes/theme_a/templates/theme_a/blocks/*.html  # Modified if needed
```

---

## Dependencies

**Depends On:**
- [ ] WO-THEME-001: Audit and document all critical CSS issues

**Blocks:**
- WO-THEME-004: Visual regression testing and QA

---

## Risk

**Level:** Medium

**Why:**
- CSS changes can have cascading effects
- Layout fixes may affect responsive behavior

**Mitigation:**
- Test thoroughly across breakpoints
- Visual comparison before/after
- Review in multiple browsers

---

## Labels

- [ ] `type:task`
- [ ] `component:themes`
- [ ] `risk:medium`
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
fix(themes): resolve layout and spacing bugs in Theme A

- Fix grid alignment issues in hero section
- Correct spacing in card components
- Fix flexbox layout in footer
- Resolve margin/padding inconsistencies

Closes #TBD
```
