---
name: Version Declaration
about: Version Declaration for milestone v0.6.0
title: `VD: Blog + Dynamic Forms + Cookie Consent + Legal Pages (v0.6.0)`
labels: ["type:version-declaration"]
projects: ["markashton480/12"]
---

# Version Declaration: v0.6.0

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value                                                   |
| ------------------ | ------------------------------------------------------- |
| **Version**        | `v0.6.0`                                                |
| **Type**           | `MINOR`                                                 |
| **Milestone**      | `v0.6.0`                                                |
| **Branch**         | `release/0.6.0`                                         |
| **Target**         | `develop` → `main`                                      |
| **Started**        | 2025-12-23                                              |
| **Target Release** | 2025-01-17                                              |

---

## Statement of Intent

### What This Version IS

v0.6.0 delivers three interconnected feature sets: a **Dynamic Forms v1** system allowing site admins to create custom lead capture forms without code changes, a **Blog v1** feature as the first vertical slice exercising the full templating and theme system, and a comprehensive **Cookie Consent + Legal Pages** system for GDPR compliance. These features are intentionally coupled—Blog CTAs must use DynamicFormBlock to maintain consistency across all lead capture touchpoints.

### What This Version IS NOT

- ❌ NOT including e-commerce or payment processing
- ❌ NOT including multi-language/i18n support
- ❌ NOT refactoring the existing lead pipeline (Lead model unchanged)
- ❌ NOT changing the theme system architecture
- ❌ NOT including granular cookie preferences UI (CMP-style)
- ❌ NOT including server-side consent audit logging
- ❌ NOT including hierarchical blog categories (single-level only)
- ❌ NOT including CLI v2 enhancements (deferred to v2.0.0)

---

## Features (Work Orders)

List all features planned for this version. Each becomes a Work Order issue.

| #   | Feature                              | Work Order                                          | Branch                   | Status  |
| --- | ------------------------------------ | --------------------------------------------------- | ------------------------ | ------- |
| 1   | Dynamic Forms v1                     | WO-061: Dynamic Form System                         | `feature/dynamic-forms`  | 🔲 Todo |
| 2   | Blog v1                              | WO-062: Blog with Categories                        | `feature/blog`           | 🔲 Todo |
| 3   | Cookie Consent + Legal + Homepage    | WO-060: Consent + Legal Pages + Starter Homepage    | `feature/legal-consent`  | 🔲 Todo |

**Status Legend:** 🔲 Todo | 🔄 In Progress | ✅ Done | ⏸️ Deferred

---

## Scope Boundaries

### Components In Scope

| Component                              | Changes Expected                                         |
| -------------------------------------- | -------------------------------------------------------- |
| `core/sum_core/forms/`                 | New FormDefinition model, field blocks, dynamic renderer |
| `core/sum_core/blocks/`                | New DynamicFormBlock, form field blocks                  |
| `core/sum_core/pages/`                 | BlogIndexPage, BlogPostPage, LegalPage types             |
| `core/sum_core/branding/`              | Cookie consent fields in SiteSettings                    |
| `core/sum_core/analytics/`             | Client-side analytics loader (consent-gated)             |
| `core/sum_core/templates/`             | Cookie banner, legal page, blog templates                |
| `core/sum_core/static/`                | cookie_consent.js, analytics_loader.js                   |
| `themes/theme_a/templates/`            | Blog, legal page, cookie banner theme overrides          |
| `management/commands/`                 | Seeder updates for starter homepage + legal pages        |
| `tests/`                               | Tests for all new features                               |
| `docs/`                                | Wiring inventory, theme guide, developer notes           |

### Components Out of Scope

| Component                 | Reason                                              |
| ------------------------- | --------------------------------------------------- |
| `core/sum_core/leads/`    | Existing pipeline unchanged (Lead model untouched)  |
| `cli/`                    | No CLI changes this version (CLI v2 is v2.0.0)      |
| `infrastructure/`         | No infra changes                                    |
| `core/sum_core/services/` | No service page changes                             |

---

## Expected Metrics

### At Version Completion (release/0.6.0 → develop)

| Metric                             | Expected        | Tolerance |
| ---------------------------------- | --------------- | --------- |
| Work Orders                        | 3               | ±0        |
| Total PRs merged to release branch | 18-24           | ±5        |
| Lines changed                      | +4,000 / -500   | ±50%      |
| Test coverage (new code)           | ≥80%            | -5%       |

### At Final Release (develop → main)

| Metric             | Expected | Tolerance   |
| ------------------ | -------- | ----------- |
| Commits (squashed) | 1        | 0           |
| Features included  | 3        | As declared |

### Performance Targets

| Metric                    | Target           |
| ------------------------- | ---------------- |
| Lighthouse Score          | ≥90 all metrics  |
| CSS Bundle Size           | ≤100kb compressed|
| Form Submission Latency   | <500ms p95       |
| Zero Lost Leads           | Maintained       |

> **Note:** These are sanity checks. A "MINOR" release adding 15,000 lines for 3 features might be fine. A "PATCH" release adding 3,000 lines is suspicious.

---

## Dependencies & Prerequisites

### External Dependencies

| Dependency         | Version | Required By                          |
| ------------------ | ------- | ------------------------------------ |
| Wagtail            | 7.0+    | Blog pages, FormDefinition snippet   |
| Django             | 5.2+    | Form widgets, StreamField            |
| wagtail.snippets   | -       | FormDefinition, Category models      |

### Internal Prerequisites

| Prerequisite                          | Status |
| ------------------------------------- | ------ |
| v0.5.x stable and deployed            | ☐      |
| Test infrastructure ready             | ☐      |
| Theme A base templates functional     | ☐      |
| Lead model and pipeline stable        | ☐      |

---

## Risk Assessment

### Overall Risk Level: `Medium`

| Risk                              | Likelihood | Impact | Mitigation                                                    |
| --------------------------------- | ---------- | ------ | ------------------------------------------------------------- |
| Form system complexity            | Medium     | High   | Incremental delivery, task-level PRs, comprehensive tests     |
| Cookie consent compliance         | Medium     | High   | Keep analytics out of HTML entirely (cache-safe)              |
| Blog/Forms coupling issues        | Low        | Medium | Clear interface contracts, DynamicFormBlock in CONTENT_BLOCKS |
| Template conflicts                | Low        | Medium | Feature branches isolate changes                              |
| Migration issues                  | Low        | High   | Test migrations on copy of prod data                          |
| Theme overrides break contracts   | Medium     | Medium | Add DOM contract tests for banner + ToC                       |
| Seeding duplicates content        | Low        | Medium | Slug-scoped seeding, idempotent operations                    |

---

## Milestones & Checkpoints

| Checkpoint                           | Target Date | Criteria                                          |
| ------------------------------------ | ----------- | ------------------------------------------------- |
| All WOs created                      | Week 1      | Issues exist with subtasks                        |
| Feature branches created             | Week 1      | Branches exist, linked to WOs                     |
| Dynamic Forms Phase 1 complete       | Week 1      | FormDefinition + field blocks merged              |
| Cookie consent settings complete     | Week 1      | GH-0601 merged to feature/legal-consent           |
| Dynamic Forms Phase 2 complete       | Week 2      | Form rendering + submission working               |
| Cookie banner + analytics complete   | Week 2      | GH-0602, GH-0603, GH-0604 merged                  |
| Blog feature complete                | Week 2-3    | BlogIndexPage, BlogPostPage, templates merged     |
| Legal pages complete                 | Week 3      | GH-0606 merged                                    |
| Seeder + Docs complete               | Week 3      | GH-0607, GH-0608 merged                           |
| Integration tests pass               | Week 3      | All features working together                     |
| Version RC ready                     | Week 4      | All features merged to release/0.6.0              |
| Version merged to develop            | Week 4      | PR approved and merged                            |
| Released to main                     | Week 4      | Tagged and synced to public                       |

---

## Work Order Summary

### WO-060: Cookie Consent + Legal Pages + Starter Homepage

**Objective:** Implement GDPR-compliant cookie consent, legal pages, and starter homepage seeding.

**Branch:** `feature/legal-consent`

**Subtasks:**

- [ ] GH-0601: Add consent-related fields to SiteSettings + admin wiring
- [ ] GH-0602: Cookie banner include + a11y baseline + theme contract
- [ ] GH-0603: Consent cookies + banner behavior + "Manage cookies" flow (JS)
- [ ] GH-0604: Client-side analytics loader (no scripts in HTML) + config emission
- [ ] GH-0605: Tests for consent + analytics loader + theme contracts
- [ ] GH-0606: Legal pages as CMS "article" pages with Section-based ToC
- [ ] GH-0607: Seeder + starter profile updates (homepage + legal pages + footer links)
- [ ] GH-0608: Docs updates — wiring inventory + theme guide + contracts

**Merge Order:** 0601 → 0602 → 0603 → 0604 → 0606 → 0607 → 0605 → 0608

**Risk Level:** Medium

---

### WO-061: Dynamic Forms v1

**Objective:** Allow admins to create custom forms via Wagtail admin with lead capture integration.

**Branch:** `feature/dynamic-forms`

**Phase 1: Foundation (~3-4 days)**
- [ ] 1.1: FormDefinition model (Wagtail Snippet, site-scoped)
- [ ] 1.2: Field type blocks (text, email, phone, textarea, select, checkbox, radio, file)
- [ ] 1.3: DynamicFormBlock for StreamField embedding

**Phase 2: Rendering + Submission (~3-4 days)**
- [ ] 2.1: Runtime Django form generation from FormDefinition
- [ ] 2.2: Form templates (inline, modal, sidebar presentation styles)
- [ ] 2.3: Lead integration + form submission handler enhancement

**Phase 3: Integration + Polish**
- [ ] 3.1: Clone/duplicate functionality
- [ ] 3.2: Email notifications + auto-reply
- [ ] 3.3: Webhook integration
- [ ] 3.4: Admin UI enhancements

**Critical Constraint:** Blog CTAs MUST use DynamicFormBlock (selecting FormDefinition) to prevent form fragmentation.

**Risk Level:** Medium

---

### WO-062: Blog v1 with Categories

**Objective:** Add blog functionality with category filtering as first vertical slice of theme system.

**Branch:** `feature/blog`

**Subtasks:**

- [ ] Category snippet model (single-level, no hierarchy)
- [ ] BlogIndexPage (listing with pagination + category filtering)
- [ ] BlogPostPage (article with featured image, excerpt, reading time, body StreamField)
- [ ] Blog templates for theme_a (index + post + category filtering)
- [ ] Integration with DynamicFormBlock for CTAs
- [ ] RSS feed (optional)
- [ ] Integration tests

**Dependencies:** Requires Dynamic Forms Phase 1 complete (DynamicFormBlock available)

**Risk Level:** Low-Medium

---

## Feature Dependency Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                     v0.6.0 DEPENDENCY GRAPH                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PARALLEL TRACK A: Dynamic Forms                                    │
│  ┌──────────────────┐                                              │
│  │ FormDefinition   │ ──► Wagtail Snippet (site-scoped)            │
│  │ Model (1.1)      │                                               │
│  └────────┬─────────┘                                              │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ Field Type       │ ◄──►│ DynamicFormBlock │                     │
│  │ Blocks (1.2)     │     │ (1.3)            │                     │
│  └────────┬─────────┘     └────────┬─────────┘                     │
│           │                        │                                │
│           ▼                        ▼                                │
│  ┌──────────────────────────────────────────┐                      │
│  │ Form Rendering + Submission (Phase 2)    │                      │
│  └────────────────────┬─────────────────────┘                      │
│                       │                                             │
│                       ▼                                             │
│  PARALLEL TRACK B: Blog ─────────────────────                      │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ Category Snippet │     │ BlogPostPage     │                     │
│  └────────┬─────────┘     │ (uses            │                     │
│           │               │ DynamicFormBlock)│◄── CRITICAL         │
│           ▼               └────────┬─────────┘    CONSTRAINT       │
│  ┌──────────────────┐              │                               │
│  │ BlogIndexPage    │◄─────────────┘                               │
│  └──────────────────┘                                              │
│                                                                     │
│  PARALLEL TRACK C: Cookie Consent + Legal                          │
│  ┌──────────────────┐                                              │
│  │ SiteSettings     │ (GH-0601)                                    │
│  │ consent fields   │                                               │
│  └────────┬─────────┘                                              │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ Cookie Banner    │────►│ Consent JS +     │                     │
│  │ (GH-0602)        │     │ Analytics (0603-4)│                    │
│  └──────────────────┘     └──────────────────┘                     │
│           │                        │                                │
│           ▼                        ▼                                │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ Legal Pages      │     │ Seeder Updates   │                     │
│  │ (GH-0606)        │────►│ (GH-0607)        │                     │
│  └──────────────────┘     └──────────────────┘                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Verification Checklist

### Smoke Tests (After Each Merge)

```bash
make lint
make test
python manage.py test
```

### Dynamic Forms Verification

- [ ] FormDefinition creatable in Wagtail admin
- [ ] All field types render correctly
- [ ] Form submission creates Lead (no schema change)
- [ ] Email notifications send correctly
- [ ] Webhook fires on submission

### Blog Verification

- [ ] BlogIndexPage renders with pagination
- [ ] Category filtering works
- [ ] BlogPostPage renders with featured image
- [ ] Reading time auto-calculates
- [ ] DynamicFormBlock renders in post body

### Cookie Consent Verification

- [ ] With no consent cookie: banner visible; analytics scripts NOT in HTML
- [ ] After Accept: consent cookie set; analytics scripts load dynamically
- [ ] After Reject: consent cookie set; analytics does NOT load
- [ ] "Manage cookies" re-opens banner and allows changing decision
- [ ] Version mismatch triggers re-prompt

### Legal Pages Verification

- [ ] Legal pages render with ToC + section anchors
- [ ] Mobile ToC uses accessible toggle (aria-expanded)
- [ ] Print button works
- [ ] Pages linked in footer

### Seeder Verification

- [ ] Running seeder twice produces identical tree (idempotent)
- [ ] Starter homepage renders with theme header/footer
- [ ] Legal pages exist, published, and linked in footer

---

## Changelog Draft

Prepare the changelog entry as work progresses:

```markdown
## [v0.6.0] - 2025-01-17

### Added

- **Dynamic Forms v1**: Create custom lead capture forms via Wagtail admin
  - FormDefinition snippet with configurable field types
  - DynamicFormBlock for embedding forms in any StreamField
  - Support for text, email, phone, textarea, select, checkbox, radio, file fields
  - Email notifications and webhook integration
  - Clone/duplicate functionality for rapid form iteration

- **Blog v1**: First vertical slice with full theme system support
  - BlogIndexPage with pagination and category filtering
  - BlogPostPage with featured image, excerpt, and reading time
  - Category snippet for organizing posts
  - Integration with DynamicFormBlock for CTAs

- **Cookie Consent + Legal Pages**
  - GDPR-compliant cookie consent banner with Accept/Reject
  - "Manage cookies" link for preference changes
  - Client-side analytics loader (no scripts in server-rendered HTML)
  - LegalPage type with Section-based Table of Contents
  - Starter homepage and legal pages via seeder

### Changed

- SiteSettings extended with cookie consent configuration fields
- Base template includes cookie banner conditionally
- Seeder updated with starter profile for homepage + legal pages

### Fixed

- (list any bug fixes included)
```

---

## Pre-Release Checklist

Before merging `release/0.6.0` → `develop`:

- [ ] All Work Orders marked Done
- [ ] All feature branches merged to release branch
- [ ] `make release-check` passes on release branch
- [ ] Lighthouse scores ≥90 across all metrics
- [ ] Test coverage ≥80% for new code
- [ ] Form submission latency <500ms p95
- [ ] Zero lost leads verified
- [ ] Changelog draft finalized
- [ ] Version numbers updated
- [ ] Release audit requested

---

## Release Audit Log

_Append audit results here:_

```
[YYYY-MM-DD HH:MM] Audit by: <agent/human>
PR: #NNN (release/0.6.0 → develop)
Result: PASS / FAIL
Notes: <observations>
```

---

## Sign-Off

| Role    | Name | Date | Approved |
| ------- | ---- | ---- | -------- |
| Author  |      |      | ☐        |
| Auditor |      |      | ☐        |

---

## Post-Release Notes

_After release, document any lessons learned:_

```
[YYYY-MM-DD] Released as v0.6.0
- What went well:
- What could improve:
- Follow-up items:
```
