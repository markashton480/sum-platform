# Work Order

**Title:** `WO: Sage & Stone Deployment Review (v0.6.1)`

---

## Parent

**Version Declaration:** VD-0.6.1

---

## Branch

| Branch | Target |
|--------|--------|
| `fix/sage-stone-review` | `release/0.6.1` |

```bash
git checkout release/0.6.1
git checkout -b fix/sage-stone-review
git push -u origin fix/sage-stone-review
```

---

## Objective

- [ ] Conduct comprehensive review of Sage & Stone staging deployment
- [ ] Identify bugs, issues, and improvements from real-world usage
- [ ] Document findings and create follow-up issues
- [ ] Fix footer duplication bug (critical issue identified)
- [ ] Prioritize issues for inclusion in v0.6.1 or deferral to v0.7.0

---

## Scope

### In Scope

- Full review of Sage & Stone staging site (https://sage-and-stone.lintel.site)
- Bug identification and documentation
- **Footer duplication fix** (Theme hardcodes "Studio" section while CMS also includes it)
- Issue triage and prioritization
- Documentation of review findings

### Out of Scope

- New features for Sage & Stone
- Production deployment
- Client-specific customizations beyond bug fixes

---

## Known Issues Identified

### Footer Duplication Bug (Critical)

**Problem:** The footer displays two identical "Studio" sections instead of one.

**Root Cause:** Mismatch between two rendering systems:
- CMS-configured footer navigation menu includes a "Studio" section
- Theme template hardcodes a "Studio" section
- Both appear in the final output, causing duplication

**Proposed Solutions:**
1. **Immediate (Recommended):** Remove the manually-created "Studio" section from the Footer Navigation in the Wagtail admin interface, since the theme already displays this content automatically
2. **Long-term:** Refactor the theme template to prevent conflicts or clarify documentation about which component owns the Studio contact block

---

## Subtasks

| # | Task | Branch | Status |
|---|------|--------|--------|
| 1 | WO-SS-001: Complete staging site review | `fix/sage-stone-review/001-site-review` | 🔲 |
| 2 | WO-SS-002: Fix footer duplication bug | `fix/sage-stone-review/002-footer-fix` | 🔲 |
| 3 | WO-SS-003: Document findings and create issues | `fix/sage-stone-review/003-document-findings` | 🔲 |
| 4 | WO-SS-004: Triage and prioritize issues | `fix/sage-stone-review/004-triage-issues` | 🔲 |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Affected Paths

```
themes/theme_a/
└── templates/
    └── theme_a/
        └── includes/
            └── footer.html         # Modified: remove hardcoded Studio section

docs/
└── dev/
    └── reports/
        └── sage-stone-review/
            └── findings.md         # New: review findings
```

---

## Verification

### After Each Task Merge

```bash
git checkout fix/sage-stone-review
git pull origin fix/sage-stone-review
make lint && make test
```

### Before Feature PR

```bash
# Verify on staging site
# - Footer shows single Studio section
# - No visual regressions
# - All identified issues documented
```

---

## Risk

**Level:** Low

**Factors:**
- Theme changes could affect other clients
- Review may identify more issues than can be addressed in v0.6.1

**Mitigation:**
- Test theme changes across multiple scenarios
- Triage issues strictly - defer non-critical to v0.7.0

---

## Labels

- [ ] `type:work-order`
- [ ] `component:themes`
- [ ] `component:docs`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] Full review of Sage & Stone staging site completed
- [ ] Footer duplication bug fixed
- [ ] All identified issues documented as GitHub issues
- [ ] Critical/high-priority issues triaged for v0.6.1
- [ ] Lower-priority issues deferred to appropriate future milestones
- [ ] Review findings documented
- [ ] Feature branch merged to release branch
- [ ] Version Declaration updated
