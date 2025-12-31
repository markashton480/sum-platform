# Task

**Title:** `WO-TEST-002: Complete BLOG-016 test improvements`

---

## Parent

**Work Order:** WO: Test Coverage Improvements Phase 3 (v0.6.1)
**Tracking Issue:** #187

---

## Branch

| Branch | Target |
|--------|--------|
| `test/coverage-phase-3/002-blog-tests` | `test/coverage-phase-3` |

```bash
git checkout test/coverage-phase-3
git pull origin test/coverage-phase-3
git checkout -b test/coverage-phase-3/002-blog-tests
git push -u origin test/coverage-phase-3/002-blog-tests
```

---

## Deliverable

This task will deliver:

- Completed test improvements deferred from BLOG-016
- Enhanced blog module test coverage
- Tests for blog page models
- Tests for blog listing and filtering
- Tests for blog category functionality

---

## Boundaries

### Do

- Complete deferred test improvements from #187
- Add tests for BlogPage model
- Add tests for BlogIndexPage
- Add tests for category filtering
- Add tests for blog listing pagination
- Test blog-specific template tags if any
- Achieve ≥80% coverage for blog module

### Do NOT

- ❌ Do not modify blog production code
- ❌ Do not add new blog features
- ❌ Do not change blog templates
- ❌ Do not modify existing passing tests

---

## Acceptance Criteria

- [ ] All deferred test improvements from #187 completed
- [ ] BlogPage model has test coverage
- [ ] BlogIndexPage has test coverage
- [ ] Category filtering is tested
- [ ] Pagination is tested
- [ ] Coverage for blog module ≥80%
- [ ] All tests pass locally and in CI
- [ ] No flaky tests

---

## Test Commands

```bash
make lint
make test

# Run specific tests
python -m pytest tests/blog/ -v

# Check coverage
python -m pytest tests/blog/ --cov=core/sum_core/blog --cov-report=term-missing
```

---

## Files Expected to Change

```
tests/
└── blog/
    ├── test_models.py           # Modified/New
    ├── test_pages.py            # Modified/New
    └── test_categories.py       # New
```

---

## Dependencies

**Depends On:**
- [ ] None — can run in parallel with WO-TEST-001

**Blocks:**
- WO-TEST-004: Coverage verification and reporting

---

## Risk

**Level:** Low

**Why:**
- Adding tests only, no production code changes
- Completing previously planned work

---

## Labels

- [ ] `type:task`
- [ ] `component:core`
- [ ] `risk:low`
- [ ] Milestone: `v0.6.1`

---

## Definition of Done

- [ ] Acceptance criteria met
- [ ] `make lint && make test` passes
- [ ] PR merged to feature branch
- [ ] **Model Used** field set
- [ ] `model:*` label applied
- [ ] Parent Work Order updated

---

## Commit Message

```
test(blog): complete BLOG-016 deferred test improvements

- Add BlogPage model tests
- Add BlogIndexPage tests
- Add category filtering tests
- Add pagination tests
- Achieve ≥80% coverage for blog module

Closes #187
```
