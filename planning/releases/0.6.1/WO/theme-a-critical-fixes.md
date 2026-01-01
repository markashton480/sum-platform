# Work Order

**Title:** `WO: Theme A Critical Fixes (v0.6.1)`

---

## Parent

**Version Declaration:** #460 (VD-0.6.1)
**Tracking Issue:** #461
**Related Issue:** #292 (original Theme A task)
**Audit Report:** `docs/dev/reports/theme-a-audit.md`

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/theme-a-critical-issues` | `release/0.6.1` |

```bash
git checkout release/0.6.1
git checkout -b fix/theme-a-critical-issues
git push -u origin fix/theme-a-critical-issues
```

---

## Objective

- [x] Audit and document all critical CSS bugs affecting Theme A layouts
- [ ] Fix all critical accessibility and functionality bugs (P0)
- [ ] Resolve high-priority visual issues identified in audit (P1)
- [ ] Ensure responsive design works correctly across all breakpoints
- [ ] Maintain Lighthouse scores ≥90 on all metrics

---

## Audit Summary

**Date:** 2026-01-01
**Total Issues Found:** 28

| Priority | Count | Description |
|----------|-------|-------------|
| P0 Critical | 3 | Accessibility violations, broken functionality |
| P1 High | 10 | Block violations, missing blocks, major UX |
| P2 Medium | 9 | Visual discrepancies |
| P3 Low | 6 | Minor polish |

**In-Scope Issues:** 12 (P0 + select P1/P2 fixes)

---

## Scope

### In Scope

- CSS bug fixes for layout issues
- Template corrections for rendering problems
- Responsive design fixes across breakpoints
- Visual regression testing
- Theme contract compliance verification

### Out of Scope

- New theme features or enhancements (ProvenancePlateBlock deferred)
- Theme architecture changes (HSL migration deferred)
- Adding new blocks or components
- JavaScript functionality changes (unless critical bug)

---

## Subtasks

| # | Task | Issue | Branch | Status |
|---|------|-------|--------|--------|
| 1 | WO-THEME-001: Audit and document all critical CSS issues | #463 | `task/theme-a-critical-issues/001-audit-issues` | ✅ |
| 2 | WO-THEME-005: Fix P0 critical accessibility and functionality bugs | #500 | `fix/theme-a-critical-issues/005-p0-fixes` | 🔲 |
| 3 | WO-THEME-006: Add print styles and CSS polish | #501 | `fix/theme-a-critical-issues/006-css-polish` | 🔲 |
| 4 | WO-THEME-007: Enhance mega menu layout | #502 | `fix/theme-a-critical-issues/007-mega-menu` | 🔲 |
| 5 | WO-THEME-008: Add responsive image handling | #503 | `fix/theme-a-critical-issues/008-responsive-images` | 🔲 |
| 6 | WO-THEME-004: Visual regression testing and QA | #466 | `fix/theme-a-critical-issues/009-visual-qa` | 🔲 |

### Superseded Issues

These generic issues are superseded by the specific tasks above:
- #464 (WO-THEME-002: Fix layout and spacing bugs) → superseded by #500
- #465 (WO-THEME-003: Fix responsive breakpoint issues) → superseded by #503

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Affected Paths

```
themes/theme_a/
├── static/
│   └── css/
│       ├── main.css
│       └── components/
└── templates/
    └── theme_a/
        ├── base.html
        └── blocks/
```

---

## Verification

### After Each Task Merge

```bash
git checkout fix/theme-a-critical-issues
git pull origin fix/theme-a-critical-issues
make lint && make test
```

### Before Feature PR

```bash
# Visual QA on staging
# Lighthouse audit on key pages
# Cross-browser testing (Chrome, Firefox, Safari)
# Mobile responsive testing
```

---

## Risk

**Level:** Low-Medium

**Factors:**
- CSS changes can have cascading effects
- Visual regressions may not be caught by automated tests

**Mitigation:**
- Visual regression testing before merge
- Staging environment validation
- Cross-browser testing checklist

---

## Labels

- [ ] `type:work-order`
- [ ] `component:themes`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] Visual QA passed on staging environment
- [ ] No CSS regressions introduced
- [ ] Lighthouse scores ≥90 on all metrics
- [ ] Cross-browser testing completed
- [ ] Feature branch merged to release branch
- [ ] Version Declaration updated

---

## Deferred Items

These audit findings are out of scope for this WO and should be tracked separately:

| Item | Reason | Suggested Follow-up |
|------|--------|---------------------|
| ProvenancePlateBlock | New block/component | Create WO for v0.7.0 |
| HSL color migration | Architecture change | Create enhancement issue |
| Block usage violations | Content decisions | Document in content guidelines |
| ComparisonBlock template | New template creation | Create enhancement issue |
| FeaturesListBlock template | New template creation | Create enhancement issue |
