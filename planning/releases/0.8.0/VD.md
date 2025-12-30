# Version Declaration: v0.8.0

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value                                                      |
| ------------------ | ---------------------------------------------------------- |
| **Version**        | `v0.8.0`                                                   |
| **Type**           | `MINOR`                                                    |
| **Milestone**      | `v0.8.0`                                                   |
| **Branch**         | `release/0.8.0`                                            |
| **Target**         | `develop` -> `main`                                        |
| **Started**        | 2025-12-30                                                 |
| **Target Release** | Mid-February 2026                                          |

---

## Statement of Intent

### What This Version IS

v0.8.0 is a **focused feature release** that adds blog search capability, establishes visual regression testing infrastructure, delivers lead analytics, and introduces admin-level feature controls. This release is validated against **Elysian** as the consumer site, replacing the previous LINTEL focus.

**Core Themes:**
1. **Blog Search v1** - Wireframe-parity blog search (NOT site-wide search)
2. **Visual Regression Testing** - Automated screenshot diffs for quality assurance
3. **Lead Analytics** - Scoring and dashboard for lead management insights
4. **Admin Control Plane** - Feature toggles and granular site settings
5. **Elysian Validation** - Real consumer site proving all v0.8.0 features

### What This Version IS NOT

- NOT implementing site-wide or global page search (blog only)
- NOT adding external search backends (Algolia, Elasticsearch)
- NOT implementing search analytics, query logging, or relevance tuning
- NOT adding workflow automation for leads
- NOT launching LINTEL (removed from roadmap)
- NOT adding multi-language support
- NOT implementing AI audit layer (deferred)

---

## Consumer Site Change

**IMPORTANT:** This version marks a strategic pivot:

- **OUT:** LINTEL as showcase site
- **IN:** Elysian as the v0.8.0 "run-against" consumer site

Elysian will be used to:
- Validate all new v0.8.0 core features
- Test real deploy/upgrade loop (v0.7.x -> v0.8.0)
- Prove multi-theme architecture continues to work
- Generate visual regression baselines

---

## Priority Tiers

### P0 - Must Land (Core Scope)

| #   | Work Order                         | Issue   | Branch                           | Status  |
| --- | ---------------------------------- | ------- | -------------------------------- | ------- |
| 1   | Blog Search v1                     | #TBD    | `feature/blog-search`            | Planned |
| 2   | Visual Regression Testing v1       | #TBD    | `feature/visual-regression`      | Planned |
| 3   | Lead Scoring/Analytics Dashboard   | #TBD    | `feature/lead-analytics`         | Planned |
| 4   | Admin Control Plane v1             | #TBD    | `feature/admin-control-plane`    | Planned |
| 5   | Elysian Consumer Site Validation   | #TBD    | `feature/elysian-validation`     | Planned |

### P1 - If Time Permits (Optional)

_No P1 items defined for this focused release._

**Status Legend:** Planned | In Progress | Done | Deferred

---

## Work Order Summaries

### WO1: Blog Search v1 (P0)

**Goal:** Deliver wireframe-parity blog search functionality using Wagtail's built-in search backend.

**Deliverables:**
- Search input component matching wireframe placement
- Blog search results page with pagination
- No-results state handling
- Wagtail DB-backed search integration

**Explicit Non-Goals:**
- Global/site-wide page search
- Relevance tuning or synonyms
- External search backends (Algolia, Elasticsearch)
- Query logging or search analytics dashboards

**Success Criteria:**
- Search input appears where wireframe specifies
- Blog posts are searchable by title and content
- Results page renders with proper pagination
- No-results state displays appropriate message
- Search works across all themes

---

### WO2: Visual Regression Testing v1 (P0)

**Goal:** Establish automated visual regression testing infrastructure for wireframe parity validation.

**Deliverables:**
- Screenshot capture tooling for key pages/components
- Baseline image management
- Diff generation and threshold configuration
- CI integration for automated checks
- Reporting for visual differences

**Success Criteria:**
- Can capture screenshots of all page types
- Can compare against approved baselines
- Diffs highlight visual changes clearly
- CI fails on significant visual regressions
- Baseline approval workflow documented

---

### WO3: Lead Scoring/Analytics Dashboard (P0)

**Goal:** Deliver lead scoring functionality and an analytics dashboard for lead management insights.

**Deliverables:**
- Lead scoring model/algorithm
- Score display in lead admin
- Analytics dashboard with key metrics
- Score-based filtering and sorting
- Historical scoring data

**Success Criteria:**
- Leads receive calculated scores
- Dashboard displays conversion metrics
- Editors can filter/sort by score
- Historical trends visible
- Integration with existing Lead Management v1

---

### WO4: Admin Control Plane v1 (P0)

**Goal:** Add feature toggles and granular site settings for admin control over platform capabilities.

**Deliverables:**
- Feature enable/disable booleans in SiteSettings
- Blog feature toggle
- Leads feature toggle
- Jobs feature toggle (for future use)
- Typography/spacing granular controls
- Feature state respected throughout templates

**Success Criteria:**
- Admins can enable/disable blog via settings
- Admins can enable/disable leads capture
- Disabled features hide from navigation/templates
- Typography controls adjust rendered output
- Settings persist and apply site-wide

---

### WO5: Elysian Consumer Site Validation (P0)

**Goal:** Deploy and validate Elysian as the consumer site proving all v0.8.0 features work in production context.

**Deliverables:**
- Elysian site scaffolded via `sum init`
- All v0.8.0 features exercised on Elysian
- Upgrade path tested (v0.7.x -> v0.8.0)
- Visual regression baselines captured
- Documentation of validation results

**Success Criteria:**
- Elysian deploys successfully with v0.8.0
- Blog search works on Elysian
- Lead analytics visible on Elysian
- Feature toggles function correctly
- Upgrade from v0.7.x completes without issues
- Visual regression baselines approved

---

## Scope Boundaries

### Components In Scope

| Component                          | Changes Expected                                          |
| ---------------------------------- | --------------------------------------------------------- |
| `core/sum_core/search/`            | New module for blog search                                |
| `core/sum_core/leads/`             | Scoring model, analytics views                            |
| `core/sum_core/settings/`          | Feature toggles, typography controls                      |
| `themes/*/templates/`              | Search templates, dashboard templates                     |
| `tests/visual/`                    | New visual regression test infrastructure                 |
| `clients/elysian/`                 | Consumer site for validation                              |
| `docs/`                            | Feature documentation updates                             |

### Components Out of Scope

| Component                          | Reason                                                    |
| ---------------------------------- | --------------------------------------------------------- |
| `cli/sum_cli/`                     | No CLI changes in this version                            |
| Site-wide search                   | Explicit non-goal; blog search only                       |
| External search backends           | Wagtail built-in only for v1                              |
| Search analytics/query logging     | Deferred to future version                                |
| AI audit layer                     | Deferred from original M8 plan                            |
| LINTEL site                        | Removed from roadmap                                      |

---

## Dependencies

### External Dependencies

- v0.7.0 must be released first
- Elysian design/content requirements defined
- Visual regression tooling selection (Playwright, Percy, or similar)

### Internal Dependencies

| Work Order | Depends On | Reason |
| ---------- | ---------- | ------ |
| WO5 (Elysian) | WO1-WO4 | Validation requires all features complete |
| WO3 (Analytics) | Lead Management v1 (v0.7.0) | Builds on existing lead system |

---

## Expected Metrics

| Metric                             | Expected                   | Tolerance |
| ---------------------------------- | -------------------------- | --------- |
| Work Orders (P0)                   | 5                          | +0        |
| Work Orders (P1)                   | 0                          | +0        |
| Total PRs merged to release branch | 20-30                      | +/-5      |
| Lines changed                      | 2500-4000                  | +/-500    |
| Test coverage (overall)            | >=85%                      | -3%       |
| New tests added                    | 40+                        | -10       |
| Visual regression baselines        | 20+                        | -5        |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Blog search scope creep to site-wide | High | High | Explicit non-goals, strict PR review |
| Visual regression tooling complexity | Medium | Medium | Start with simple Playwright screenshots |
| Lead scoring algorithm debates | Medium | Low | Start simple, iterate based on feedback |
| Elysian content/design delays | Medium | High | Parallel track; use placeholder content |
| v0.7.0 delays affecting start | Low | Medium | Planning can proceed; execution blocks |

---

## Changelog Draft

```markdown
## [v0.8.0] - 2026-02-15

### Added
- **Blog Search v1**: Search functionality for blog posts with results page and pagination
- **Visual Regression Testing**: Automated screenshot comparison for quality assurance
- **Lead Scoring**: Automatic lead scoring based on engagement and data completeness
- **Lead Analytics Dashboard**: Metrics and insights for lead management
- **Admin Control Plane**: Feature toggles for blog, leads, and jobs
- **Typography Controls**: Granular font weight and spacing settings in SiteSettings
- **Elysian Site**: New consumer site validating v0.8.0 features

### Changed
- **SiteSettings**: Extended with feature toggles and typography controls
- **Lead Admin**: Enhanced with scoring display and analytics integration

### Removed
- **LINTEL**: Removed from consumer site roadmap (replaced by Elysian)
```

---

## Definition of Done

### Version-Level DoD

- [ ] All P0 Work Orders in this Version Declaration are closed
- [ ] `release/0.8.0` merged to `develop` and `main` per release process
- [ ] `make release-check` passes on `release/0.8.0`
- [ ] Test coverage >= 85%
- [ ] Changelog entry finalized for v0.8.0
- [ ] Blog search functional on all themes
- [ ] Visual regression baselines approved for Elysian
- [ ] Lead analytics dashboard operational
- [ ] Feature toggles working in admin
- [ ] Elysian upgrade from v0.7.x validated

### Work Order DoD (each WO)

- [ ] All tasks in Work Order are closed
- [ ] Feature branch merged to release branch
- [ ] No unresolved conflicts
- [ ] All acceptance criteria met

### Task DoD (each task)

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] Model Used field set on issue
- [ ] `model:*` label applied

---

## Sign-Off

| Role                     | Name | Date | Approved |
| ------------------------ | ---- | ---- | -------- |
| Author                   | Claude-on-WSL | 2025-12-30 | Pending |
| Product Owner            |      |      | Pending  |
| Tech Lead                |      |      | Pending  |

---

## Audit Log

_Append audit results here:_

```
[2025-12-30] Initial VD created by Claude-on-WSL
- Scope: 5 P0 Work Orders, 0 P1 Work Orders
- Target: Mid-February 2026
- Consumer site: Elysian (replacing LINTEL)
- Key change: Blog search only (NOT site-wide)
```
