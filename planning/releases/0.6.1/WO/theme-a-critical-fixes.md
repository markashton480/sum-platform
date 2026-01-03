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

- [ ] Fix all critical CSS bugs affecting Theme A layouts
- [ ] Resolve high-priority visual issues identified in #292
- [ ] Ensure responsive design works correctly across all breakpoints
- [ ] Validate theme against theme contract requirements
- [ ] Maintain Lighthouse scores ≥90 on all metrics

---

## Scope

### In Scope

- CSS bug fixes for layout issues
- Template corrections for rendering problems
- Responsive design fixes across breakpoints
- Visual regression testing
- Theme contract compliance verification

### Out of Scope

- New theme features or enhancements
- Theme architecture changes
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

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Audit Summary

- See `docs/dev/reports/theme-a-audit.md`

---

## Superseded Issues

- #464 (superseded by #500)
- #465 (superseded by #503)

---

## Deferred Items

- None

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
