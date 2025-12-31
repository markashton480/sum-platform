# Version Declaration: v0.7.0

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value                                                      |
| ------------------ | ---------------------------------------------------------- |
| **Version**        | `v0.7.0`                                                   |
| **Type**           | `MINOR`                                                    |
| **Milestone**      | `v0.7.0`                                                   |
| **Branch**         | `release/0.7.0`                                            |
| **Target**         | `develop` -> `main`                                        |
| **Started**        | 2025-12-30                                                 |
| **Target Release** | 2026-01-31 (End of January)                                |

---

## Statement of Intent

### What This Version IS

v0.7.0 is a **MINOR feature release** that establishes multi-theme capability as production-ready, delivers the first iteration of lead management features, and fixes internal linking across the platform. This release proves the platform architecture supports multiple themes and provides essential operational features for lead-focused websites.

**Core Themes:**
1. **Multi-theme Validation** - Prove Theme B (and optionally Theme C) works, establish theme contracts
2. **Lead Management v1** - Pipeline/status management, notes, assignment, history, filtering
3. **Internal Linking & CTAs** - Fix UniversalLinkBlock usage, add dedicated CTABlock

### What This Version IS NOT

- NOT implementing search functionality (deferred to v0.7.1 or v0.8.x)
- NOT adding scheduled publishing (scope-creep risk)
- NOT refactoring the core architecture
- NOT changing the CLI scaffolding approach
- NOT implementing workflow automation for leads
- NOT adding lead scoring or analytics dashboards
- NOT including multi-site support

---

## Priority Tiers

### P0 - Must Land (Core Scope)

| #   | Work Order                         | Issue   | Branch                       | Status  |
| --- | ---------------------------------- | ------- | ---------------------------- | ------- |
| 1   | Multi-theme Validation             | #364    | `feature/multi-theme`        | Planned |
| 2   | Lead Management v1                 | #365    | `feature/leads-v1`           | Planned |
| 3   | Internal Linking & CTAs            | #366    | `feature/internal-linking`   | Planned |

### P1 - If Time Permits (Optional)

| #   | Work Order                         | Issue   | Branch                       | Status  |
| --- | ---------------------------------- | ------- | ---------------------------- | ------- |
| 4   | New Page Types                     | #367    | `feature/page-types`         | Planned |
| 5   | Link Health Tooling                | #368    | `feature/link-health`        | Planned |

**Status Legend:** Planned | In Progress | Done | Deferred

---

## Work Order Summaries

### WO1: Multi-theme Validation (P0)

**Goal:** Prove the platform architecture genuinely supports multiple themes by implementing Theme B (minimum) and Theme C (if low friction), plus documenting theme contracts.

**Deliverables:**
- Theme B fully implemented and functional
- Theme C (stretch goal if low friction)
- Theme contract documentation
- Theme switching/selection mechanism
- Seeder support for theme selection

**Success Criteria:**
- Theme B passes all existing template contract tests
- Seeder can generate site with Theme B
- Theme contract documented in THEME-GUIDE.md
- No regressions in Theme A

---

### WO2: Lead Management v1 (P0)

**Goal:** Deliver the first production-ready lead management feature set as specified in POST-MVP_BIG-PLAN.

**Deliverables:**
- Lead pipeline/status management with workflow
- Lead notes and activity history
- Lead assignment to users
- Enhanced filtering and search
- Bulk actions for leads

**Success Criteria:**
- Editors can update lead status through intuitive UI
- Editors can add notes to leads with timestamps
- Leads can be assigned to team members
- Saved filters work for common queries
- Bulk status updates functional

---

### WO3: Internal Linking & CTAs (P0)

**Goal:** Fix internal linking across all blocks and add a dedicated CTABlock for consistent call-to-action patterns.

**Deliverables:**
- Audit and fix all UniversalLinkBlock usages
- Fix ServiceCardItemBlock to use UniversalLinkBlock
- Add dedicated CTABlock with primary/secondary buttons
- Link validation in admin
- Template updates for consistent rendering

**Success Criteria:**
- Page chooser appears in all link contexts
- Internal links render correctly in all templates
- CTABlock available in PageStreamBlock
- No regression in existing link functionality

---

### WO4: New Page Types (P1 - Optional)

**Goal:** Add AboutPage and LandingPage types to reduce StandardPage overuse.

**Deliverables:**
- AboutPage with team, mission, timeline blocks
- LandingPage with conversion-focused structure
- ContactPage and FAQPage (if cheap to add)
- Theme templates for new page types

**Success Criteria:**
- New page types available in Wagtail admin
- Theme A and Theme B templates for each
- Seeder can generate pages of each type

---

### WO5: Link Health Tooling (P1 - Optional)

**Goal:** Add management command and report for detecting broken internal links.

**Deliverables:**
- `manage.py check_links` command
- Report output (console + optional JSON)
- Integration with admin dashboard (optional)

**Success Criteria:**
- Command detects broken page references
- Command detects links to unpublished pages
- Output is actionable for editors

---

## Scope Boundaries

### Components In Scope

| Component                        | Changes Expected                                          |
| -------------------------------- | --------------------------------------------------------- |
| `themes/theme_b/`                | New theme implementation                                  |
| `themes/theme_c/`                | Optional new theme implementation                         |
| `core/sum_core/leads/`           | Enhanced models, admin, views                             |
| `core/sum_core/blocks/`          | CTABlock, UniversalLinkBlock fixes                        |
| `core/sum_core/blocks/services.py` | Fix to use UniversalLinkBlock                           |
| `core/sum_core/pages/`           | Optional: AboutPage, LandingPage, ContactPage, FAQPage    |
| `core/sum_core/navigation/`      | Link handling improvements                                |
| `docs/dev/THEME-GUIDE.md`        | Theme contract documentation                              |
| `tests/`                         | Tests for all new functionality                           |

### Components Out of Scope

| Component                        | Reason                                                    |
| -------------------------------- | --------------------------------------------------------- |
| `cli/sum_cli/`                   | No CLI changes in this version                            |
| Search functionality             | Deferred to v0.7.1 or v0.8.x (tends to sprawl)            |
| Workflow automation              | Not in core deliverables                                  |
| Lead scoring/dashboards          | Not in v0.7.0 scope                                       |

---

## Dependencies

### External Dependencies

- v0.6.1 must be released first (stabilization patch, upgrade practice on Sage & Stone)
- Theme B design assets/wireframes (if not using existing patterns)

### Internal Dependencies

| Work Order | Depends On | Reason |
| ---------- | ---------- | ------ |
| WO4 (Page Types) | WO1 (Multi-theme) | New page types need theme templates |
| WO5 (Link Health) | WO3 (Internal Linking) | Link health builds on fixed link system |

---

## Expected Metrics

| Metric                             | Expected                   | Tolerance |
| ---------------------------------- | -------------------------- | --------- |
| Work Orders (P0)                   | 3                          | +0        |
| Work Orders (P1)                   | 2                          | -2        |
| Total PRs merged to release branch | 15-25                      | +/-5      |
| Lines changed                      | 3000-5000                  | +/-1000   |
| Test coverage (overall)            | >=85%                      | -3%       |
| New tests added                    | 50+                        | -10       |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| Theme B takes longer than expected | Medium | High | Start early, have fallback to Theme B-only |
| Lead management scope creep | High | Medium | Strict acceptance criteria, defer scoring/dashboards |
| Internal linking fixes cause regressions | Medium | Medium | Comprehensive test coverage before changes |
| P1 items don't make the cut | Medium | Low | P1 is explicitly optional |

---

## Changelog Draft

```markdown
## [v0.7.0] - 2026-01-31

### Added
- **Multi-theme Support**: Theme B fully implemented and functional
- **Theme Contracts**: Documented theme requirements and contracts in THEME-GUIDE.md
- **Lead Management v1**: Pipeline/status management with workflow
- **Lead Notes**: Activity history and timestamped notes on leads
- **Lead Assignment**: Assign leads to team members
- **Lead Filtering**: Enhanced filtering and saved queries
- **Lead Bulk Actions**: Bulk status updates for multiple leads
- **CTABlock**: Dedicated call-to-action block with primary/secondary buttons
- **Link Health Command**: `manage.py check_links` for broken link detection (if P1 lands)
- **AboutPage**: Purpose-built page type for company information (if P1 lands)
- **LandingPage**: Conversion-focused page type (if P1 lands)

### Fixed
- **Internal Linking**: ServiceCardItemBlock now uses UniversalLinkBlock (page chooser works)
- **Internal Linking**: All blocks now consistently support internal page links
- **Link Rendering**: Internal links render correctly in all theme templates

### Changed
- **Lead Admin**: Redesigned lead management interface for operational use
- **Theme System**: Established formal theme contracts and validation
```

---

## Definition of Done

### Version-Level DoD

- [ ] All P0 Work Orders in this Version Declaration are closed
- [ ] `release/0.7.0` merged to `develop` and `main` per release process
- [ ] `make release-check` passes on `release/0.7.0`
- [ ] Test coverage >= 85%
- [ ] Changelog entry finalized for v0.7.0
- [ ] Theme B functional and passing all tests
- [ ] Lead management v1 features operational
- [ ] Internal linking works in all block contexts
- [ ] Theme contract documented

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
- Scope: 3 P0 Work Orders, 2 P1 Work Orders
- Target: End of January 2026
- Dependencies: v0.6.1 release first
```
