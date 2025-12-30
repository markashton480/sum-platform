# Implementation Plan: v0.8.0

> **This document provides the complete implementation plan for v0.8.0.**
> It serves as the master reference for scope, dependencies, and execution strategy.

---

## Executive Summary

**Version:** 0.8.0
**Type:** MINOR (focused feature release)
**Target Date:** Mid-February 2026
**Theme:** Blog Search + Visual QA + Lead Analytics + Admin Control + Elysian Validation

v0.8.0 delivers targeted enhancements that improve content discoverability (blog search), quality assurance (visual regression), operational insights (lead analytics), and administrative flexibility (control plane), all validated against the new Elysian consumer site.

---

## Problem Statement

The SUM Platform has established multi-theme capability and lead management in v0.7.0. However, several gaps remain:

1. **Blog discoverability is limited** - Users cannot search blog content; they must browse or use external search engines.

2. **Visual quality is manually verified** - No automated way to detect unintended visual changes across themes and pages.

3. **Lead insights are basic** - Leads can be managed but not scored or analyzed for conversion optimization.

4. **Feature control is all-or-nothing** - No admin ability to enable/disable platform features per site.

5. **Consumer site validation needed** - Elysian replaces LINTEL as the proving ground for new features.

---

## Goals

### Primary Goals (P0)

1. **Enable blog search** with wireframe-parity UI using Wagtail's built-in search
2. **Establish visual regression testing** for automated quality assurance
3. **Deliver lead analytics** with scoring and dashboard
4. **Add admin control plane** for feature toggles and typography settings
5. **Validate on Elysian** as the new consumer site

### Non-Goals

- Site-wide or global page search
- External search backends (Algolia, Elasticsearch)
- Search analytics, query logging, or relevance tuning
- Workflow automation for leads
- AI audit layer
- LINTEL launch

---

## Success Criteria

| Criterion | Measurement |
| --------- | ----------- |
| Blog search works | Users can search blog posts, see results with pagination |
| Visual regression catches changes | CI fails on significant visual diffs |
| Lead scores calculated | All leads have computed scores |
| Analytics dashboard functional | Key metrics displayed, filterable |
| Feature toggles work | Disabling blog hides it from site |
| Elysian validated | All features work, upgrade path tested |

---

## Work Breakdown

### P0 Work Orders (Must Land)

| WO | Title | Tasks | Est. Hours | Dependencies |
| -- | ----- | ----- | ---------- | ------------ |
| 1 | Blog Search v1 | 7 | 14-22 | None |
| 2 | Visual Regression Testing v1 | 6 | 12-20 | None |
| 3 | Lead Scoring/Analytics Dashboard | 8 | 16-26 | Lead Mgmt v1 (v0.7.0) |
| 4 | Admin Control Plane v1 | 7 | 12-20 | None |
| 5 | Elysian Consumer Site Validation | 6 | 10-16 | WO1-WO4 |

**Total:** 34 tasks, 64-104 hours

---

## Task Inventory

### WO1: Blog Search v1 (7 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO1-001 | Configure Wagtail Search for BlogPostPage | 2-3h | Low | `feature/blog-search/001-wagtail-search-config` |
| WO1-002 | Create Search Input Component | 2-3h | Low | `feature/blog-search/002-search-input` |
| WO1-003 | Create Blog Search Results Page | 3-4h | Med | `feature/blog-search/003-results-page` |
| WO1-004 | Implement No-Results State | 1-2h | Low | `feature/blog-search/004-no-results` |
| WO1-005 | Add Results Pagination | 2-3h | Low | `feature/blog-search/005-pagination` |
| WO1-006 | Theme Templates for Search | 2-4h | Med | `feature/blog-search/006-theme-templates` |
| WO1-007 | Blog Search Tests | 2-3h | Low | `feature/blog-search/007-tests` |

### WO2: Visual Regression Testing v1 (6 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO2-001 | Select and Configure Tooling | 2-3h | Med | `feature/visual-regression/001-tooling-setup` |
| WO2-002 | Create Screenshot Capture Scripts | 3-4h | Med | `feature/visual-regression/002-screenshot-capture` |
| WO2-003 | Implement Baseline Management | 2-3h | Low | `feature/visual-regression/003-baseline-management` |
| WO2-004 | Create Diff Generation and Reporting | 2-4h | Med | `feature/visual-regression/004-diff-reporting` |
| WO2-005 | CI Integration | 2-3h | Med | `feature/visual-regression/005-ci-integration` |
| WO2-006 | Documentation and Workflow Guide | 1-3h | Low | `feature/visual-regression/006-documentation` |

### WO3: Lead Scoring/Analytics Dashboard (8 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO3-001 | Design Lead Scoring Algorithm | 2-3h | Med | `feature/lead-analytics/001-scoring-algorithm` |
| WO3-002 | Add Score Field to Lead Model | 1-2h | Low | `feature/lead-analytics/002-score-field` |
| WO3-003 | Implement Score Calculation | 2-3h | Med | `feature/lead-analytics/003-score-calculation` |
| WO3-004 | Display Score in Lead Admin | 2-3h | Low | `feature/lead-analytics/004-admin-score-display` |
| WO3-005 | Create Analytics Dashboard View | 3-4h | Med | `feature/lead-analytics/005-dashboard-view` |
| WO3-006 | Dashboard Metrics and Charts | 3-5h | Med | `feature/lead-analytics/006-metrics-charts` |
| WO3-007 | Score-based Filtering | 1-2h | Low | `feature/lead-analytics/007-score-filtering` |
| WO3-008 | Analytics Tests | 2-4h | Low | `feature/lead-analytics/008-tests` |

### WO4: Admin Control Plane v1 (7 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO4-001 | Add Feature Toggle Fields to SiteSettings | 2-3h | Low | `feature/admin-control-plane/001-toggle-fields` |
| WO4-002 | Implement Blog Feature Toggle | 2-3h | Med | `feature/admin-control-plane/002-blog-toggle` |
| WO4-003 | Implement Leads Feature Toggle | 2-3h | Med | `feature/admin-control-plane/003-leads-toggle` |
| WO4-004 | Implement Jobs Feature Toggle (Placeholder) | 1-2h | Low | `feature/admin-control-plane/004-jobs-toggle` |
| WO4-005 | Add Typography Controls | 2-3h | Med | `feature/admin-control-plane/005-typography-controls` |
| WO4-006 | Add Spacing Controls | 2-3h | Med | `feature/admin-control-plane/006-spacing-controls` |
| WO4-007 | Control Plane Tests | 2-3h | Low | `feature/admin-control-plane/007-tests` |

### WO5: Elysian Consumer Site Validation (6 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO5-001 | Scaffold Elysian Site | 2-3h | Low | `feature/elysian-validation/001-scaffold` |
| WO5-002 | Configure Elysian with v0.8.0 Features | 2-3h | Med | `feature/elysian-validation/002-configure` |
| WO5-003 | Test Blog Search on Elysian | 1-2h | Low | `feature/elysian-validation/003-test-search` |
| WO5-004 | Test Lead Analytics on Elysian | 1-2h | Low | `feature/elysian-validation/004-test-analytics` |
| WO5-005 | Capture Visual Regression Baselines | 2-3h | Med | `feature/elysian-validation/005-capture-baselines` |
| WO5-006 | Test Upgrade Path v0.7.x to v0.8.0 | 2-3h | Med | `feature/elysian-validation/006-upgrade-test` |

---

## Dependency Graph

```
                    +---------------------------------------------+
                    |            v0.7.0 RELEASE                   |
                    |     (prerequisite - must ship first)        |
                    +---------------------------------------------+
                                        |
          +-----------------------------+-----------------------------+
          |              |              |              |              |
          v              v              v              v              |
    +-----------+  +-----------+  +-----------+  +-----------+       |
    |    WO1    |  |    WO2    |  |    WO3    |  |    WO4    |       |
    |   Blog    |  |  Visual   |  |   Lead    |  |   Admin   |       |
    |  Search   |  | Regression|  | Analytics |  |  Control  |       |
    |   (P0)    |  |   (P0)    |  |   (P0)    |  |   (P0)    |       |
    +-----------+  +-----------+  +-----------+  +-----------+       |
          |              |              |              |              |
          +--------------+--------------+--------------+              |
                                   |                                  |
                                   v                                  |
                            +-----------+                             |
                            |    WO5    |                             |
                            |  Elysian  |<----------------------------+
                            |Validation |
                            |   (P0)    |
                            +-----------+
```

### Inter-WO Dependencies

| Dependency | Reason |
| ---------- | ------ |
| WO5 depends on WO1-WO4 | Validation requires all features complete |
| WO3 depends on Lead Mgmt v1 | Builds on v0.7.0 lead system |

### Parallelization Opportunities

WO1, WO2, WO3, and WO4 can all proceed in parallel. They have no inter-dependencies until WO5 integration.

---

## Execution Strategy

### Phase 1: Foundation (Week 1)

**Goal:** Start all P0 work orders in parallel

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-001 (Search Config) | 2-3h | Yes |
| WO2-001 (Tooling Setup) | 2-3h | Yes |
| WO3-001 (Scoring Design) | 2-3h | Yes |
| WO4-001 (Toggle Fields) | 2-3h | Yes |

### Phase 2: Core Implementation (Week 1-2)

**Goal:** Complete core functionality for all work orders

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-002 through WO1-005 (Search UI) | 8-12h | Sequential |
| WO2-002 through WO2-004 (Screenshots + Diffs) | 7-11h | Sequential |
| WO3-002 through WO3-006 (Scoring + Dashboard) | 11-17h | Mostly sequential |
| WO4-002 through WO4-006 (Toggles + Controls) | 9-14h | Parallel possible |

### Phase 3: Integration (Week 2-3)

**Goal:** Complete tests, documentation, and begin Elysian validation

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-006, WO1-007 (Templates + Tests) | 4-7h | Sequential |
| WO2-005, WO2-006 (CI + Docs) | 3-6h | Sequential |
| WO3-007, WO3-008 (Filtering + Tests) | 3-6h | Parallel |
| WO4-007 (Tests) | 2-3h | Yes |
| WO5-001, WO5-002 (Elysian Setup) | 4-6h | After WO1-4 core |

### Phase 4: Validation & Release (Week 3)

**Goal:** Complete Elysian validation and release

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO5-003 through WO5-006 (Validation Tests) | 6-10h | Sequential |
| Integration testing | 4-6h | After WO5 |
| Release preparation | 2-4h | Final |

---

## Risk Mitigation

| Risk | Mitigation |
| ---- | ---------- |
| Blog search scope creep | Explicit non-goals in WO1; PR review enforces boundaries |
| Visual regression tooling complexity | Start with Playwright; keep configuration simple |
| Lead scoring debates | Document simple initial algorithm; iterate post-release |
| Elysian delays | Can use test_project for basic validation if needed |
| Parallel work conflicts | Clear branch structure; regular integration to release branch |

---

## Testing Strategy

### Unit Tests

- Blog search query building and filtering
- Lead score calculation logic
- Feature toggle state checks
- Typography/spacing CSS generation

### Integration Tests

- Search results render correctly across themes
- Visual regression captures match expectations
- Dashboard aggregations are accurate
- Toggles actually hide/show features

### Visual Regression Tests

- All page types captured
- All themes covered
- Key component states (hover, active, disabled)
- Responsive breakpoints

### Manual Testing

- Search UX review on all themes
- Dashboard data accuracy spot-check
- Feature toggle behavior in admin
- Elysian end-to-end walkthrough

---

## Documentation Updates

| Document | Updates Needed |
| -------- | -------------- |
| `docs/dev/HANDBOOK.md` | Blog search usage, visual regression workflow |
| `docs/dev/ADMIN-GUIDE.md` | Feature toggles, typography controls |
| `docs/dev/TESTING.md` | Visual regression testing guide |
| `docs/dev/LEAD-GUIDE.md` | Lead scoring explanation, dashboard usage |

---

## Rollout Plan

1. **v0.7.0 Release** (prerequisite)
   - Complete before v0.8.0 execution starts

2. **v0.8.0-alpha** (internal)
   - WO1-WO4 features complete
   - Internal testing on test_project

3. **v0.8.0-beta**
   - Elysian validation complete
   - Visual baselines approved

4. **v0.8.0 Release**
   - Full release to develop -> main
   - Tag and publish
   - Consumer upgrade documentation

---

## Artifacts

This implementation plan is supported by:

- `/planning/releases/0.8.0/VD.md` - Version Declaration
- `/planning/releases/0.8.0/WO/blog-search-v1.md` - WO1 details
- `/planning/releases/0.8.0/WO/visual-regression-testing-v1.md` - WO2 details
- `/planning/releases/0.8.0/WO/lead-scoring-analytics.md` - WO3 details
- `/planning/releases/0.8.0/WO/admin-control-plane-v1.md` - WO4 details
- `/planning/releases/0.8.0/WO/elysian-validation.md` - WO5 details

---

## Approval

| Role | Name | Date | Approved |
| ---- | ---- | ---- | -------- |
| Author | Claude-on-WSL | 2025-12-30 | - |
| Product Owner | | | Pending |
| Tech Lead | | | Pending |

---

## Revision History

| Date | Author | Changes |
| ---- | ------ | ------- |
| 2025-12-30 | Claude-on-WSL | Initial plan created |
