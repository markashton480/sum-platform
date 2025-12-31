# Work Order: Elysian Consumer Site Validation

> **Parent:** [VD v0.8.0](../VD.md)
> **Branch:** `feature/elysian-validation`
> **Priority:** P0

---

## Overview

### Goal

Deploy and validate Elysian as the consumer site proving all v0.8.0 features work in a production context. This validates the upgrade path from v0.7.x and establishes visual regression baselines.

### Context

Elysian replaces LINTEL as the "run-against" consumer site for v0.8.0. It serves as:
- Real-world validation of all v0.8.0 features
- Test subject for visual regression baseline capture
- Upgrade path validation (v0.7.x -> v0.8.0)
- Proof that the platform delivers what we claim

### Dependency

This work order requires WO1-WO4 to be substantially complete before validation can begin.

---

## Acceptance Criteria

### Must Have

- [ ] Elysian site scaffolded via `sum init`
- [ ] Site deploys successfully with v0.8.0
- [ ] Blog search works on Elysian
- [ ] Lead analytics dashboard accessible
- [ ] Feature toggles function correctly
- [ ] Typography controls apply to output
- [ ] Upgrade from v0.7.x completes successfully
- [ ] Visual regression baselines captured and approved

### Should Have

- [ ] Real content populated (not just lorem ipsum)
- [ ] All page types exercised
- [ ] Multiple forms configured and tested
- [ ] Lead scoring active with test leads
- [ ] Documentation of validation results

### Could Have

- [ ] Staging environment for ongoing validation
- [ ] Automated validation scripts
- [ ] Performance benchmarks captured

---

## Technical Approach

### Site Scaffolding

```bash
# Scaffold Elysian site
cd clients/
sum init elysian --theme theme_a
cd elysian
```

### Configuration Checklist

| Feature | Configuration |
| ------- | ------------- |
| Theme | Theme A (or Theme B) |
| Blog | Enabled, 3+ posts created |
| Blog Search | Tested with queries |
| Lead Forms | 3+ forms configured |
| Lead Analytics | Dashboard populated |
| Feature Toggles | All tested (on and off) |
| Typography | Custom settings applied |

### Upgrade Path Testing

```bash
# Start with v0.7.x
pip install sum-core==0.7.x

# Verify site works
python manage.py check
python manage.py runserver

# Upgrade to v0.8.0
pip install sum-core==0.8.0
python manage.py migrate
python manage.py collectstatic

# Verify new features work
```

### Visual Regression Baselines

Capture baselines for all key pages:

| Page | Viewports |
| ---- | --------- |
| Home | Mobile, Tablet, Desktop |
| About | Mobile, Tablet, Desktop |
| Services | Mobile, Tablet, Desktop |
| Blog Index | Mobile, Tablet, Desktop |
| Blog Post | Mobile, Tablet, Desktop |
| Blog Search Results | Mobile, Tablet, Desktop |
| Contact | Mobile, Tablet, Desktop |
| Lead Dashboard (admin) | Desktop |

---

## Validation Checklist

### Blog Search Validation

- [ ] Search input visible on blog index
- [ ] Search query returns results
- [ ] No-results state displays correctly
- [ ] Pagination works with many results
- [ ] Search respects published status

### Lead Analytics Validation

- [ ] Dashboard accessible to staff
- [ ] Metrics display correctly
- [ ] Charts render properly
- [ ] Score filtering works
- [ ] Scores calculate for all leads

### Feature Toggle Validation

- [ ] Disable blog -> blog hidden
- [ ] Disable blog -> blog URLs 404
- [ ] Disable leads -> forms hidden
- [ ] Disable leads -> submissions rejected
- [ ] Enable all -> everything works

### Typography Validation

- [ ] Change heading weight -> applies to headings
- [ ] Change body weight -> applies to body text
- [ ] Change line height -> applies to paragraphs
- [ ] Change letter spacing -> applies site-wide

### Upgrade Path Validation

- [ ] Clean upgrade with no errors
- [ ] Migrations apply successfully
- [ ] Existing content preserved
- [ ] New features immediately available
- [ ] No breaking changes for existing functionality

---

## File Changes

### New Files (in clients/elysian/)

| File | Purpose |
| ---- | ------- |
| `clients/elysian/` | Elysian site directory |
| `docs/validation/v0.8.0-elysian.md` | Validation results |

### Modified Files

| File | Changes |
| ---- | ------- |
| `tests/visual/baselines/elysian/` | Visual baselines |

---

## Tasks

### TASK-001: Scaffold Elysian Site

**Estimate:** 2-3 hours
**Risk:** Low

Create Elysian site using sum init and configure basic structure.

**Acceptance Criteria:**
- [ ] Site scaffolded successfully
- [ ] Theme selected and applied
- [ ] Basic pages created (Home, About, Services, Contact)
- [ ] Site runs locally without errors
- [ ] Admin accessible and functional

**Technical Notes:**
- Use `sum init elysian --theme theme_a`
- Follow standard scaffolding process
- Verify all dependencies install

**Branch:** `feature/elysian-validation/001-scaffold`

---

### TASK-002: Configure Elysian with v0.8.0 Features

**Estimate:** 2-3 hours
**Risk:** Medium

Configure all v0.8.0 features on Elysian site.

**Acceptance Criteria:**
- [ ] Blog enabled with 3+ posts
- [ ] Lead forms configured (3+ placements)
- [ ] Feature toggles set
- [ ] Typography controls customized
- [ ] Test leads created for scoring

**Technical Notes:**
- Use realistic content (not lorem ipsum if possible)
- Configure multiple form types
- Create varied lead data for analytics

**Branch:** `feature/elysian-validation/002-configure`

---

### TASK-003: Test Blog Search on Elysian

**Estimate:** 1-2 hours
**Risk:** Low

Validate blog search functionality on Elysian.

**Acceptance Criteria:**
- [ ] Search input visible and functional
- [ ] Search returns correct results
- [ ] No-results handled gracefully
- [ ] Pagination works
- [ ] Screenshots captured

**Technical Notes:**
- Test various query types
- Test edge cases (empty, special chars)
- Document any issues found

**Branch:** `feature/elysian-validation/003-test-search`

---

### TASK-004: Test Lead Analytics on Elysian

**Estimate:** 1-2 hours
**Risk:** Low

Validate lead analytics and scoring on Elysian.

**Acceptance Criteria:**
- [ ] Dashboard accessible
- [ ] Metrics accurate for test data
- [ ] Charts render correctly
- [ ] Filtering by score works
- [ ] Scores update correctly

**Technical Notes:**
- Create leads with varying completeness
- Verify score calculations
- Check dashboard performance

**Branch:** `feature/elysian-validation/004-test-analytics`

---

### TASK-005: Capture Visual Regression Baselines

**Estimate:** 2-3 hours
**Risk:** Medium

Capture approved visual regression baselines for Elysian.

**Acceptance Criteria:**
- [ ] All page types captured
- [ ] All viewports captured
- [ ] Baselines reviewed and approved
- [ ] Baselines committed to repository
- [ ] Documentation updated

**Technical Notes:**
- Use Playwright screenshot capture
- Follow viewport specifications
- Get approval before committing

**Branch:** `feature/elysian-validation/005-capture-baselines`

---

### TASK-006: Test Upgrade Path v0.7.x to v0.8.0

**Estimate:** 2-3 hours
**Risk:** Medium

Validate upgrade path from v0.7.x to v0.8.0.

**Acceptance Criteria:**
- [ ] Start with clean v0.7.x site
- [ ] Upgrade to v0.8.0 completes
- [ ] Migrations apply successfully
- [ ] Existing content preserved
- [ ] New features work immediately
- [ ] Upgrade documented

**Technical Notes:**
- May need separate test environment
- Document exact upgrade steps
- Note any manual steps required

**Branch:** `feature/elysian-validation/006-upgrade-test`

---

## Execution Order

```
[WO1-WO4 Complete]
        |
        v
001 (Scaffold)
        |
        v
002 (Configure)
        |
        +---> 003 (Test Search)
        |
        +---> 004 (Test Analytics)
        |
        v
005 (Capture Baselines)
        |
        v
006 (Upgrade Test)
```

### Dependencies

This WO depends on WO1-WO4 being substantially complete. Individual validation tasks can proceed as features land.

---

## Testing Requirements

### Manual Testing

- All validation is primarily manual
- Document results in validation report
- Screenshot evidence for key validations

### Automated Testing

- Visual regression tests run against baselines
- Existing test suite passes on Elysian

---

## Documentation Deliverables

### Validation Report

Create `/docs/validation/v0.8.0-elysian.md` with:

- Validation date and version
- Features tested with pass/fail
- Issues found and resolutions
- Screenshots of key validations
- Upgrade path steps
- Performance notes

---

## Definition of Done

- [ ] All 6 tasks completed and merged
- [ ] All acceptance criteria met
- [ ] Elysian site running with v0.8.0
- [ ] All features validated
- [ ] Visual baselines captured and approved
- [ ] Upgrade path documented
- [ ] Validation report complete
- [ ] PR merged to `release/0.8.0`

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
| ---- | ---------- | ------ | ---------- |
| WO1-WO4 delays block validation | Medium | High | Begin scaffold early, validate incrementally |
| Content creation delays | Low | Low | Use placeholder content initially |
| Upgrade issues discovered | Medium | Medium | Document and fix before release |
| Visual baseline debates | Low | Low | Clear approval workflow |

---

## Sign-Off

| Role | Name | Date | Approved |
| ---- | ---- | ---- | -------- |
| Author | Claude-on-WSL | 2025-12-30 | - |
| Tech Lead | | | Pending |

---

## Revision History

| Date | Author | Changes |
| ---- | ------ | ------- |
| 2025-12-30 | Claude-on-WSL | Initial WO created |
