---
name: Version Declaration
about: Version Declaration for a milestone
title: `VD: <Feature Description> (vX.Y.Z)`
labels: ["type:version-declaration"]
projects: ["markashton480/12"]
---

# Version Declaration: vX.Y.0

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value              |
| ------------------ | ------------------ |
| **Version**        | `vX.Y.0`           |
| **Type**           | `MINOR` / `MAJOR`  |
| **Milestone**      | `vX.Y.0`           |
| **Branch**         | `release/X.Y.0`    |
| **Target**         | `develop` → `main` |
| **Started**        | YYYY-MM-DD         |
| **Target Release** | YYYY-MM-DD         |

---

## Statement of Intent

### What This Version IS

> _2-3 sentences describing the theme and goals of this release._

Example: "v0.7.0 introduces a dynamic form system allowing site admins to create custom forms without code changes. It also adds blog functionality with categories and a cookie consent system for GDPR compliance."

### What This Version IS NOT

> _Explicitly state what is OUT OF SCOPE for this version._

Example:

- ❌ NOT including e-commerce or payment processing
- ❌ NOT including multi-language support
- ❌ NOT refactoring the existing lead pipeline
- ❌ NOT changing the theme system architecture

---

## Features (Work Orders)

List all features planned for this version. Each becomes a Work Order issue.

| #   | Feature       | Work Order               | Branch          | Status  |
| --- | ------------- | ------------------------ | --------------- | ------- |
| 1   | Dynamic Forms | WO: Dynamic Form System  | `feature/forms` | 🔲 Todo |
| 2   | Blog System   | WO: Blog with Categories | `feature/blog`  | 🔲 Todo |
| 3   | Legal/GDPR    | WO: Cookie Consent       | `feature/legal` | 🔲 Todo |

**Status Legend:** 🔲 Todo | 🔄 In Progress | ✅ Done | ⏸️ Deferred

---

## Scope Boundaries

### Components In Scope

| Component                   | Changes Expected        |
| --------------------------- | ----------------------- |
| `core/sum_core/forms/`      | New dynamic form models |
| `core/sum_core/blocks/`     | New form block          |
| `core/sum_core/pages/`      | Blog page types         |
| `themes/theme_a/templates/` | Form and blog templates |
| `tests/`                    | Tests for new features  |

### Components Out of Scope

| Component              | Reason                      |
| ---------------------- | --------------------------- |
| `core/sum_core/leads/` | Existing pipeline unchanged |
| `cli/`                 | No CLI changes this version |
| `infrastructure/`      | No infra changes            |

---

## Expected Metrics

### At Version Completion (release/X.Y.0 → develop)

| Metric                             | Expected      | Tolerance |
| ---------------------------------- | ------------- | --------- |
| Work Orders                        | 3             | ±1        |
| Total PRs merged to release branch | 8-12          | ±3        |
| Lines changed                      | +2,000 / -500 | ±50%      |

### At Final Release (develop → main)

| Metric             | Expected | Tolerance   |
| ------------------ | -------- | ----------- |
| Commits (squashed) | 1        | 0           |
| Features included  | 3        | As declared |

> **Note:** These are sanity checks. A "MINOR" release adding 15,000 lines for 3 features might be fine. A "PATCH" release adding 3,000 lines is suspicious.

---

## Dependencies & Prerequisites

### External Dependencies

| Dependency | Version | Required By  |
| ---------- | ------- | ------------ |
| Wagtail    | 7.0+    | Blog pages   |
| Django     | 5.2+    | Form widgets |

### Internal Prerequisites

| Prerequisite               | Status |
| -------------------------- | ------ |
| v0.6.x stable and deployed | ☐      |
| Test infrastructure ready  | ☐      |
| Theme templates updated    | ☐      |

---

## Risk Assessment

### Overall Risk Level: `Medium`

| Risk                   | Likelihood | Impact | Mitigation                           |
| ---------------------- | ---------- | ------ | ------------------------------------ |
| Form system complexity | Medium     | High   | Incremental delivery, task-level PRs |
| Template conflicts     | Low        | Medium | Feature branches isolate changes     |
| Migration issues       | Low        | High   | Test migrations on copy of prod data |

---

## Milestones & Checkpoints

| Checkpoint                | Target Date | Criteria                                |
| ------------------------- | ----------- | --------------------------------------- |
| All WOs created           | Week 1      | Issues exist with subtasks              |
| Feature branches created  | Week 1      | Branches exist, linked to WOs           |
| Forms feature complete    | Week 2      | All forms tasks merged to feature/forms |
| Blog feature complete     | Week 3      | All blog tasks merged to feature/blog   |
| Version RC ready          | Week 4      | All features merged to release/X.Y.0    |
| Version merged to develop | Week 4      | PR approved and merged                  |
| Released to main          | Week 4      | Tagged and synced to public             |

---

## Work Order Summary

### WO-1: Dynamic Form System

**Objective:** Allow admins to create custom forms via Wagtail admin.

**Subtasks:**

- [ ] GH-XXX: FormDefinition snippet model
- [ ] GH-XXX: Form field blocks (text, email, select, etc.)
- [ ] GH-XXX: DynamicFormBlock for StreamField
- [ ] GH-XXX: Form rendering and submission
- [ ] GH-XXX: Integration tests

**Branch:** `feature/forms`

---

### WO-2: Blog with Categories

**Objective:** Add blog functionality with category filtering.

**Subtasks:**

- [ ] GH-XXX: Category snippet
- [ ] GH-XXX: BlogIndexPage
- [ ] GH-XXX: BlogPostPage
- [ ] GH-XXX: Category filtering
- [ ] GH-XXX: Templates and tests

**Branch:** `feature/blog`

---

### WO-3: Cookie Consent (GDPR)

**Objective:** Add cookie consent banner for GDPR compliance.

**Subtasks:**

- [ ] GH-XXX: Cookie consent model and settings
- [ ] GH-XXX: Consent banner template
- [ ] GH-XXX: Analytics integration (respect consent)

**Branch:** `feature/legal`

---

## Changelog Draft

Prepare the changelog entry as work progresses:

```markdown
## [vX.Y.0] - YYYY-MM-DD

### Added

- Dynamic form system: create custom forms via admin
- Blog pages with category filtering
- Cookie consent banner for GDPR compliance

### Changed

- (list any changes to existing behavior)

### Fixed

- (list any bug fixes included)
```

---

## Pre-Release Checklist

Before merging `release/X.Y.0` → `develop`:

- [ ] All Work Orders marked Done
- [ ] All feature branches merged to release branch
- [ ] `make release-check` passes on release branch
- [ ] Changelog draft finalized
- [ ] Version numbers updated (will be done in release prep)
- [ ] Release audit requested

---

## Release Audit Log

_Append audit results here:_

```
[YYYY-MM-DD HH:MM] Audit by: <agent/human>
PR: #NNN (release/X.Y.0 → develop)
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
[YYYY-MM-DD] Released as vX.Y.0
- What went well:
- What could improve:
- Follow-up items:
```
