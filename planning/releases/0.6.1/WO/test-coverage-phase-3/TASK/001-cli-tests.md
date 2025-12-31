# Task

**Title:** `WO-TEST-001: CLI scaffold_project unit tests`

---

## Parent

**Work Order:** #458 (WO: Test Coverage Phase 3)
**Tracking Issue:** #471

---

## Branch

| Branch | Target |
|--------|--------|
| `test/coverage-phase-3/001-cli-tests` | `test/coverage-phase-3` |

```bash
git checkout test/coverage-phase-3
git pull origin test/coverage-phase-3
git checkout -b test/coverage-phase-3/001-cli-tests
git push -u origin test/coverage-phase-3/001-cli-tests
```

---

## Deliverable

This task will deliver:

- Unit tests for CLI scaffold_project functionality
- Test coverage for project creation logic
- Tests for template copying and file generation
- Error handling tests for edge cases

---

## Boundaries

### Do

- Add unit tests for `scaffold_project` function
- Test project directory creation
- Test template file copying
- Test configuration file generation
- Test error handling (existing project, permissions, etc.)
- Mock filesystem operations where appropriate
- Achieve ≥80% coverage for scaffold_project module

### Do NOT

- ❌ Do not modify CLI production code
- ❌ Do not add integration tests (unit tests only)
- ❌ Do not test external dependencies
- ❌ Do not change existing tests

---

## Acceptance Criteria

- [ ] Unit tests for `scaffold_project` function exist
- [ ] Tests cover successful project creation
- [ ] Tests cover error scenarios (directory exists, permissions)
- [ ] Tests cover template file copying
- [ ] Tests cover configuration generation
- [ ] Coverage for scaffold_project module ≥80%
- [ ] All tests pass locally and in CI
- [ ] No flaky tests

---

## Test Commands

```bash
make lint
make test

# Run specific tests
python -m pytest tests/cli/test_scaffold_project.py -v

# Check coverage
python -m pytest tests/cli/test_scaffold_project.py --cov=cli/sum_cli/scaffold --cov-report=term-missing
```

---

## Files Expected to Change

```
tests/
└── cli/
    └── test_scaffold_project.py    # New
```

---

## Dependencies

**Depends On:**
- [ ] None — this is the first task

**Blocks:**
- WO-TEST-004: Coverage verification and reporting

---

## Risk

**Level:** Low

**Why:**
- Adding tests only, no production code changes
- Well-defined scope

---

## Labels

- [ ] `type:task`
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
test(cli): add unit tests for scaffold_project functionality

- Add tests for project directory creation
- Add tests for template file copying
- Add tests for configuration generation
- Add tests for error handling scenarios
- Achieve ≥80% coverage for scaffold module

Closes #458
```

---

## Implementation Notes

### Test Structure

```python
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

class TestScaffoldProject:
    """Tests for scaffold_project functionality."""

    def test_creates_project_directory(self, tmp_path):
        """Test that project directory is created."""
        pass

    def test_copies_template_files(self, tmp_path):
        """Test that template files are copied correctly."""
        pass

    def test_generates_config_files(self, tmp_path):
        """Test that configuration files are generated."""
        pass

    def test_error_when_directory_exists(self, tmp_path):
        """Test error handling when project directory exists."""
        pass

    def test_error_on_permission_denied(self, tmp_path):
        """Test error handling on permission denied."""
        pass
```
