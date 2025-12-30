# Implementation Plan: v0.7.0

> **This document provides the complete implementation plan for v0.7.0.**
> It serves as the master reference for scope, dependencies, and execution strategy.

---

## Executive Summary

**Version:** 0.7.0
**Type:** MINOR (feature release)
**Target Date:** End of January 2026
**Theme:** Multi-theme Validation + Lead Operations + Platform Correctness

v0.7.0 establishes the SUM Platform as production-ready for multi-theme deployments while delivering essential lead management features and fixing internal linking across the platform.

---

## Problem Statement

The SUM Platform has proven itself with Theme A and a successful Sage & Stone deployment. However, three critical gaps remain:

1. **Multi-theme is theoretical** - Theme A is the only theme. The platform promises multi-theme support but hasn't validated this architecture with additional themes.

2. **Lead management is incomplete** - Leads can be captured but not operationally managed. Status displays but can't be updated. No notes, no assignment, no history.

3. **Internal linking is broken** - UniversalLinkBlock exists but isn't used consistently. ServiceCardItemBlock uses URLBlock. Editors can't link to pages in many contexts.

---

## Goals

### Primary Goals (P0)

1. **Prove multi-theme architecture** by implementing Theme B (minimum), with Theme C as stretch
2. **Enable lead operations** with status management, notes, assignment, and filtering
3. **Fix internal linking** across all blocks and add dedicated CTABlock

### Secondary Goals (P1)

4. **Reduce StandardPage overuse** with AboutPage and LandingPage
5. **Enable link health monitoring** with management command

### Non-Goals

- Search functionality (deferred to v0.7.1 or v0.8.x)
- Scheduled publishing
- Lead scoring or analytics dashboards
- Workflow automation

---

## Success Criteria

| Criterion | Measurement |
| --------- | ----------- |
| Theme B functional | Seeder generates complete site, all pages render |
| Theme contract documented | THEME-GUIDE.md updated with contract specification |
| Lead status manageable | Editors can change status in Wagtail admin |
| Lead notes work | Notes can be added with timestamps and author |
| Lead assignment works | Leads can be assigned to users |
| Internal links work everywhere | Page chooser appears in all link contexts |
| CTABlock available | CTABlock renders in all themes |
| Test coverage maintained | >= 85% overall coverage |

---

## Work Breakdown

### P0 Work Orders (Must Land)

| WO | Title | Tasks | Est. Hours | Dependencies |
| -- | ----- | ----- | ---------- | ------------ |
| 1 | Multi-theme Validation | 8 | 21-43 | None |
| 2 | Lead Management v1 | 10 | 19-31 | None |
| 3 | Internal Linking & CTAs | 8 | 15-24 | None |

**P0 Total:** 26 tasks, 55-98 hours

### P1 Work Orders (If Time)

| WO | Title | Tasks | Est. Hours | Dependencies |
| -- | ----- | ----- | ---------- | ------------ |
| 4 | New Page Types | 8 | 15-31 | WO1, WO3 |
| 5 | Link Health Tooling | 5 | 9-14 | WO3 |

**P1 Total:** 13 tasks, 24-45 hours

**Grand Total:** 39 tasks, 79-143 hours

---

## Task Inventory

### WO1: Multi-theme Validation (8 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO1-001 | Audit Theme A and Extract Contract | 2-3h | Low | `feature/multi-theme/001-theme-contract-audit` |
| WO1-002 | Create Theme B Skeleton | 1-2h | Low | `feature/multi-theme/002-theme-b-skeleton` |
| WO1-003 | Implement Theme B Base Templates | 4-6h | Med | `feature/multi-theme/003-theme-b-base-templates` |
| WO1-004 | Implement Theme B Page Templates | 4-6h | Med | `feature/multi-theme/004-theme-b-page-templates` |
| WO1-005 | Implement Theme B Block Templates | 6-8h | Med | `feature/multi-theme/005-theme-b-block-templates` |
| WO1-006 | Create Theme B Seeder Profile | 2-3h | Low | `feature/multi-theme/006-theme-b-seeder` |
| WO1-007 | Theme Contract Tests | 2-3h | Low | `feature/multi-theme/007-theme-contract-tests` |
| WO1-008 | Theme C Implementation (Stretch) | 8-12h | High | `feature/multi-theme/008-theme-c` |

### WO2: Lead Management v1 (10 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO2-001 | Add Lead Assignment Field | 2-3h | Low | `feature/leads-v1/001-lead-assignment` |
| WO2-002 | Create LeadNote Model | 1-2h | Low | `feature/leads-v1/002-lead-note-model` |
| WO2-003 | Create LeadActivity Model | 2-3h | Low | `feature/leads-v1/003-lead-activity-model` |
| WO2-004 | Lead Notes Admin Panel | 3-4h | Med | `feature/leads-v1/004-notes-admin-panel` |
| WO2-005 | Lead Activity Timeline | 2-3h | Low | `feature/leads-v1/005-activity-timeline` |
| WO2-006 | Enhanced Lead Filters | 3-4h | Med | `feature/leads-v1/006-enhanced-filters` |
| WO2-007 | Lead Search | 2-3h | Med | `feature/leads-v1/007-lead-search` |
| WO2-008 | Bulk Status Updates | 2-3h | Low | `feature/leads-v1/008-bulk-status` |
| WO2-009 | Inline Status Editing | 2-3h | Med | `feature/leads-v1/009-inline-status` |
| WO2-010 | Lead Source Taxonomy (P1) | 2-3h | Low | `feature/leads-v1/010-lead-source` |

### WO3: Internal Linking & CTAs (8 tasks)

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO3-001 | Audit All Link Usages | 1-2h | Low | `feature/internal-linking/001-link-audit` |
| WO3-002 | Fix ServiceCardItemBlock | 2-3h | Low | `feature/internal-linking/002-fix-service-cards` |
| WO3-003 | Fix Other Identified Blocks | 2-4h | Med | `feature/internal-linking/003-fix-other-blocks` |
| WO3-004 | Create CTABlock | 2-3h | Low | `feature/internal-linking/004-cta-block` |
| WO3-005 | CTABlock Theme Templates | 2-3h | Low | `feature/internal-linking/005-cta-templates` |
| WO3-006 | Link Rendering Consistency | 2-3h | Med | `feature/internal-linking/006-link-rendering` |
| WO3-007 | Link Validation in Admin | 2-3h | Med | `feature/internal-linking/007-link-validation` |
| WO3-008 | Comprehensive Link Tests | 2-3h | Low | `feature/internal-linking/008-link-tests` |

### WO4: New Page Types (8 tasks) - P1

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO4-001 | Create Supporting Blocks | 3-4h | Low | `feature/page-types/001-supporting-blocks` |
| WO4-002 | Create AboutPage Model | 2-3h | Low | `feature/page-types/002-about-page-model` |
| WO4-003 | Create LandingPage Model | 2-3h | Low | `feature/page-types/003-landing-page-model` |
| WO4-004 | AboutPage Theme Templates | 3-4h | Med | `feature/page-types/004-about-templates` |
| WO4-005 | LandingPage Theme Templates | 3-4h | Med | `feature/page-types/005-landing-templates` |
| WO4-006 | Page Type Seeder Support | 2-3h | Low | `feature/page-types/006-seeder-support` |
| WO4-007 | ContactPage (Stretch) | 4-5h | Med | `feature/page-types/007-contact-page` |
| WO4-008 | FAQPage (Stretch) | 4-5h | Med | `feature/page-types/008-faq-page` |

### WO5: Link Health Tooling (5 tasks) - P1

| ID | Task | Est. | Risk | Branch |
| -- | ---- | ---- | ---- | ------ |
| WO5-001 | Create Link Scanner Core | 3-4h | Med | `feature/link-health/001-link-scanner` |
| WO5-002 | Create check_links Command | 2-3h | Low | `feature/link-health/002-check-links-command` |
| WO5-003 | Add JSON Output Format | 1-2h | Low | `feature/link-health/003-json-output` |
| WO5-004 | Link Health Tests | 2-3h | Low | `feature/link-health/004-tests` |
| WO5-005 | Documentation | 1-2h | Low | `feature/link-health/005-documentation` |

---

## Dependency Graph

```
                    ┌─────────────────────────────────────────────┐
                    │            v0.6.1 RELEASE                   │
                    │     (prerequisite - must ship first)        │
                    └─────────────────────────────────────────────┘
                                        │
                    ┌───────────────────┼───────────────────┐
                    │                   │                   │
                    ▼                   ▼                   ▼
           ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
           │     WO1     │     │     WO2     │     │     WO3     │
           │ Multi-theme │     │  Leads v1   │     │   Linking   │
           │     (P0)    │     │    (P0)     │     │    (P0)     │
           └─────────────┘     └─────────────┘     └─────────────┘
                    │                                     │
                    │                                     │
                    ▼                                     ▼
           ┌─────────────┐                       ┌─────────────┐
           │     WO4     │                       │     WO5     │
           │ Page Types  │◄──────────────────────│ Link Health │
           │    (P1)     │    (uses CTABlock)    │    (P1)     │
           └─────────────┘                       └─────────────┘
```

### Inter-WO Dependencies

| Dependency | Reason |
| ---------- | ------ |
| WO4 depends on WO1 | New page types need Theme B templates |
| WO4 depends on WO3 | LandingPage uses CTABlock |
| WO5 depends on WO3 | Link health checks fixed link structure |

### Intra-WO Dependencies (critical paths)

**WO1:** 001 → 002 → 003 → 004/005 → 006 → 007 → 008
**WO2:** 002/003 → 001 → 004/005 → 006/007/008/009 → 010
**WO3:** 001 → 002/003 → 004 → 005 → 006/007 → 008
**WO4:** 001 → 002/003 → 004/005 → 006 → 007/008
**WO5:** 001 → 002 → 003 → 004/005

---

## Execution Strategy

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish foundations for all P0 work orders

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-001 (Theme Contract Audit) | 2-3h | Yes |
| WO2-002 (LeadNote Model) | 1-2h | Yes |
| WO2-003 (LeadActivity Model) | 2-3h | Yes |
| WO3-001 (Link Audit) | 1-2h | Yes |

### Phase 2: Core Implementation (Week 2-3)

**Goal:** Complete core P0 deliverables

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-002 through WO1-005 (Theme B) | 15-22h | Sequential |
| WO2-001, WO2-004, WO2-005 (Leads Admin) | 7-10h | Mostly parallel |
| WO3-002 through WO3-005 (Link Fixes + CTA) | 8-13h | Mostly parallel |

### Phase 3: Integration (Week 3-4)

**Goal:** Complete P0 and begin P1 if on track

| Task | Duration | Parallelizable |
| ---- | -------- | -------------- |
| WO1-006, WO1-007 (Theme B Seeder + Tests) | 4-6h | Sequential |
| WO2-006 through WO2-009 (Leads Filters + Actions) | 9-13h | Parallel |
| WO3-006 through WO3-008 (Link Polish + Tests) | 6-9h | Parallel |
| WO4 (if P0 on track) | 15-21h | After WO1, WO3 |
| WO5 (if P0 on track) | 9-14h | After WO3 |

### Phase 4: Polish & Release (Week 4)

**Goal:** Finalize, test, and release

- Integration testing across all features
- Theme B + Lead Management + Link fixes working together
- Documentation updates
- Release preparation

---

## Risk Mitigation

| Risk | Mitigation |
| ---- | ---------- |
| Theme B takes too long | Start early, have clear contract from audit, skip Theme C if needed |
| Lead management scope creep | Strict acceptance criteria, defer scoring/dashboards to v0.8.x |
| Link fixes cause regressions | Comprehensive tests before changes, test all themes |
| P1 doesn't fit | P1 is explicitly optional, P0 is the release |
| v0.6.1 delays | v0.7.0 planning can proceed, but execution blocks on v0.6.1 release |

---

## Testing Strategy

### Unit Tests

- All new models (LeadNote, LeadActivity, new blocks)
- All new management commands
- All block modifications

### Integration Tests

- Theme B renders all page types
- Lead workflow (create → assign → note → status change)
- Link rendering across all themes

### Manual Testing

- Theme B visual QA
- Lead admin UX review
- Link chooser functionality in all contexts

---

## Documentation Updates

| Document | Updates Needed |
| -------- | -------------- |
| `docs/dev/THEME-GUIDE.md` | Theme contract specification |
| `docs/dev/HANDBOOK.md` | Lead management guide, link health usage |
| `docs/dev/blocks-reference.md` | CTABlock documentation |
| `docs/dev/page-types-reference.md` | AboutPage, LandingPage (if P1 lands) |

---

## Rollout Plan

1. **v0.6.1 Release** (prerequisite)
   - Stabilization patch
   - Upgrade rehearsal on Sage & Stone

2. **v0.7.0-alpha** (internal)
   - P0 features complete
   - Internal testing

3. **v0.7.0-beta** (if needed)
   - P1 features added
   - Broader testing

4. **v0.7.0 Release**
   - Full release to develop → main
   - Tag and publish
   - Consumer upgrade documentation

---

## Artifacts

This implementation plan is supported by:

- `/planning/releases/0.7.0/VD.md` - Version Declaration
- `/planning/releases/0.7.0/WO/multi-theme-validation.md` - WO1 details
- `/planning/releases/0.7.0/WO/lead-management-v1.md` - WO2 details
- `/planning/releases/0.7.0/WO/internal-linking-ctas.md` - WO3 details
- `/planning/releases/0.7.0/WO/new-page-types.md` - WO4 details
- `/planning/releases/0.7.0/WO/link-health-tooling.md` - WO5 details

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
