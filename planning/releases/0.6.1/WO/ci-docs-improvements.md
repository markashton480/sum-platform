# Work Order

**Title:** `WO: CI & Documentation Enhancements (v0.6.1)`

---

## Parent

**Version Declaration:** VD-0.6.1
**Tracking Issues:** #229, #225, #186

---

## Branch

| Branch | Target |
|--------|--------|
| `chore/ci-docs-improvements` | `release/0.6.1` |

```bash
git checkout release/0.6.1
git checkout -b chore/ci-docs-improvements
git push -u origin chore/ci-docs-improvements
```

---

## Objective

- [ ] Implement fast-path CI for docs/CI-only changes (#229)
- [ ] Enable Claude review workflow to submit reviews (#225)
- [ ] Document Lead.form_data structure (#186)
- [ ] Reduce CI pipeline runtime for documentation changes

---

## Scope

### In Scope

- GitHub Actions workflow modifications
- CI path-based job skipping
- Claude review workflow permissions
- Lead.form_data documentation
- Developer handbook updates

### Out of Scope

- New CI features beyond fast-path
- Production deployment workflows
- New documentation structure

---

## Subtasks

| # | Task | Branch | Status |
|---|------|--------|--------|
| 1 | WO-CI-001: Implement docs-only CI fast-path | `chore/ci-docs-improvements/001-ci-fastpath` | 🔲 |
| 2 | WO-CI-002: Configure Claude review permissions | `chore/ci-docs-improvements/002-claude-review` | 🔲 |
| 3 | WO-CI-003: Document Lead.form_data structure | `chore/ci-docs-improvements/003-form-data-docs` | 🔲 |
| 4 | WO-CI-004: Update developer handbook | `chore/ci-docs-improvements/004-handbook-update` | 🔲 |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Affected Paths

```
.github/
├── workflows/
│   ├── ci.yml                  # Modified: fast-path logic
│   └── claude-review.yml       # Modified: permissions
└── CODEOWNERS                  # Modified if needed

docs/
├── dev/
│   └── HANDBOOK.md             # Modified: Lead.form_data docs
└── api/
    └── lead-form-data.md       # New: dedicated form_data docs
```

---

## Verification

### After Each Task Merge

```bash
git checkout chore/ci-docs-improvements
git pull origin chore/ci-docs-improvements
make lint && make test
```

### Before Feature PR

```bash
# Test CI fast-path with docs-only PR
# Verify Claude review can submit reviews
# Validate documentation accuracy against code
```

---

## Risk

**Level:** Low

**Factors:**
- CI changes could affect build reliability
- Documentation may drift from implementation

**Mitigation:**
- Test CI changes in feature branch first
- Review documentation against actual code

---

## Labels

- [ ] `type:work-order`
- [ ] `component:docs`
- [ ] `component:ci`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] Docs-only PRs skip expensive CI checks
- [ ] Claude review workflow can submit reviews
- [ ] Lead.form_data structure documented
- [ ] Developer handbook updated
- [ ] CI pipeline runtime reduced for docs changes
- [ ] Feature branch merged to release branch
- [ ] Version Declaration updated
