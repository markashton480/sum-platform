# Task

**Title:** `WO-THEME-003: Fix responsive breakpoint issues`

---

## Parent

**Work Order:** #461 (WO: Theme A Critical Fixes)
**Tracking Issue:** #465

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/theme-a-critical-issues/003-responsive-fixes` | `fix/theme-a-critical-issues` |

```bash
git checkout fix/theme-a-critical-issues
git pull origin fix/theme-a-critical-issues
git checkout -b fix/theme-a-critical-issues/003-responsive-fixes
git push -u origin fix/theme-a-critical-issues/003-responsive-fixes
```

---

## Deliverable

This task will deliver:

- Fixed responsive breakpoint issues
- Correct mobile and tablet layouts
- Proper media query behavior
- Consistent responsive behavior across devices

---

## Boundaries

### Do

- Fix responsive issues documented in audit
- Correct mobile layout problems
- Fix tablet breakpoint issues
- Ensure smooth transitions between breakpoints
- Test on multiple device sizes
- Verify touch targets are appropriate size on mobile

### Do NOT

- ❌ Do not add new breakpoints
- ❌ Do not change desktop-first to mobile-first (or vice versa)
- ❌ Do not refactor media query structure
- ❌ Do not change core layout patterns
- ❌ Do not modify non-responsive CSS

---

## Acceptance Criteria

- [ ] All critical responsive issues from audit fixed
- [ ] Mobile layout renders correctly (320px - 767px)
- [ ] Tablet layout renders correctly (768px - 1023px)
- [ ] Desktop layout renders correctly (1024px+)
- [ ] No content overflow or horizontal scroll issues
- [ ] Touch targets ≥44px on mobile
- [ ] `make lint && make test` passes

---

## Test Commands

```bash
make lint
make test

# Responsive testing
# Use browser dev tools to test at:
# - 320px (small mobile)
# - 375px (standard mobile)
# - 768px (tablet)
# - 1024px (small desktop)
# - 1440px (large desktop)
```

---

## Files Expected to Change

```
themes/theme_a/static/css/main.css              # Modified: media queries
themes/theme_a/static/css/components/*.css      # Modified: responsive styles
```

---

## Dependencies

**Depends On:**
- [ ] WO-THEME-001: Audit and document all critical CSS issues
- [ ] WO-THEME-002: Fix layout and spacing bugs (recommended)

**Blocks:**
- WO-THEME-004: Visual regression testing and QA

---

## Risk

**Level:** Medium

**Why:**
- Responsive changes affect all device sizes
- Media query changes can have unexpected cascading effects

**Mitigation:**
- Test at multiple breakpoints
- Use browser dev tools device emulation
- Test on real mobile devices if possible

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
fix(themes): resolve responsive breakpoint issues in Theme A

- Fix mobile layout rendering issues
- Correct tablet breakpoint behavior
- Resolve content overflow on small screens
- Ensure proper touch target sizes

Closes #TBD
```
