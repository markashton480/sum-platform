# Testing Guide

**Single Source of Truth for SUM Platform Testing**

This document is the canonical reference for all testing practices on the SUM Platform. For deep dives into theme testing, template isolation, and post-MVP architecture, see [test-strategy-post-mvp-v1.md](master-docs/test-strategy-post-mvp-v1.md).

---

## Quick Reference

### Running Tests Locally

**Prerequisites**: Tests require an activated virtual environment.

```bash
# ALWAYS activate .venv before running tests
source .venv/bin/activate

# Fast tier (default) - every push
make test

# Integration tier - seeders, webhooks, form flows
make test-integration

# Full tier - everything except E2E
make test-full

# E2E tier - Playwright browser tests
make test-e2e

# Quick gate - CLI + themes only
make test-fast
```

### Common Test Commands

```bash
# Run a specific test file
python -m pytest tests/path/to/test_file.py -v

# Run a specific test function
python -m pytest tests/path/to/test_file.py::test_function_name -v

# Run tests matching a pattern
python -m pytest -k "test_pattern" -v

# Run with coverage report
python -m pytest --cov=sum_core --cov-report=html

# Run in verbose mode with output
python -m pytest -vv -s
```

---

## Test Tiers

The SUM Platform uses a **tiered test strategy** to optimize CI/CD performance while maintaining comprehensive coverage.

### Fast Tier (Default)

**What**: Unit tests, quick integration checks, core business logic
**When**: Every commit, every push
**Duration**: < 5 minutes on CI
**Make Target**: `make test`

```bash
# Fast tests explicitly exclude slow/integration markers
python -m pytest  # Uses default config from pyproject.toml
```

**Characteristics**:
- No seeder execution
- Minimal database operations
- No webhook delivery tests
- No external service calls
- Template rendering with mocked data

**Configuration** (from `pyproject.toml`):
```toml
addopts = [
    "-m",
    "not slow and not integration",
]
```

### Integration Tier

**What**: Seeder tests, webhook delivery, form submission flows, email notifications
**When**: Feature branch PRs, release branches
**Duration**: 10-15 minutes on CI
**Make Target**: `make test-integration`

```bash
python -m pytest -m "slow or integration"
```

**Characteristics**:
- Full seeder execution (Sage & Stone, Showroom)
- Webhook delivery with retries
- Complete form-to-lead-to-notification flows
- Database-intensive operations

**Markers**:
```python
@pytest.mark.slow
@pytest.mark.integration
```

### Full Tier

**What**: All tests except E2E (Playwright)
**When**: Release PRs to develop/main, pre-release gates
**Duration**: 15-20 minutes on CI
**Make Target**: `make test-full`

```bash
python -m pytest -m "" --ignore=tests/e2e
```

**Characteristics**:
- Runs both fast and integration tiers
- Includes theme rendering tests
- Includes CLI integration tests
- Template loading verification
- Regression test suite

### E2E Tier

**What**: Playwright browser tests for critical user journeys
**When**: Nightly builds, manual triggers, pre-production gates
**Duration**: Variable (browser-dependent)
**Make Target**: `make test-e2e`

```bash
python -m pytest tests/e2e
```

**Characteristics**:
- Real browser automation
- Full stack integration (frontend + backend)
- Form submissions with JavaScript validation
- Navigation and routing tests

---

## Pytest Markers

SUM Platform uses pytest markers to categorize and filter tests.

### Available Markers

| Marker | Purpose | When to Use |
|--------|---------|-------------|
| `@pytest.mark.unit` | Pure unit tests | Testing isolated functions/classes |
| `@pytest.mark.integration` | Integration tests | Testing component interactions |
| `@pytest.mark.slow` | Slow-running tests (>5s) | Seeder tests, full workflow tests |
| `@pytest.mark.regression` | Regression tests | Preventing known bugs from reappearing |
| `@pytest.mark.requires_themes` | Needs theme system (0.6+) | Theme rendering, template override tests |
| `@pytest.mark.legacy_only` | Only for 0.5.x | Tests for frozen legacy version |
| `@pytest.mark.loopsite` | Loop site validation | Tests against deployed sites |
| `@pytest.mark.e2e` | End-to-end browser tests | Playwright tests |
| `@pytest.mark.django_db` | Requires database access | Any test hitting Django models |

### Adding Markers to Tests

```python
import pytest

@pytest.mark.slow
@pytest.mark.integration
def test_sage_stone_seeder_full_run():
    """Full seeder execution test."""
    # This test will only run with `make test-integration` or `make test-full`
    pass

@pytest.mark.requires_themes
def test_theme_a_hero_template():
    """Verify Theme A hero template rendering."""
    # Skipped on 0.5.x versions
    pass
```

---

## CI Behavior Per Branch Type

CI automatically selects the appropriate test tier based on branch patterns.

| Branch Pattern | Test Tier | Rationale |
|----------------|-----------|-----------|
| `task/*`, `fix/*` | **Fast** | Quick feedback loop for isolated changes |
| `feature/*` | **Fast + Integration** | Validate feature completeness including seeders |
| `release/*`, `infra/*` | **Full** | Comprehensive validation before merge |
| `develop` → `main` | **Full** (+ optional E2E) | Production-ready gate |

### CI Workflow Configuration

From `.github/workflows/ci.yml`:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Determine test tier
        id: tier
        run: |
          if [[ "${{ github.ref }}" == refs/heads/task/* ]] || [[ "${{ github.ref }}" == refs/heads/fix/* ]]; then
            echo "target=test" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == refs/heads/feature/* ]]; then
            echo "target=test test-integration" >> $GITHUB_OUTPUT
          else
            echo "target=test-full" >> $GITHUB_OUTPUT
          fi

      - name: Run tests
        run: make ${{ steps.tier.outputs.target }}
```

---

## Test Isolation Patterns

### Virtual Environment Requirement

**CRITICAL**: Tests will NOT run without an activated virtual environment.

```bash
# ALWAYS do this first
source .venv/bin/activate

# Then run tests
make test
```

**Why**: The test suite relies on dependencies installed in `.venv/`. Running tests outside the virtual environment will fail with import errors.

**For CI**: The CI workflow automatically creates and activates a virtual environment before running tests.

**For Agents**: Agents should use the existing `.venv/` - no installation needed, just activation.

### Theme Test Isolation

Theme tests use pytest's `tmp_path` fixture to ensure source theme files are never modified.

```python
@pytest.fixture
def isolated_theme_env(tmp_path: Path) -> dict[str, str]:
    """
    Provides an isolated test environment for theme operations.

    - Copies theme source to temp directory for WRITE operations
    - Points SUM_THEME_PATH to read-only source for READS
    - All test outputs go to tmp_path
    """
    work_dir = tmp_path / "work"
    work_dir.mkdir()

    return {
        "SUM_THEME_PATH": str(SOURCE_THEMES_PATH),
        "SUM_BOILERPLATE_PATH": str(SOURCE_BOILERPLATE_PATH),
        "SUM_CLIENT_OUTPUT_PATH": str(work_dir),
        "SUM_TEST_MODE": "1",
    }
```

### Safe Deletion Guards

**Rule**: Never use `shutil.rmtree()` directly in tests. Use safe deletion utilities.

```python
from tests.utils.safe_cleanup import safe_rmtree

# Safe deletion with multiple guardrails
safe_rmtree(path, repo_root, tmp_base)
```

**Protected Paths** (never deletable):
- `.git`
- `themes/`
- `boilerplate/`
- `core/`
- `cli/`
- `docs/`

See [test-strategy-post-mvp-v1.md § Safe Deletion Guards](master-docs/test-strategy-post-mvp-v1.md#23-safe-deletion-guards) for implementation details.

---

## Template Loading Order

### The Problem

Tests must verify that themes override core templates correctly. Template loading order:

1. **Theme templates** (highest priority): `theme/active/templates/`
2. **Client overrides**: `templates/overrides/`
3. **Core fallback**: `sum_core/templates/`

### Verification Tests

```python
# tests/templates/test_template_loading_order.py

def test_theme_template_takes_precedence_over_core():
    """Theme template should load before core template."""
    template = get_template("sum_core/blocks/stats.html")
    origin = template.origin.name

    assert "theme_a" in origin or "theme/active" in origin, (
        f"Expected theme template, got: {origin}"
    )
```

### Configuration

From `test_project/settings.py`:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            THEME_TEMPLATES_DIR,           # Theme templates (1st priority)
            BASE_DIR / "templates",        # Client overrides (2nd priority)
            # sum_core templates loaded via APP_DIRS
        ],
        "APP_DIRS": True,  # Loads sum_core/templates/ (3rd priority)
    },
]
```

---

## Seeder Tests

Seeder tests are marked as `@pytest.mark.slow` and `@pytest.mark.integration` because they:
- Execute full site creation workflows
- Populate databases with realistic content
- Test complete theme rendering
- Verify form configurations

### Example Seeder Test

```python
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.django_db
def test_sage_stone_seeder_creates_complete_site():
    """Sage & Stone seeder creates all expected pages and content."""
    call_command("seed_sage_stone")

    # Verify site structure
    home = HomePage.objects.first()
    assert home is not None

    # Verify blog exists
    blog_index = BlogIndexPage.objects.first()
    assert blog_index is not None

    # Verify forms configured
    contact_page = ContactPage.objects.first()
    assert contact_page is not None
```

**Run seeder tests**: `make test-integration`

---

## Writing New Tests

### Test File Organization

```
tests/
├── unit/              # Fast, isolated unit tests
├── integration/       # Integration tests (slow)
├── themes/            # Theme-specific tests (0.6+)
├── templates/         # Template loading tests
├── cli/               # CLI integration tests
└── e2e/               # Playwright E2E tests
```

### Test Naming Conventions

```python
# File: test_<module>.py
# Class: Test<Feature>
# Function: test_<specific_behavior>

# Example:
class TestHeroBlock:
    def test_hero_renders_with_image(self):
        pass

    def test_hero_validates_cta_limit(self):
        pass
```

### Fixture Usage

```python
import pytest
from django.test import Client

@pytest.fixture
def client():
    """Django test client."""
    return Client()

@pytest.fixture
def home_page(db):
    """Create a home page for testing."""
    from sum_core.pages.home import HomePage
    return HomePage.objects.create(title="Test Home", slug="home")

def test_home_page_renders(client, home_page):
    response = client.get(home_page.url)
    assert response.status_code == 200
```

### Adding Markers

```python
import pytest

@pytest.mark.django_db  # Required for database access
@pytest.mark.slow       # Runs only in integration tier
def test_expensive_database_operation():
    # ... test logic ...
    pass
```

---

## Coverage Reports

### Generating Coverage

```bash
# Run tests with coverage
python -m pytest --cov=sum_core --cov-report=html

# Open HTML report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage Configuration

From `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["."]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/migrations/*",
    "boilerplate/*",
    "clients/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == \"__main__\":",
]
```

**Target**: ≥ 80% coverage for new code

---

## Debugging Tests

### Running Specific Tests

```bash
# Single file
python -m pytest tests/unit/test_blocks.py -v

# Single test class
python -m pytest tests/unit/test_blocks.py::TestHeroBlock -v

# Single test function
python -m pytest tests/unit/test_blocks.py::TestHeroBlock::test_hero_renders -v

# Tests matching a pattern
python -m pytest -k "hero" -v
```

### Verbose Output

```bash
# Extra verbose with stdout
python -m pytest -vv -s

# Show local variables on failure
python -m pytest -l

# Drop into debugger on failure
python -m pytest --pdb
```

### Common Issues

**Issue**: `ImportError: No module named 'sum_core'`
**Solution**: Activate virtual environment: `source .venv/bin/activate`

**Issue**: `django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS`
**Solution**: Ensure `DJANGO_SETTINGS_MODULE` is set (automatic in pytest config)

**Issue**: Tests pass individually but fail in full suite
**Solution**: Check for test isolation issues, especially theme/template settings leakage

**Issue**: `PermissionError` when tests try to delete files
**Solution**: Use `tmp_path` fixture and safe deletion utilities

---

## Theme-Specific Testing

### Theme Requirements

All themes must pass:
- **Metadata validation** (`theme.json` schema)
- **Template contract tests** (required blocks implemented)
- **Accessibility gates** (WCAG 2.1 AA baseline)
- **Performance gates** (Lighthouse ≥ 90)

### Theme Test Structure

```python
# tests/themes/test_theme_a_rendering.py

@pytest.mark.requires_themes
@pytest.mark.django_db
def test_theme_a_home_page_uses_base_template(client, home_page):
    """Homepage must use Theme A's base.html."""
    response = client.get(home_page.url)

    assert response.status_code == 200
    # Verify theme template was used
    assert any("theme_a" in t.origin.name for t in response.templates)
```

### Theme Guardrails

**Regression Prevention**: After the "Theme Delete Drama" incident, we enforce:

```python
# tests/themes/test_theme_a_guardrails.py

def test_theme_a_source_assets_exist():
    """theme_a directory and manifest must always exist."""
    theme_a = REPO_ROOT / "themes" / "theme_a"
    assert theme_a.exists(), "CRITICAL: themes/theme_a is missing!"
    assert (theme_a / "theme.json").exists(), "CRITICAL: theme.json missing!"
```

This test runs on **every CI build** to catch accidental deletions.

---

## CLI Testing

CLI tests use isolated environments to prevent corrupting source files.

### CLI Test Isolation

```python
def test_init_creates_project_in_output_path_only(tmp_path, isolated_theme_env):
    """sum init must only write to SUM_CLIENT_OUTPUT_PATH."""
    env = {**os.environ, **isolated_theme_env}

    result = subprocess.run(
        ["sum", "init", "test-client", "--theme", "a"],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
    )

    assert result.returncode == 0
    # Verify source themes untouched
    assert (REPO_ROOT / "themes" / "theme_a").exists()
```

---

## Regression Testing

### Known Issue Prevention

After fixing a bug, add a regression test:

```python
@pytest.mark.regression
def test_form_submission_preserves_utm_params():
    """
    Regression test for #123: UTM parameters must be captured.

    Bug: Form submissions were losing UTM parameters.
    Fix: Updated LeadAttributionMiddleware to preserve query params.
    """
    # Test that verifies the fix
    pass
```

### Regression Test Markers

```python
@pytest.mark.regression  # Indicates this prevents a known bug
```

---

## Multi-Version Testing

### Version-Specific Markers

```python
@pytest.mark.requires_themes  # Only runs on 0.6.x+
@pytest.mark.legacy_only      # Only runs on 0.5.x
```

### Version Detection

From `tests/conftest.py`:

```python
def pytest_collection_modifyitems(config, items):
    """Skip tests based on current version."""
    current_version = tuple(int(x) for x in __version__.split(".")[:2])

    for item in items:
        if "requires_themes" in item.keywords:
            if current_version < (0, 6):
                item.add_marker(pytest.mark.skip(
                    reason=f"Requires 0.6.x+, current: {__version__}"
                ))
```

---

## Performance & Accessibility Gates

### Performance Targets

| Metric | Target | Enforcement |
|--------|--------|-------------|
| Lighthouse Performance | ≥ 90 | CI gate |
| Lighthouse Accessibility | ≥ 90 | CI gate |
| Lighthouse SEO | ≥ 90 | CI gate |
| CSS Bundle Size (gzip) | ≤ 100kb | Build artifact check |

### Accessibility Tests

```python
@pytest.mark.requires_themes
def test_base_template_has_skip_link():
    """Base template must have skip-to-main-content link."""
    base_html = THEME_A_DIR / "templates" / "theme" / "base.html"
    content = base_html.read_text()

    assert "skip" in content.lower()
    assert 'href="#main' in content or 'href="#content' in content
```

---

## Further Reading

### Deep Dive Documentation

- **[Test Strategy Post-MVP v1.0](master-docs/test-strategy-post-mvp-v1.md)**: Comprehensive test architecture, theme testing, multi-version strategy
- **[Wiring Inventory](WIRING-INVENTORY.md)**: Theme wiring, template loading configuration
- **[Hygiene Standards](hygiene.md)**: Code quality and testing best practices

### CI/CD

- `.github/workflows/ci.yml`: Complete CI workflow configuration
- **[Release Runbook](../ops-pack/RELEASE_RUNBOOK.md)**: Pre-release testing requirements

---

## Cheat Sheet

```bash
# Prerequisites
source .venv/bin/activate

# Common Commands
make test                    # Fast tests (default)
make test-integration        # Integration tests
make test-full               # All tests except E2E
make test-e2e                # Playwright E2E tests
make test-fast               # Quick gate (CLI + themes)

# Specific Test Selection
python -m pytest tests/unit/test_blocks.py -v
python -m pytest -k "hero" -v
python -m pytest -m "slow or integration"

# Coverage
python -m pytest --cov=sum_core --cov-report=html

# Debugging
python -m pytest -vv -s      # Verbose with stdout
python -m pytest --pdb       # Drop to debugger on failure
python -m pytest -l          # Show local vars on failure

# Markers
@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.requires_themes
@pytest.mark.regression
@pytest.mark.django_db
```

---

**Last Updated**: 2026-01-03
**Maintained By**: SUM Platform Team
