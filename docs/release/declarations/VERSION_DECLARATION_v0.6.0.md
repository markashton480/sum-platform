---
name: Version Declaration
about: Version Declaration for milestone v0.6.0
title: `VD: Blog + Dynamic Forms + Cookie Consent + Legal Pages + CLI v2 (v0.6.0)`
labels: ["type:version-declaration"]
projects: ["markashton480/12"]
---

# Version Declaration: v0.6.0

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value              |
| ------------------ | ------------------ |
| **Version**        | `v0.6.0`           |
| **Type**           | `MINOR`            |
| **Milestone**      | `v0.6.0`           |
| **Branch**         | `release/0.6.0`    |
| **Target**         | `develop` → `main` |
| **Started**        | 2025-12-23         |
| **Target Release** | 2025-01-24         |

---

## Statement of Intent

### What This Version IS

v0.6.0 delivers four major feature sets: a **Dynamic Forms v1** system allowing site admins to create custom lead capture forms without code changes, a **Blog v1** feature as the first vertical slice exercising the full templating and theme system, a comprehensive **Cookie Consent + Legal Pages** system for GDPR compliance, and **CLI v2** transforming the 9-step manual project setup into a single `sum init --full` command. These features work together—Blog CTAs use DynamicFormBlock for consistent lead capture, and CLI v2 seeds themed sites with legal pages ready out of the box.

### What This Version IS NOT

- ❌ NOT including e-commerce or payment processing
- ❌ NOT including multi-language/i18n support
- ❌ NOT refactoring the existing lead pipeline (Lead model unchanged)
- ❌ NOT changing the theme system architecture
- ❌ NOT including granular cookie preferences UI (CMP-style)
- ❌ NOT including server-side consent audit logging
- ❌ NOT including hierarchical blog categories (single-level only)
- ❌ NOT including per-client seed presets (CLI Phase 4 - future)
- ❌ NOT including database backend selection (SQLite vs PostgreSQL)
- ❌ NOT including `sum init --undo` rollback functionality

---

## Features (Work Orders)

| #   | Feature                           | Work Order                                       | Branch                  | Status  |
| --- | --------------------------------- | ------------------------------------------------ | ----------------------- | ------- |
| 1   | Dynamic Forms v1                  | WO-061: Dynamic Form System                      | `feature/dynamic-forms` | 🔲 Todo |
| 2   | Blog v1                           | WO-062: Blog with Categories                     | `feature/blog`          | 🔲 Todo |
| 3   | Cookie Consent + Legal + Homepage | WO-060: Consent + Legal Pages + Starter Homepage | `feature/legal-consent` | 🔲 Todo |
| 4   | CLI v2 Enhanced Architecture      | WO-063: CLI v2 Enhanced Architecture             | `feature/cli-v2`        | 🔲 Todo |

**Status Legend:** 🔲 Todo | 🔄 In Progress | ✅ Done | ⏸️ Deferred

---

## Scope Boundaries

### Components In Scope

| Component                            | Changes Expected                                         |
| ------------------------------------ | -------------------------------------------------------- |
| `core/sum_core/forms/`               | New FormDefinition model, field blocks, dynamic renderer |
| `core/sum_core/blocks/`              | New DynamicFormBlock, form field blocks                  |
| `core/sum_core/pages/`               | BlogIndexPage, BlogPostPage, LegalPage types             |
| `core/sum_core/branding/`            | Cookie consent fields in SiteSettings                    |
| `core/sum_core/analytics/`           | Client-side analytics loader (consent-gated)             |
| `core/sum_core/templates/`           | Cookie banner, legal page, blog templates                |
| `core/sum_core/static/`              | cookie_consent.js, analytics_loader.js                   |
| `core/sum_core/management/commands/` | seed_homepage command                                    |
| `themes/theme_a/templates/`          | Blog, legal page, cookie banner theme overrides          |
| `cli/sum/`                           | Enhanced init, new run command, setup modules, utilities |
| `cli/sum/commands/`                  | init.py (enhanced), run.py (new), check.py (enhanced)    |
| `cli/sum/setup/`                     | New: orchestrator, venv, deps, database, seed, auth      |
| `cli/sum/utils/`                     | New: environment, output, prompts, django, validation    |
| `cli/tests/`                         | Tests for all new CLI modules                            |
| `docs/`                              | Wiring inventory, theme guide, CLI docs, developer notes |

### Components Out of Scope

| Component                 | Reason                                             |
| ------------------------- | -------------------------------------------------- |
| `core/sum_core/leads/`    | Existing pipeline unchanged (Lead model untouched) |
| `core/sum_core/services/` | No service page changes                            |
| `infrastructure/`         | No infra changes                                   |

---

## Expected Metrics

### At Version Completion (release/0.6.0 → develop)

| Metric                             | Expected      | Tolerance |
| ---------------------------------- | ------------- | --------- |
| Work Orders                        | 4             | ±0        |
| Total PRs merged to release branch | 26-34         | ±5        |
| Lines changed                      | +6,000 / -500 | ±50%      |
| Test coverage (new code)           | ≥80%          | -5%       |

### At Final Release (develop → main)

| Metric             | Expected | Tolerance   |
| ------------------ | -------- | ----------- |
| Commits (squashed) | 1        | 0           |
| Features included  | 4        | As declared |

### Performance Targets

| Metric                       | Target            |
| ---------------------------- | ----------------- |
| Lighthouse Score             | ≥90 all metrics   |
| CSS Bundle Size              | ≤100kb compressed |
| Form Submission Latency      | <500ms p95        |
| Zero Lost Leads              | Maintained        |
| `sum init --full` completion | <2 minutes        |

> **Note:** CLI "<2 minutes" target assumes warm pip cache. First-time installs may take longer.

---

## Dependencies & Prerequisites

### External Dependencies

| Dependency       | Version | Required By                        |
| ---------------- | ------- | ---------------------------------- |
| Wagtail          | 7.0+    | Blog pages, FormDefinition snippet |
| Django           | 5.2+    | Form widgets, StreamField          |
| Click            | 8.0+    | CLI commands                       |
| wagtail.snippets | -       | FormDefinition, Category models    |

### Internal Prerequisites

| Prerequisite                      | Status |
| --------------------------------- | ------ |
| v0.5.x stable and deployed        | ☐      |
| Test infrastructure ready         | ☐      |
| Theme A base templates functional | ☐      |
| Lead model and pipeline stable    | ☐      |
| Existing `sum init` v1 working    | ☐      |

---

## Risk Assessment

### Overall Risk Level: `Medium-High`

| Risk                                | Likelihood | Impact | Mitigation                                                     |
| ----------------------------------- | ---------- | ------ | -------------------------------------------------------------- |
| CLI orchestrator cascade errors     | Medium     | High   | Comprehensive unit tests, idempotent operations                |
| Form system complexity              | Medium     | High   | Incremental delivery, task-level PRs, comprehensive tests      |
| Cookie consent compliance           | Medium     | High   | Keep analytics out of HTML entirely (cache-safe)               |
| Blog/Forms coupling issues          | Low        | Medium | Clear interface contracts, DynamicFormBlock in CONTENT_BLOCKS  |
| Cross-component work (sum_core↔CLI) | Medium     | Medium | Clear ownership, integration tests after each merge            |
| Mode detection complexity (CLI)     | Medium     | Medium | Monorepo root detection via markers (`core/` + `boilerplate/`) |
| Template conflicts                  | Low        | Medium | Feature branches isolate changes                               |
| Migration issues                    | Low        | High   | Test migrations on copy of prod data                           |
| Theme overrides break contracts     | Medium     | Medium | Add DOM contract tests for banner + ToC                        |
| Seeding duplicates content          | Low        | Medium | Slug-scoped seeding, idempotent operations                     |

---

## Milestones & Checkpoints

| Checkpoint                         | Target Date | Criteria                                      |
| ---------------------------------- | ----------- | --------------------------------------------- |
| All WOs created                    | Week 1      | Issues exist with subtasks                    |
| Feature branches created           | Week 1      | Branches exist, linked to WOs                 |
| CLI Foundation + Django Config     | Week 1      | CLI-001, CLI-002 merged                       |
| Dynamic Forms Phase 1 complete     | Week 1      | FormDefinition + field blocks merged          |
| Cookie consent settings complete   | Week 1      | GH-0601 merged                                |
| CLI Env + DB/Auth modules          | Week 2      | CLI-003, CLI-004 merged                       |
| Dynamic Forms Phase 2 complete     | Week 2      | Form rendering + submission working           |
| Cookie banner + analytics complete | Week 2      | GH-0602, GH-0603, GH-0604 merged              |
| seed_homepage command              | Week 2      | CLI-005 merged                                |
| Blog feature complete              | Week 2-3    | BlogIndexPage, BlogPostPage, templates merged |
| Legal pages complete               | Week 3      | GH-0606 merged                                |
| CLI Orchestrator + Enhanced Init   | Week 3      | CLI-006, CLI-007 merged                       |
| Seeder + Docs complete             | Week 3      | GH-0607, GH-0608 merged                       |
| CLI Run + Check commands           | Week 4      | CLI-008 merged                                |
| Integration tests pass             | Week 4      | All features working together                 |
| Version RC ready                   | Week 4      | All features merged to release/0.6.0          |
| Version merged to develop          | Week 5      | PR approved and merged                        |
| Released to main                   | Week 5      | Tagged and synced to public                   |

---

## Work Order Summary

### WO-060: Cookie Consent + Legal Pages + Starter Homepage

**Objective:** Implement GDPR-compliant cookie consent, legal pages, and starter homepage seeding.

**Branch:** `feature/legal-consent`

**Subtasks:**

| #   | Issue   | Description                                             | Status |
| --- | ------- | ------------------------------------------------------- | ------ |
| 1   | GH-0601 | Add consent-related fields to SiteSettings + admin      | 🔲     |
| 2   | GH-0602 | Cookie banner include + a11y baseline + theme contract  | 🔲     |
| 3   | GH-0603 | Consent cookies + banner behavior + "Manage cookies" JS | 🔲     |
| 4   | GH-0604 | Client-side analytics loader (no scripts in HTML)       | 🔲     |
| 5   | GH-0605 | Tests for consent + analytics loader + theme contracts  | 🔲     |
| 6   | GH-0606 | Legal pages as CMS pages with Section-based ToC         | 🔲     |
| 7   | GH-0607 | Seeder updates (homepage + legal pages + footer links)  | 🔲     |
| 8   | GH-0608 | Docs updates — wiring inventory + theme guide           | 🔲     |

**Merge Order:** 0601 → 0602 → 0603 → 0604 → 0606 → 0607 → 0605 → 0608

**Risk Level:** Medium

---

### WO-061: Dynamic Forms v1

**Objective:** Allow admins to create custom forms via Wagtail admin with lead capture integration.

**Branch:** `feature/dynamic-forms`

**Phase 1: Foundation (~3-4 days)**

| #   | Description                                                    | Status |
| --- | -------------------------------------------------------------- | ------ |
| 1.1 | FormDefinition model (Wagtail Snippet, site-scoped)            | 🔲     |
| 1.2 | Field type blocks (text, email, phone, textarea, select, etc.) | 🔲     |
| 1.3 | DynamicFormBlock for StreamField embedding                     | 🔲     |

**Phase 2: Rendering + Submission (~3-4 days)**

| #   | Description                                        | Status |
| --- | -------------------------------------------------- | ------ |
| 2.1 | Runtime Django form generation from FormDefinition | 🔲     |
| 2.2 | Form templates (inline, modal, sidebar styles)     | 🔲     |
| 2.3 | Lead integration + form submission handler         | 🔲     |

**Phase 3: Integration + Polish**

| #   | Description                      | Status |
| --- | -------------------------------- | ------ |
| 3.1 | Clone/duplicate functionality    | 🔲     |
| 3.2 | Email notifications + auto-reply | 🔲     |
| 3.3 | Webhook integration              | 🔲     |
| 3.4 | Admin UI enhancements            | 🔲     |

**Critical Constraint:** Blog CTAs MUST use DynamicFormBlock to prevent form fragmentation.

**Risk Level:** Medium

---

### WO-062: Blog v1 with Categories

**Objective:** Add blog functionality with category filtering as first vertical slice of theme system.

**Branch:** `feature/blog`

**Subtasks:**

| #   | Description                                          | Status |
| --- | ---------------------------------------------------- | ------ |
| 1   | Category snippet model (single-level, no hierarchy)  | 🔲     |
| 2   | BlogIndexPage (listing + pagination + filtering)     | 🔲     |
| 3   | BlogPostPage (featured image, excerpt, reading time) | 🔲     |
| 4   | Blog templates for theme_a (index + post)            | 🔲     |
| 5   | Integration with DynamicFormBlock for CTAs           | 🔲     |
| 6   | RSS feed (optional)                                  | 🔲     |
| 7   | Integration tests                                    | 🔲     |

**Dependencies:** Requires Dynamic Forms Phase 1 complete (DynamicFormBlock available)

**Risk Level:** Low-Medium

---

### WO-063: CLI v2 Enhanced Architecture

**Objective:** Transform 9-step manual project setup into single `sum init --full` command delivering a fully-functioning themed site ready for testing in <2 minutes.

**Branch:** `feature/cli-v2`

**Subtasks:**

| #   | Issue   | Branch                                 | Description                  | Status |
| --- | ------- | -------------------------------------- | ---------------------------- | ------ |
| 1   | CLI-001 | `feature/cli-v2/001-foundation-utils`  | Foundation Utilities         | 🔲     |
| 2   | CLI-002 | `feature/cli-v2/002-django-config`     | Django Execution & Config    | 🔲     |
| 3   | CLI-003 | `feature/cli-v2/003-env-setup`         | Environment Setup Modules    | 🔲     |
| 4   | CLI-004 | `feature/cli-v2/004-db-auth`           | Database & Auth Modules      | 🔲     |
| 5   | CLI-005 | `feature/cli-v2/005-seed-homepage-cmd` | seed_homepage Command        | 🔲     |
| 6   | CLI-006 | `feature/cli-v2/006-seed-orchestrator` | Seeding & Orchestrator       | 🔲     |
| 7   | CLI-007 | `feature/cli-v2/007-enhanced-init`     | Enhanced Init Command        | 🔲     |
| 8   | CLI-008 | `feature/cli-v2/008-run-check`         | Run Command & Enhanced Check | 🔲     |

**Merge Dependency Graph:**

```
CLI-001 Foundation Utilities
    │
    ▼
CLI-002 Django & Config
    │
    ├────────┬────────────────┐
    ▼        ▼                ▼
CLI-003  CLI-004          CLI-005
Env Setup DB & Auth       seed_homepage (parallel)
    │        │                │
    └────┬───┴────────────────┘
         ▼
    CLI-006 Seeding & Orchestrator
         │
         ▼
    CLI-007 Enhanced Init
         │
         ▼
    CLI-008 Run & Check
```

**Key Design Decisions:**

- **Monorepo root detection:** Path resolution walks upward to find repo root (markers: `core/` + `boilerplate/`)
- **Python interpreter:** Django commands ALWAYS run under project's `.venv/bin/python`
- **Idempotency:** All operations safe to re-run (no corruption, no duplicates)
- **Backward compatibility:** v1 `sum init` behavior maintained

**Hot Files (merge conflicts likely):**

| File                        | Owners                    | Notes                |
| --------------------------- | ------------------------- | -------------------- |
| `cli/sum/utils/__init__.py` | CLI-001, CLI-002          | Export consolidation |
| `cli/sum/setup/__init__.py` | CLI-003, CLI-004, CLI-006 | Export consolidation |
| `cli/sum/commands/init.py`  | CLI-007                   | Complete rewrite     |
| `cli/sum/cli.py`            | CLI-007, CLI-008          | Command registration |

**Risk Level:** Medium

---

## Feature Dependency Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        v0.6.0 DEPENDENCY GRAPH                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  TRACK A: Dynamic Forms                    TRACK B: Blog                    │
│  ┌──────────────────┐                     ┌──────────────────┐             │
│  │ FormDefinition   │                     │ Category Snippet │             │
│  │ Model (1.1)      │                     └────────┬─────────┘             │
│  └────────┬─────────┘                              │                        │
│           │                                        ▼                        │
│           ▼                               ┌──────────────────┐             │
│  ┌──────────────────┐                     │ BlogIndexPage    │             │
│  │ DynamicFormBlock │◄────────────────────│ BlogPostPage     │             │
│  │ (1.3)            │  CRITICAL CONSTRAINT│ (uses FormBlock) │             │
│  └────────┬─────────┘                     └──────────────────┘             │
│           │                                                                 │
│           ▼                                                                 │
│  ┌──────────────────────────────────────────┐                              │
│  │ Form Rendering + Submission (Phase 2)    │                              │
│  └──────────────────────────────────────────┘                              │
│                                                                             │
│  TRACK C: Cookie Consent + Legal           TRACK D: CLI v2                 │
│  ┌──────────────────┐                     ┌──────────────────┐             │
│  │ SiteSettings     │                     │ CLI-001 Utils    │             │
│  │ (GH-0601)        │                     └────────┬─────────┘             │
│  └────────┬─────────┘                              │                        │
│           │                                        ▼                        │
│           ▼                               ┌──────────────────┐             │
│  ┌──────────────────┐                     │ CLI-002 Django   │             │
│  │ Cookie Banner    │                     └────────┬─────────┘             │
│  │ (GH-0602-0604)   │                              │                        │
│  └────────┬─────────┘                     ┌────────┼────────┐              │
│           │                               ▼        ▼        ▼              │
│           ▼                            CLI-003  CLI-004  CLI-005           │
│  ┌──────────────────┐                     │        │        │              │
│  │ Legal Pages      │                     └────────┼────────┘              │
│  │ (GH-0606)        │                              ▼                        │
│  └────────┬─────────┘                     ┌──────────────────┐             │
│           │                               │ CLI-006 Orchestr │             │
│           ▼                               └────────┬─────────┘             │
│  ┌──────────────────┐                              │                        │
│  │ Seeder Updates   │◄─────────────────────────────┤                        │
│  │ (GH-0607)        │  CLI seeds legal pages       ▼                        │
│  └──────────────────┘                     ┌──────────────────┐             │
│                                           │ CLI-007/008      │             │
│                                           │ Init + Run       │             │
│                                           └──────────────────┘             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
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

### CLI v2 Verification

```bash
# Full integration test
sum init test-project --full --ci
cd clients/test-project
sum check
curl http://127.0.0.1:8000/ | grep "Welcome"
```

- [ ] `sum init project --full --ci` creates working project in <2 minutes
- [ ] `sum run` works from anywhere in monorepo
- [ ] `sum check` catches common configuration issues
- [ ] All error messages have clear next steps
- [ ] Backward compatible: `sum init` (without flags) works as before
- [ ] Idempotent: all operations safe to re-run
- [ ] Test coverage >80% for new CLI modules

---

## Affected Paths Summary

```
core/sum_core/
├── forms/                    # New: FormDefinition, fields, dynamic renderer
├── blocks/                   # Modified: DynamicFormBlock added
├── pages/                    # New: BlogIndexPage, BlogPostPage, LegalPage
├── branding/models.py        # Modified: cookie consent fields
├── analytics/templatetags/   # Modified: analytics_tags.py
├── templates/
│   ├── theme/base.html       # Modified: cookie banner include
│   └── sum_core/includes/    # New: cookie_banner.html
├── static/sum_core/js/       # New: cookie_consent.js, analytics_loader.js
└── management/commands/      # New: seed_homepage.py

themes/theme_a/templates/     # Modified: blog, legal, banner overrides

cli/
├── sum/
│   ├── cli.py                # Modified: register new commands
│   ├── config.py             # New: SetupConfig dataclass
│   ├── exceptions.py         # New: Exception hierarchy
│   ├── commands/
│   │   ├── init.py           # Modified: enhanced with new flags
│   │   ├── check.py          # Modified: enhanced validation
│   │   └── run.py            # New: sum run command
│   ├── setup/                # New: orchestrator, venv, deps, database, seed, auth
│   └── utils/                # New: environment, output, prompts, django, validation
└── tests/                    # New: tests for all CLI modules

docs/                         # Modified: wiring inventory, theme guide, CLI docs
```

---

## Changelog Draft

```markdown
## [v0.6.0] - 2025-01-24

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

- **CLI v2 Enhanced Architecture**
  - New `sum init --full` command: fully-functioning themed site in <2 minutes
  - New `sum run` command with port conflict handling
  - Enhanced `sum check` with additional validations
  - Setup modules: venv, deps, database, auth, seed, orchestrator
  - Utility modules: environment, output, prompts, django, validation
  - `seed_homepage` management command in sum_core
  - 100% idempotent operations (safe to re-run)

### Changed

- SiteSettings extended with cookie consent configuration fields
- Base template includes cookie banner conditionally
- `sum init` enhanced with `--full`, `--quick`, `--ci`, `--no-prompt`, `--skip-*`, `--run` flags
- CLI now auto-detects monorepo root for path resolution

### Fixed

- (list any bug fixes included)
```

---

## Pre-Release Checklist

Before merging `release/0.6.0` → `develop`:

- [ ] All Work Orders marked Done (4/4)
- [ ] All feature branches merged to release branch
- [ ] `make release-check` passes on release branch
- [ ] `make lint && make test` passes
- [ ] Lighthouse scores ≥90 across all metrics
- [ ] Test coverage ≥80% for new code
- [ ] Form submission latency <500ms p95
- [ ] `sum init --full --ci` completes in <2 minutes
- [ ] Zero lost leads verified
- [ ] Changelog draft finalized
- [ ] Version numbers updated
- [ ] Documentation updated (README.md, cli.md, CONTRIBUTING.md)
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
