# Task

**Title:** `WO-TEST-003: Seeder profile and --clear tests`

---

## Parent

**Work Order:** #458 (WO: Test Coverage Phase 3)
**Tracking Issue:** #473
**Related Issue:** #173

---

## Branch

| Branch | Target |
|--------|--------|
| `test/coverage-phase-3/003-seeder-tests` | `test/coverage-phase-3` |

```bash
git checkout test/coverage-phase-3
git pull origin test/coverage-phase-3
git checkout -b test/coverage-phase-3/003-seeder-tests
git push -u origin test/coverage-phase-3/003-seeder-tests
```

---

## Deliverable

This task will deliver:

- Tests for seed_showroom management command
- Tests for different seeder profiles
- Tests for --clear flag behavior
- Tests for idempotent seeding operations

---

## Boundaries

### Do

- Add tests for `seed_showroom` management command
- Test different profile options (minimal, full, etc.)
- Test `--clear` flag behavior
- Test idempotency (running multiple times)
- Test error handling for invalid profiles
- Achieve ≥80% coverage for seeder module

### Do NOT

- ❌ Do not modify seeder production code
- ❌ Do not add new seeder profiles
- ❌ Do not change seeding behavior
- ❌ Do not modify database models

---

## Acceptance Criteria

- [ ] Tests for seed_showroom command exist
- [ ] All available profiles are tested
- [ ] `--clear` flag behavior is tested
- [ ] Idempotency is verified (safe to run multiple times)
- [ ] Error handling for invalid profiles tested
- [ ] Coverage for seeder module ≥80%
- [ ] All tests pass locally and in CI
- [ ] No flaky tests

---

## Test Commands

```bash
make lint
make test

# Run specific tests
python -m pytest tests/management/test_seed_showroom.py -v

# Check coverage
python -m pytest tests/management/test_seed_showroom.py --cov=core/sum_core/management/commands --cov-report=term-missing
```

---

## Files Expected to Change

```
tests/
└── management/
    └── test_seed_showroom.py    # Modified/New
```

---

## Dependencies

**Depends On:**
- [ ] None — can run in parallel with WO-TEST-001 and WO-TEST-002

**Blocks:**
- WO-TEST-004: Coverage verification and reporting

---

## Risk

**Level:** Low

**Why:**
- Adding tests only, no production code changes
- Testing existing functionality

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
test(core): add seed_showroom profile and --clear tests

- Add tests for different seeder profiles
- Add tests for --clear flag behavior
- Verify seeding idempotency
- Add error handling tests

Closes #173
```

---

## Implementation Notes

### Test Structure

```python
import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from io import StringIO

class TestSeedShowroom:
    """Tests for seed_showroom management command."""

    @pytest.mark.django_db
    def test_minimal_profile(self):
        """Test seeding with minimal profile."""
        out = StringIO()
        call_command('seed_showroom', '--profile=minimal', stdout=out)
        # Assert expected content created

    @pytest.mark.django_db
    def test_full_profile(self):
        """Test seeding with full profile."""
        pass

    @pytest.mark.django_db
    def test_clear_flag_removes_existing(self):
        """Test that --clear removes existing content."""
        pass

    @pytest.mark.django_db
    def test_idempotent_seeding(self):
        """Test running seed multiple times is safe."""
        call_command('seed_showroom', '--profile=minimal')
        call_command('seed_showroom', '--profile=minimal')
        # Assert no duplicates

    def test_invalid_profile_error(self):
        """Test error handling for invalid profile."""
        with pytest.raises(CommandError):
            call_command('seed_showroom', '--profile=invalid')
```
