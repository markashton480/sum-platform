# Work Order

**Title:** `WO: Test Coverage Improvements Phase 3 (v0.6.1)`

---

## Parent

**Version Declaration:** #460 (VD-0.6.1)
**Tracking Issue:** #458
**Related Issues:** #187, #173

---

## Branch

| Branch | Target |
|--------|--------|
| `test/coverage-phase-3` | `release/0.6.1` |

```bash
git checkout release/0.6.1
git checkout -b test/coverage-phase-3
git push -u origin test/coverage-phase-3
```

---

## Objective

- [ ] Add unit tests for CLI scaffold_project functionality (#458)
- [ ] Complete deferred BLOG-016 test improvements (#187)
- [ ] Add test coverage for seed_showroom profiles and --clear behavior (#173)
- [ ] Achieve overall test coverage ≥85%
- [ ] Ensure all tests pass locally and in CI

---

## Scope

### In Scope

- CLI scaffold_project unit tests
- Blog test improvements (deferred from BLOG-016)
- Seeder test coverage for profiles and --clear flag
- Test coverage reporting and metrics

### Out of Scope

- Production code changes (tests only)
- New features or functionality
- Performance optimizations

---

## Subtasks

| # | Task | Issue | Branch | Status |
|---|------|-------|--------|--------|
| 1 | WO-TEST-001: CLI scaffold_project unit tests | #471 | `test/coverage-phase-3/001-cli-tests` | 🔲 |
| 2 | WO-TEST-002: Complete BLOG-016 test improvements | #472 | `test/coverage-phase-3/002-blog-tests` | 🔲 |
| 3 | WO-TEST-003: Seeder profile and --clear tests | #473 | `test/coverage-phase-3/003-seeder-tests` | 🔲 |
| 4 | WO-TEST-004: Coverage verification and reporting | #474 | `test/coverage-phase-3/004-coverage-report` | 🔲 |

**Status:** 🔲 Todo | 🔄 In Progress | ✅ Done

---

## Affected Paths

```
tests/
├── cli/
│   └── test_scaffold_project.py    # New
├── blog/
│   └── test_blog_*.py              # Modified
└── management/
    └── test_seed_showroom.py       # Modified

cli/
└── tests/
    └── test_*.py                   # Modified
```

---

## Verification

### After Each Task Merge

```bash
git checkout test/coverage-phase-3
git pull origin test/coverage-phase-3
make lint && make test
```

### Before Feature PR

```bash
# Run full test suite with coverage
pytest --cov=core/sum_core --cov=cli --cov-report=term-missing
# Verify coverage ≥85%

# Verify no flaky tests
pytest --count=5 tests/  # Run tests multiple times
```

---

## Risk

**Level:** Low

**Factors:**
- Tests are additive, minimal risk of breaking existing functionality
- Flaky tests could affect CI reliability

**Mitigation:**
- Run tests multiple times to verify reliability
- Review test isolation and fixtures

---

## Labels

- [ ] `type:work-order`
- [ ] `component:core`
- [ ] `component:cli`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] All subtasks merged to feature branch
- [ ] `make lint && make test` passes on feature branch
- [ ] CLI scaffold_project has unit test coverage
- [ ] Blog tests from #187 complete and passing
- [ ] Seeder tests cover profiles and --clear flag
- [ ] Overall test coverage ≥85%
- [ ] No flaky tests introduced
- [ ] Feature branch merged to release branch
- [ ] Version Declaration updated
