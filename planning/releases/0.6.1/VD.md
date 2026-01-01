# Version Declaration: v0.6.1

> **This document is the source of truth for what this version contains.**
> Create one Version Declaration per milestone. All Work Orders reference this.
> The release audit will verify the final PR against this declaration.

---

## Version Metadata

| Field              | Value                                                   |
| ------------------ | ------------------------------------------------------- |
| **Version**        | `v0.6.1`                                                |
| **Type**           | `PATCH`                                                 |
| **Milestone**      | `v0.6.1`                                                |
| **Branch**         | `release/0.6.1`                                         |
| **Target**         | `develop` → `main`                                      |
| **Started**        | 2025-12-29                                              |
| **Target Release** | 2026-01-17                                              |

---

## Statement of Intent

### What This Version IS

v0.6.1 is a focused PATCH release that stabilizes v0.6.0 by addressing critical Theme A issues, publishing CLI v2, improving test coverage, enhancing CI workflows, filling documentation gaps, and reviewing the initial Sage & Stone deployment. This release contains **no new features** - only fixes, improvements, and technical debt reduction.

The release is composed of five Work Orders: **Theme A Critical Fixes** (WO #461, related: #292), **CLI v2 Publishing & Distribution** (WO #457), **Test Coverage Improvements** (WO #458, related: #187, #173), **CI & Documentation Enhancements** (WO #462, related: #229, #225, #186), and **Sage & Stone Deployment Review** (WO #459).

### What This Version IS NOT

- ❌ NOT adding new features (feature work belongs in v0.7.0+)
- ❌ NOT refactoring core architecture
- ❌ NOT changing the Lead model or pipeline
- ❌ NOT adding dynamic form enhancements (#183, #177 deferred to v0.7.0)
- ❌ NOT implementing blog enhancements (#172, #176 deferred to v0.7.0)
- ❌ NOT including production deployment work
- ❌ NOT changing the theme system architecture
- ❌ NOT including any breaking changes

---

## Features (Work Orders)

List all features planned for this version. Each becomes a Work Order issue.

| #   | Feature                              | Work Order                                      | Branch                          | Status  |
| --- | ------------------------------------ | ----------------------------------------------- | ------------------------------- | ------- |
| 1   | Theme A Critical Fixes               | #461: WO: Theme A Critical Fixes (v0.6.1)       | `fix/theme-a-critical-issues`   | 🔲 Todo |
| 2   | CLI v2 Publishing & Distribution     | #457: WO: CLI v2 Publishing (v0.6.1)            | `feature/cli-publishing`        | 🔲 Todo |
| 3   | Test Coverage Improvements           | #458: WO: Test Coverage Phase 3 (v0.6.1)        | `test/coverage-phase-3`         | 🔲 Todo |
| 4   | CI & Documentation Enhancements      | #462: WO: CI & Documentation Enhancements (v0.6.1) | `chore/ci-docs-improvements`    | 🔲 Todo |
| 5   | Sage & Stone Deployment Review       | #459: WO: Sage & Stone Review (v0.6.1)          | `fix/sage-stone-review`         | 🔲 Todo |

**Status Legend:** 🔲 Todo | 🔄 In Progress | ✅ Done | ⏸️ Deferred

---

## Scope Boundaries

### Components In Scope

| Component                              | Changes Expected                                         |
| -------------------------------------- | -------------------------------------------------------- |
| `themes/theme_a/`                      | CSS fixes, template corrections, critical visual bugs    |
| `cli/sum_cli/`                         | Publishing configuration, packaging improvements         |
| `tests/`                               | New test coverage for CLI, forms, blog, seeder           |
| `.github/workflows/`                   | CI workflow optimizations and review automation          |
| `docs/`                                | Lead.form_data documentation, updated guides             |
| `core/sum_core/forms/`                 | Test coverage only (no logic changes)                    |
| `core/sum_core/blog/`                  | Test coverage only (no logic changes)                    |
| `management/commands/seed_showroom.py` | Test coverage only (no logic changes)                    |

### Components Out of Scope

| Component                 | Reason                                              |
| ------------------------- | --------------------------------------------------- |
| `core/sum_core/leads/`    | No changes unless critical bug found                |
| `core/sum_core/blocks/`   | No changes unless critical bug found                |
| `core/sum_core/pages/`    | No changes unless critical bug found                |
| `core/sum_core/services/` | No changes planned                                  |

---

## Expected Metrics

### At Version Completion (release/0.6.1 → develop)

| Metric                             | Expected                   | Tolerance |
| ---------------------------------- | -------------------------- | --------- |
| Work Orders                        | 5                          | ±0        |
| Total PRs merged to release branch | 4-6                        | ±2        |
| Lines changed                      | <1000                      | ±500      |
| Test coverage (overall)            | ≥85%                       | -3%       |

### At Final Release (develop → main)

| Metric             | Expected | Tolerance   |
| ------------------ | -------- | ----------- |
| Commits (squashed) | 1        | 0           |
| Features included  | 5        | As declared |

### Performance Targets

| Metric                    | Target           |
| ------------------------- | ---------------- |
| Lighthouse Score          | ≥90 all metrics  |
| Test Suite Runtime        | <5 minutes       |
| CI Pipeline Runtime       | <10 minutes      |

> **Note:** This is a PATCH release - metrics should show stability with minimal churn.

---

## Dependencies & Prerequisites

### External Dependencies

| Dependency         | Version | Required By                          |
| ------------------ | ------- | ------------------------------------ |
| sum-core package   | v0.6.1 (planned) | Consumer repos (Sage & Stone)        |
| psycopg            | 3.2+    | Production PostgreSQL connectivity   |
| Django             | 5.x     | Provided via sum-core packaging      |
| Wagtail            | 7.x     | Provided via sum-core packaging      |

**Version bump note:**
- Update version to v0.6.1 in `pyproject.toml`, `core/pyproject.toml`, `core/sum_core/__init__.py`, `CHANGELOG.md`, `boilerplate/requirements.txt`, and `cli/sum_cli/boilerplate/requirements.txt`.
- CLI version bumps to v2.0.0 independently (already done in current branch).

### Internal Prerequisites

| Prerequisite                          | Status |
| ------------------------------------- | ------ |
| v0.6.0 stable and deployed            | ✅     |
| Test infrastructure ready             | ✅     |
| CI workflows functional               | ✅     |
| Theme A deployed to staging           | ✅     |

---

## Risk Assessment

### Overall Risk Level: `Low`

| Risk                              | Likelihood | Impact | Mitigation                                                    |
| --------------------------------- | ---------- | ------ | ------------------------------------------------------------- |
| Theme A CSS regressions           | Low        | Medium | Visual regression testing, staging validation                 |
| CLI packaging breaks installs     | Medium     | High   | Test installation from PyPI test instance before release      |
| Test additions break CI           | Low        | Low    | Run full test suite locally before merge                      |
| CI workflow changes break builds  | Low        | Medium | Test in feature branch, monitor first runs carefully          |
| Documentation drift               | Low        | Low    | Review against current codebase state                         |

---

## Milestones & Checkpoints

| Checkpoint                           | Target Date | Criteria                                          |
| ------------------------------------ | ----------- | ------------------------------------------------- |
| All WOs created                      | 2025-12-29  | 5 Work Order issues exist and scoped              |
| Sage & Stone review complete         | 2025-12-30  | Review completed, issues created and triaged      |
| Feature branches created             | 2025-12-30  | All 5 feature branches created from develop       |
| Theme A fixes complete               | 2025-12-31  | PR merged, visual QA passed                       |
| CLI publishing complete              | 2025-12-31  | CLI v2.0.0 published to PyPI                      |
| Test coverage improvements complete  | 2026-01-01  | Coverage ≥85%, all new tests passing              |
| CI & docs complete                   | 2026-01-02  | Workflows optimized, docs updated                 |
| Version RC ready                     | 2026-01-02  | All completed WOs merged to release/0.6.1         |
| Release audit                        | 2026-01-03  | Audit pass, ready for merge to develop            |

---

## Work Order Summary

### WO 1: Theme A Critical Fixes (v0.6.1)

**Issue:** #292
**Branch:** `fix/theme-a-critical-issues`
**Scope:**
- Fix critical CSS bugs affecting layout
- Resolve high-priority visual issues
- Ensure responsive design works across breakpoints
- Validate against theme contract requirements

**Acceptance Criteria:**
- [ ] All critical and high-priority issues from #292 resolved
- [ ] Visual QA passed on staging environment
- [ ] No CSS regressions introduced
- [ ] Lighthouse scores maintained ≥90

---

### WO 2: CLI v2 Publishing & Distribution (v0.6.1)

**Issue:** #457
**Branch:** `feature/cli-publishing`
**Scope:**
- Package CLI v2 for PyPI distribution
- Test installation from PyPI test instance
- Update installation documentation
- Verify CLI works in fresh environments

**Acceptance Criteria:**
- [ ] CLI v2.0.0 published to PyPI
- [ ] Installation via `pip install sum-cli` works
- [ ] `sum --version` returns 2.0.0
- [ ] Documentation updated with pip installation instructions

---

### WO 3: Test Coverage Improvements (v0.6.1)

**Issues:** #458, #187, #173
**Branch:** `test/coverage-phase-3`
**Scope:**
- Add unit tests for CLI scaffold_project (#458)
- Complete deferred BLOG-016 test improvements (#187)
- Add coverage for seed_showroom profiles and --clear behavior (#173)
- Target ≥85% overall test coverage

**Acceptance Criteria:**
- [ ] CLI scaffold_project has unit test coverage
- [ ] Blog test improvements from #187 completed
- [ ] Seeder test coverage for profiles and --clear flag
- [ ] Overall test coverage ≥85%
- [ ] All tests pass locally and in CI

---

### WO 4: CI & Documentation Enhancements (v0.6.1)

**Issues:** #229, #225, #186
**Branch:** `chore/ci-docs-improvements`
**Scope:**
- Implement fast-path CI for docs/CI-only changes (#229)
- Enable Claude review workflow to submit reviews (#225)
- Document Lead.form_data structure (#186)
- Update developer handbook as needed

**Acceptance Criteria:**
- [ ] CI skips expensive checks for docs-only PRs
- [ ] Claude review workflow can submit reviews (permissions configured)
- [ ] Lead.form_data structure documented in HANDBOOK.md or dedicated doc
- [ ] CI pipeline runtime reduced for docs changes

---

### WO 5: Sage & Stone Deployment Review (v0.6.1)

**Issue:** #459
**Branch:** `fix/sage-stone-review`
**Scope:**
- Conduct comprehensive review of Sage & Stone staging deployment
- Identify bugs, issues, and improvements from real-world usage
- Document findings and create follow-up issues
- Prioritize issues for inclusion in v0.6.1 or deferral to v0.7.0
- **Fix footer duplication bug** (identified: Theme hardcodes "Studio" section while CMS also includes it, causing duplicate display)

**Known Issues Identified:**
- Footer duplication: Two identical "Studio" sections appear - CMS footer navigation and theme template both render this content

**Acceptance Criteria:**
- [ ] Full review of Sage & Stone staging site completed
- [ ] All identified issues documented as GitHub issues
- [ ] Footer duplication bug fixed (remove hardcoded Studio section from theme or document CMS configuration)
- [ ] Critical/high-priority issues triaged for v0.6.1
- [ ] Lower-priority issues deferred to appropriate future milestones
- [ ] Review findings documented

---

## Feature Dependency Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                     v0.6.1 DEPENDENCY GRAPH                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PARALLEL TRACK A: Theme A Fixes                                    │
│  ┌──────────────────┐                                              │
│  │ CSS Bug Fixes    │ ──► Visual regression tests                  │
│  │ (#292)           │                                               │
│  └────────┬─────────┘                                              │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐                                              │
│  │ Staging QA       │                                               │
│  └──────────────────┘                                              │
│                                                                     │
│  PARALLEL TRACK B: CLI Publishing                                   │
│  ┌──────────────────┐                                              │
│  │ Package CLI      │ ──► PyPI test                                │
│  │ (#457)           │                                               │
│  └────────┬─────────┘                                              │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐                                              │
│  │ PyPI Production  │                                               │
│  └──────────────────┘                                              │
│                                                                     │
│  PARALLEL TRACK C: Test Coverage                                    │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ CLI Tests (#458) │     │ Blog Tests (#187)│                     │
│  └────────┬─────────┘     └────────┬─────────┘                     │
│           │                        │                                │
│           └────────┬───────────────┘                                │
│                    │                                                │
│                    ▼                                                │
│           ┌──────────────────┐                                      │
│           │ Seeder Tests     │                                      │
│           │ (#173)           │                                      │
│           └──────────────────┘                                      │
│                                                                     │
│  PARALLEL TRACK D: CI & Docs                                        │
│  ┌──────────────────┐     ┌──────────────────┐                     │
│  │ CI Fast-path     │     │ Claude Review    │                     │
│  │ (#229)           │     │ Workflow (#225)  │                     │
│  └────────┬─────────┘     └────────┬─────────┘                     │
│           │                        │                                │
│           └────────┬───────────────┘                                │
│                    │                                                │
│                    ▼                                                │
│           ┌──────────────────┐                                      │
│           │ Lead.form_data   │                                      │
│           │ Docs (#186)      │                                      │
│           └──────────────────┘                                      │
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

### Theme A Verification

- [ ] All layouts render correctly on desktop
- [ ] All layouts render correctly on mobile
- [ ] No CSS console errors
- [ ] Theme contract requirements met
- [ ] Lighthouse scores ≥90 all metrics

### CLI Publishing Verification

- [ ] `pip install sum-cli` works in fresh virtualenv
- [ ] `sum --version` returns 2.0.0
- [ ] `sum init` creates project successfully
- [ ] CLI commands work as expected

### Test Coverage Verification

- [ ] Overall coverage ≥85%
- [ ] CLI scaffold_project has test coverage
- [ ] Blog tests from #187 complete and passing
- [ ] Seeder tests cover profiles and --clear flag
- [ ] No flaky tests introduced

### CI & Documentation Verification

- [ ] Docs-only PRs skip expensive CI checks
- [ ] Claude review workflow can submit reviews
- [ ] Lead.form_data structure documented
- [ ] CI pipeline runs faster for docs changes

---

## Changelog Draft

Prepare the changelog entry as work progresses:

```markdown
## [v0.6.1] - 2026-01-03

### Fixed

- **Theme A**: Resolved critical CSS layout bugs and high-priority visual issues
- **CLI**: Published CLI v2.0.0 to PyPI for easier distribution

### Changed

- **CI**: Implemented fast-path for docs-only changes (reduces pipeline runtime)
- **CI**: Enabled Claude review workflow to submit automated reviews

### Added

- **Tests**: Added unit test coverage for CLI scaffold_project functionality
- **Tests**: Completed deferred blog test improvements
- **Tests**: Added seeder test coverage for profiles and --clear behavior
- **Docs**: Documented Lead.form_data structure and usage patterns

### Improved

- Test coverage increased to ≥85%
- CI pipeline runtime reduced for documentation changes
```

---

## Definition of Done

- All Work Orders in this Version Declaration are closed
- `release/0.6.1` merged to `develop` and `main` per release process
- `make release-check` passes on `release/0.6.1`
- All verification checklist items passed
- Test coverage ≥85%
- Changelog entry finalized for v0.6.1
- CLI v2.0.0 published to PyPI and installation verified

---

## Pre-Release Checklist

Before merging `release/0.6.1` → `develop`:

- [ ] All Work Orders marked Done
- [ ] All feature branches merged to release branch
- [ ] `make release-check` passes on release branch
- [ ] Test coverage ≥85%
- [ ] CLI v2.0.0 published and verified
- [ ] Theme A visual QA passed
- [ ] CI optimizations validated
- [ ] Documentation updates complete
- [ ] Changelog draft finalized
- [ ] Version numbers updated in all required files
- [ ] Release audit requested

---

## Release Audit Log

_Append audit results here:_

```
[YYYY-MM-DD HH:MM] Audit by: <agent/human>
PR: #NNN (release/0.6.1 → develop)
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
[YYYY-MM-DD] Released as v0.6.1
- What went well:
- What could improve:
- Follow-up items:
```
