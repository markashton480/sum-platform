# TEST-013 Follow-up: Phase 3 Test Infrastructure

**Branch**: `test/TEST-013-test-infra`  
**Commits**:

1. `docs(TEST-013): add task ticket`
2. `test(TEST-013): add shared fixtures utilities`
3. `test(TEST-013): make template fallback test hermetic`

---

## What Was Implemented

### 1. Shared Test Utilities (`tests/utils/fixtures.py`)

New module providing single source of truth for:

- `REPO_ROOT` — resolved repository root Path
- `get_protected_paths()` — canonical protected directory names
- `get_protected_absolute_paths()` — absolute paths to protected dirs
- `assert_protected_paths_unchanged()` — optional assertion helper

### 2. Module Re-exports (`tests/utils/__init__.py`)

Updated to expose all key symbols:

```python
from tests.utils import REPO_ROOT, get_protected_paths, safe_rmtree
```

### 3. Root Conftest Fixtures (`tests/conftest.py`)

Added session-scoped fixtures:

- `repo_root` — returns `REPO_ROOT` Path
- `protected_paths` — returns tuple of protected directory names

### 4. Hermetic Template Fallback Test

Refactored `test_core_only_template_resolves_from_core` to:

- Create empty tmp_path theme directory
- Prepend to template search path
- Verify core fallback works regardless of theme_a contents
- No longer fragile to theme_a adding new templates

---

## Verification Results

```
$ make lint
ruff check . --config pyproject.toml
All checks passed!
mypy core cli tests
Success: no issues found in 250 source files
black --check core cli tests
All done! ✨ 🍰 ✨
231 files would be left unchanged.
isort --check-only core cli tests
Skipped 44 files

$ make test
752 passed, 45 warnings in 177.90s (0:02:57)

$ make test-cli
16 passed, 7 warnings in 4.44s

$ make test-themes
69 passed, 7 warnings in 52.71s

$ make test-templates
4 passed, 7 warnings in 45.48s

$ git status --porcelain
(clean)
```

---

## Fixture Layout Summary

```
tests/
├── conftest.py          # Root fixtures: repo_root, protected_paths, safe_rmtree, etc.
└── utils/
    ├── __init__.py      # Re-exports from fixtures.py and safe_cleanup.py
    ├── fixtures.py      # REPO_ROOT, get_protected_paths(), assert helpers
    └── safe_cleanup.py  # PROTECTED_PATHS, safe_rmtree(), FilesystemSandbox
```

**Usage**:

```python
# In any test file
from tests.utils import REPO_ROOT, get_protected_paths, safe_rmtree

# Or via fixtures
def test_something(repo_root, protected_paths):
    assert repo_root.exists()
    assert "themes" in protected_paths
```

---

## PR Link

https://github.com/markashton480/sum_platform/pull/new/test/TEST-013-test-infra
