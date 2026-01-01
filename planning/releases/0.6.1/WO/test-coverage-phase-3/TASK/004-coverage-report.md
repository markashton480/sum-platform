# Task

**Title:** `WO-TEST-004: Coverage verification and reporting`

---

## Parent

**Work Order:** #458 (WO: Test Coverage Phase 3)
**Tracking Issue:** #474

---

## Branch

| Branch | Target |
|--------|--------|
| `test/coverage-phase-3/004-coverage-report` | `test/coverage-phase-3` |

```bash
git checkout test/coverage-phase-3
git pull origin test/coverage-phase-3
git checkout -b test/coverage-phase-3/004-coverage-report
git push -u origin test/coverage-phase-3/004-coverage-report
```

---

## Deliverable

This task will deliver:

- Overall coverage verification (≥85%)
- Coverage report generation
- Identification of remaining coverage gaps
- Documentation of coverage improvements achieved

---

## Boundaries

### Do

- Run full test suite with coverage
- Generate coverage report
- Verify overall coverage ≥85%
- Document coverage improvements from this work order
- Identify any remaining critical gaps
- Run tests multiple times to verify no flaky tests

### Do NOT

- ❌ Do not add new tests (consolidation only)
- ❌ Do not modify production code
- ❌ Do not ignore failing tests
- ❌ Do not lower coverage thresholds

---

## Acceptance Criteria

- [ ] Overall test coverage ≥85%
- [ ] Coverage report generated and reviewed
- [ ] No flaky tests (all tests pass 5 consecutive runs)
- [ ] Coverage improvements documented
- [ ] Any gaps identified for future work
- [ ] CI coverage checks pass

---

## Test Commands

```bash
make lint
make test

# Full coverage report
python -m pytest --cov=core/sum_core --cov=cli --cov-report=term-missing --cov-report=html

# Verify no flaky tests
python -m pytest --count=5

# Check coverage threshold
python -m pytest --cov=core/sum_core --cov=cli --cov-fail-under=85
```

---

## Files Expected to Change

```
docs/dev/reports/coverage-phase-3-report.md    # New: coverage report
```

---

## Dependencies

**Depends On:**
- [ ] WO-TEST-001: CLI scaffold_project unit tests
- [ ] WO-TEST-002: Complete BLOG-016 test improvements
- [ ] WO-TEST-003: Seeder profile and --clear tests

**Blocks:**
- Nothing — this is the final task

---

## Risk

**Level:** Low

**Why:**
- Verification task only
- No production code changes

---

## Labels

- [ ] `type:task`
- [ ] `component:core`
- [ ] `component:cli`
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
docs(tests): add coverage phase 3 verification report

- Document overall coverage achievement (≥85%)
- List coverage improvements from phase 3
- Identify any remaining gaps for future work
- Verify no flaky tests

Closes #TBD
```

---

## Coverage Report Template

```markdown
# Test Coverage Phase 3 Report

## Summary

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Overall Coverage | XX% | XX% | +X% |
| CLI Module | XX% | XX% | +X% |
| Blog Module | XX% | XX% | +X% |
| Seeder Module | XX% | XX% | +X% |

## Improvements Made

### CLI Tests (#458)
- Added scaffold_project tests
- Coverage: XX%

### Blog Tests (#187)
- Completed BLOG-016 deferred improvements
- Coverage: XX%

### Seeder Tests (#173)
- Added profile and --clear tests
- Coverage: XX%

## Remaining Gaps

| Module | Current | Target | Priority |
|--------|---------|--------|----------|
| ... | XX% | XX% | Low/Medium/High |

## Flaky Test Check

✅ All tests passed 5 consecutive runs
```
