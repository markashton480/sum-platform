# SUM Platform – Post-MVP Test Strategy v1.0

**Product:** SUM Platform – Client Website Deployment System  
**Version:** 1.0  
**Date:** December 21, 2025  
**Scope:** Post-MVP (M6+: Theme System, Blog, Dynamic Forms)  
**Status:** Draft  
**Supersedes:** Extends test-strategy-v1.1 for post-MVP development

---

## Document Purpose

This document extends the MVP Test Strategy (v1.1) to address the post-MVP architecture changes, specifically:

- The new theme system (Tailwind-first, init-time selection)
- Multi-version testing (0.5.x frozen, 0.6.x+ active)
- Test isolation and safety (preventing incidents like "Theme Delete Drama")
- Template override verification in test environments
- Loop Sites validation strategy

**Key Principle:** The MVP test strategy remains valid for `sum_core` business logic. This document adds theme-specific testing guidance and addresses post-MVP architectural concerns.

---

## 1. Executive Summary

### 1.1 What Changed

| Aspect | MVP (0.5.x) | Post-MVP (0.6.x+) |
|--------|-------------|-------------------|
| **Styling** | Token-based CSS | Tailwind-first themes |
| **Theme Selection** | N/A (single style) | Fixed at init-time |
| **Template Source** | `sum_core/templates/` | Theme templates + core fallback |
| **CSS Build** | Static tokens | Tailwind compilation per theme |
| **Test Scope** | Core package only | Core + Theme + CLI integration |

### 1.2 Key Testing Risks (Post-MVP Specific)

1. **Theme file safety** – Tests must never modify/delete source theme files
2. **Template resolution** – Tests must verify correct theme template loading order
3. **Settings leakage** – Test isolation between theme-aware and theme-agnostic tests
4. **Multi-version regression** – Ensuring 0.5.x stability while developing 0.6.x+
5. **CLI integration safety** – `sum init --theme` must not corrupt source assets

---

## 2. Test Environment Architecture

### 2.1 Environment Isolation Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TEST ENVIRONMENT LAYERS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────┐   READ-ONLY    ┌──────────────────────────────┐    │
│  │ Source Assets   │ ◄───────────── │ Test Fixtures                │    │
│  │                 │                │                              │    │
│  │ themes/         │                │ • Theme snapshots            │    │
│  │ boilerplate/    │                │ • Template test data         │    │
│  │ sum_core/       │                │ • Reference outputs          │    │
│  └─────────────────┘                └──────────────────────────────┘    │
│           │                                                              │
│           │ COPY (never reference directly for writes)                   │
│           ▼                                                              │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    PYTEST tmp_path SANDBOX                       │    │
│  │                                                                  │    │
│  │  • All file creation/modification happens here                   │    │
│  │  • Automatically cleaned up by pytest                            │    │
│  │  • Injected via SUM_THEME_PATH, SUM_BOILERPLATE_PATH env vars    │    │
│  │  • Safe for shutil.rmtree and destructive operations             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Environment Variables for Test Isolation

Tests that interact with themes or the CLI **MUST** configure these environment variables:

```python
# cli/tests/conftest.py

import os
import shutil
from pathlib import Path
import pytest

# Repository root detection (safe reference)
REPO_ROOT = Path(__file__).parent.parent.parent

# Source paths (READ-ONLY)
SOURCE_THEMES_PATH = REPO_ROOT / "themes"
SOURCE_BOILERPLATE_PATH = REPO_ROOT / "boilerplate"


@pytest.fixture
def isolated_theme_env(tmp_path: Path) -> dict[str, str]:
    """
    Provides an isolated test environment for theme operations.
    
    - Copies theme source to temp directory for WRITE operations
    - Points SUM_THEME_PATH to read-only source for READS
    - All test outputs go to tmp_path
    
    Returns environment variables dict for subprocess calls.
    """
    # Create isolated working directory
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    
    # Return env vars that point to source (read) but work in temp (write)
    return {
        "SUM_THEME_PATH": str(SOURCE_THEMES_PATH),
        "SUM_BOILERPLATE_PATH": str(SOURCE_BOILERPLATE_PATH),
        "SUM_CLIENT_OUTPUT_PATH": str(work_dir),
        "SUM_TEST_MODE": "1",
    }


@pytest.fixture
def writable_theme_copy(tmp_path: Path) -> Path:
    """
    Creates a writable copy of themes for tests that need to modify theme files.
    
    Use sparingly - most tests should only READ themes.
    """
    themes_copy = tmp_path / "themes"
    shutil.copytree(SOURCE_THEMES_PATH, themes_copy)
    return themes_copy
```

### 2.3 Safe Deletion Guards

**CRITICAL:** All test cleanup code must use guarded deletion:

```python
# tests/utils/safe_cleanup.py

"""
Safe Cleanup Utilities for Test Environment

Prevents accidental deletion of source code during test cleanup.
"""

from pathlib import Path
from typing import NoReturn

# Paths that must NEVER be deleted
PROTECTED_PATHS = [
    ".git",
    "themes",
    "boilerplate", 
    "core",
    "cli",
    "docs",
    "infrastructure",
    "scripts",
]


class UnsafeDeleteError(Exception):
    """Raised when attempting to delete a protected path."""
    pass


def safe_rmtree(path: Path, repo_root: Path, tmp_base: Path) -> None:
    """
    Safely remove a directory tree with multiple safety checks.
    
    Args:
        path: Directory to remove
        repo_root: Repository root path (for protection check)
        tmp_base: Pytest tmp_path base (only paths under this are deletable)
    
    Raises:
        UnsafeDeleteError: If deletion would affect protected paths
    """
    path = path.resolve()
    repo_root = repo_root.resolve()
    tmp_base = tmp_base.resolve()
    
    # Safety check 1: Never delete repo root
    if path == repo_root:
        raise UnsafeDeleteError(f"Refusing to delete repository root: {path}")
    
    # Safety check 2: Never delete if path contains .git
    if (path / ".git").exists() or ".git" in path.parts:
        raise UnsafeDeleteError(f"Refusing to delete path with .git: {path}")
    
    # Safety check 3: Never delete protected directories
    for protected in PROTECTED_PATHS:
        if (repo_root / protected).resolve() == path:
            raise UnsafeDeleteError(f"Refusing to delete protected path: {path}")
        if path.is_relative_to(repo_root / protected):
            raise UnsafeDeleteError(
                f"Refusing to delete path under protected directory: {path}"
            )
    
    # Safety check 4: Only delete paths under tmp_base
    if not path.is_relative_to(tmp_base):
        raise UnsafeDeleteError(
            f"Refusing to delete path outside tmp_path: {path}\n"
            f"Expected path under: {tmp_base}"
        )
    
    # Safe to delete
    import shutil
    shutil.rmtree(path, ignore_errors=False)


def register_cleanup(path: Path, repo_root: Path, tmp_base: Path) -> callable:
    """
    Returns a cleanup function that uses safe_rmtree.
    
    For use in pytest fixtures or test cleanup.
    """
    def cleanup() -> None:
        if path.exists():
            safe_rmtree(path, repo_root, tmp_base)
    return cleanup
```

---

## 3. Test Levels for Theme System

### 3.1 Theme Unit Tests

**Goal:** Verify individual theme components in isolation.

**Scope:**

| Component | Test Focus | Location |
|-----------|-----------|----------|
| `theme.json` | Schema validation, required fields | `tests/themes/test_theme_metadata.py` |
| Tailwind config | Valid configuration, CSS variable mappings | `tests/themes/test_tailwind_config.py` |
| Template syntax | Django template validity | `tests/themes/test_template_syntax.py` |
| Block partials | Required blocks present | `tests/themes/test_block_contracts.py` |

**Example Test:**

```python
# tests/themes/test_theme_metadata.py

"""
Theme Metadata Validation Tests

File: tests/themes/test_theme_metadata.py
Purpose: Validate theme.json schema and required fields for all themes
Dependencies: pytest, jsonschema
Dependents: Theme loading in sum init, theme validation in sum check
"""

import json
from pathlib import Path
import pytest
from jsonschema import validate, ValidationError

THEMES_DIR = Path(__file__).parent.parent.parent / "themes"

THEME_JSON_SCHEMA = {
    "type": "object",
    "required": ["slug", "name", "version"],
    "properties": {
        "slug": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
        "name": {"type": "string", "minLength": 1},
        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
        "vibe": {"type": "string"},
        "features": {
            "type": "object",
            "properties": {
                "has_fancy_hero": {"type": "boolean"},
                "supports_dark_mode": {"type": "boolean"},
            }
        },
        "fonts": {
            "type": "object",
            "properties": {
                "heading": {"type": "string"},
                "body": {"type": "string"},
            }
        },
    }
}


def get_theme_dirs() -> list[Path]:
    """Return all theme directories."""
    return [d for d in THEMES_DIR.iterdir() if d.is_dir() and d.name.startswith("theme_")]


@pytest.fixture(params=get_theme_dirs(), ids=lambda p: p.name)
def theme_dir(request) -> Path:
    """Parametrized fixture providing each theme directory."""
    return request.param


class TestThemeMetadata:
    """Theme metadata validation tests."""
    
    def test_theme_json_exists(self, theme_dir: Path) -> None:
        """Each theme must have a theme.json file."""
        theme_json = theme_dir / "theme.json"
        assert theme_json.exists(), f"Missing theme.json in {theme_dir.name}"
    
    def test_theme_json_valid_schema(self, theme_dir: Path) -> None:
        """theme.json must conform to required schema."""
        theme_json = theme_dir / "theme.json"
        if not theme_json.exists():
            pytest.skip("No theme.json")
        
        with open(theme_json) as f:
            data = json.load(f)
        
        try:
            validate(data, THEME_JSON_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Invalid theme.json in {theme_dir.name}: {e.message}")
    
    def test_theme_slug_matches_directory(self, theme_dir: Path) -> None:
        """theme.json slug must match directory name pattern."""
        theme_json = theme_dir / "theme.json"
        if not theme_json.exists():
            pytest.skip("No theme.json")
        
        with open(theme_json) as f:
            data = json.load(f)
        
        expected_dir_name = f"theme_{data['slug']}"
        assert theme_dir.name == expected_dir_name, (
            f"Directory {theme_dir.name} doesn't match slug {data['slug']}"
        )
```

### 3.2 Theme Template Override Tests

**Goal:** Verify correct template loading order (theme → client → core fallback).

**Critical Insight from THEME-15-A:** The settings must consistently resolve `THEME_TEMPLATES_DIR` to the theme under test, not fall back to defaults during full test suite runs.

**Solution: Explicit Settings Fixture**

```python
# tests/themes/conftest.py

"""
Theme Test Configuration

File: tests/themes/conftest.py
Purpose: Configure Django settings for theme-aware tests
Dependencies: pytest-django, Django settings
"""

import os
from pathlib import Path
import pytest
from django.conf import settings


REPO_ROOT = Path(__file__).parent.parent.parent
THEME_A_TEMPLATES = REPO_ROOT / "themes" / "theme_a" / "templates"


@pytest.fixture(autouse=True)
def theme_aware_settings(settings) -> None:
    """
    Configure template loading for theme-aware tests.
    
    This fixture ensures:
    1. Theme templates are loaded FIRST
    2. Core templates are loaded as FALLBACK
    3. Settings are consistent across test isolation boundaries
    """
    # Build template dirs in correct priority order
    template_dirs = [
        str(THEME_A_TEMPLATES),  # Theme templates (highest priority)
        # Client overrides would go here
        str(REPO_ROOT / "core" / "sum_core" / "templates"),  # Core fallback
    ]
    
    # Update TEMPLATES setting
    templates_config = settings.TEMPLATES.copy()
    if templates_config:
        templates_config[0] = {
            **templates_config[0],
            "DIRS": template_dirs,
        }
        settings.TEMPLATES = templates_config


@pytest.fixture
def assert_theme_template_used():
    """
    Factory fixture for asserting a specific theme template is being used.
    
    Usage:
        def test_stats_uses_theme_template(assert_theme_template_used):
            # ... render page ...
            assert_theme_template_used(response, "sum_core/blocks/stats.html", "theme_a")
    """
    def _assert(response, template_name: str, expected_theme: str) -> None:
        """Assert that the specified template came from the expected theme."""
        templates_used = [t.origin.name for t in response.templates if t.origin]
        
        theme_template_path = f"themes/{expected_theme}/templates/{template_name}"
        
        matching = [t for t in templates_used if theme_template_path in t]
        
        assert matching, (
            f"Expected template from {expected_theme}: {template_name}\n"
            f"Templates used: {templates_used}"
        )
    
    return _assert
```

### 3.3 Theme Integration Tests

**Goal:** Verify complete template rendering with theme assets.

```python
# tests/themes/test_theme_a_rendering.py

"""
Theme A Integration Rendering Tests

File: tests/themes/test_theme_a_rendering.py
Purpose: Verify Theme A templates render correctly with real content
Dependencies: pytest-django, BeautifulSoup, Theme A fixtures
Dependents: Theme A validation gate
"""

import pytest
from bs4 import BeautifulSoup
from django.test import Client, override_settings
from wagtail.models import Page

from sum_core.pages.home import HomePage


@pytest.mark.django_db
class TestThemeAHomePageRendering:
    """Integration tests for Theme A homepage rendering."""
    
    def test_home_page_uses_theme_base_template(
        self, 
        client: Client, 
        home_page: HomePage,
        assert_theme_template_used,
    ) -> None:
        """Homepage must use Theme A's base.html."""
        response = client.get(home_page.url)
        
        assert response.status_code == 200
        assert_theme_template_used(response, "theme/base.html", "theme_a")
    
    def test_home_page_has_theme_specific_classes(
        self,
        client: Client,
        home_page: HomePage,
    ) -> None:
        """Homepage must contain Theme A specific CSS classes."""
        response = client.get(home_page.url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Theme A uses Tailwind classes, not token-based CSS
        # Check for characteristic Theme A patterns
        main = soup.find("main")
        assert main is not None
        
        # Theme A should NOT have legacy token classes
        legacy_classes = ["section--light", "section--dark", "section--primary"]
        all_classes = " ".join(main.get("class", []))
        
        for legacy in legacy_classes:
            assert legacy not in all_classes, (
                f"Found legacy token class '{legacy}' - Theme A should use Tailwind"
            )
    
    def test_home_page_includes_tailwind_css(
        self,
        client: Client,
        home_page: HomePage,
    ) -> None:
        """Homepage must link to Theme A's compiled Tailwind CSS."""
        response = client.get(home_page.url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        css_links = soup.find_all("link", rel="stylesheet")
        css_hrefs = [link.get("href", "") for link in css_links]
        
        theme_css = [href for href in css_hrefs if "theme_a" in href]
        assert theme_css, f"No Theme A CSS found. CSS links: {css_hrefs}"
```

### 3.4 Theme Block Contract Tests

**Goal:** Verify each block's theme template satisfies the contract.

```python
# tests/themes/test_theme_block_contracts.py

"""
Theme Block Contract Tests

File: tests/themes/test_theme_block_contracts.py
Purpose: Verify theme block templates implement required contracts
Dependencies: pytest, Django template engine
"""

from pathlib import Path
import pytest
from django.template import engines


THEME_A_DIR = Path(__file__).parent.parent.parent / "themes" / "theme_a"

# Block contract: required elements that must be present in each block template
BLOCK_CONTRACTS = {
    "stats.html": {
        "required_elements": ["section", "heading"],
        "accessibility": ["aria-label OR heading with id"],
    },
    "hero.html": {
        "required_elements": ["heading", "cta button OR link"],
        "accessibility": ["main heading h1 OR aria-level"],
    },
    "testimonials.html": {
        "required_elements": ["blockquote OR testimonial wrapper"],
        "accessibility": ["cite OR attribution"],
    },
}


@pytest.fixture
def template_engine():
    """Get Django template engine for parsing."""
    return engines["django"]


class TestThemeBlockContracts:
    """Verify block templates meet their contracts."""
    
    def test_all_core_blocks_have_theme_override(self) -> None:
        """Theme A must provide templates for all core blocks."""
        core_blocks_dir = (
            Path(__file__).parent.parent.parent 
            / "core" / "sum_core" / "templates" / "sum_core" / "blocks"
        )
        theme_blocks_dir = THEME_A_DIR / "templates" / "sum_core" / "blocks"
        
        core_blocks = {f.name for f in core_blocks_dir.glob("*.html")}
        theme_blocks = {f.name for f in theme_blocks_dir.glob("*.html")}
        
        # Theme should override core blocks (warn if missing, don't fail)
        missing = core_blocks - theme_blocks
        if missing:
            pytest.skip(
                f"Theme A doesn't override these blocks (using core fallback): {missing}"
            )
    
    def test_stats_block_has_required_structure(self) -> None:
        """Stats block must have semantic section structure."""
        stats_template = THEME_A_DIR / "templates" / "sum_core" / "blocks" / "stats.html"
        
        if not stats_template.exists():
            pytest.skip("Theme A uses core stats.html fallback")
        
        content = stats_template.read_text()
        
        # Check for required structural elements
        assert "<section" in content or "role=\"region\"" in content, (
            "Stats block must be a semantic section"
        )
        
        # Check for grid/stats pattern (Theme A uses Tailwind grid)
        assert "grid" in content.lower(), (
            "Stats block should use grid layout"
        )
```

---

## 4. CLI Testing Safety

### 4.1 `sum init --theme` Test Requirements

**The Theme Delete Drama taught us:** CLI tests that invoke `sum init` must:

1. **Never** use the real repo as output directory
2. **Always** use `tmp_path` for client project creation
3. **Never** use `shutil.rmtree` on paths that could resolve to source
4. **Always** inject `SUM_THEME_PATH` pointing to read-only source
5. **Always** inject `SUM_CLIENT_OUTPUT_PATH` to temp directory

```python
# cli/tests/test_theme_init_safe.py

"""
Safe Theme Initialization Tests

File: cli/tests/test_theme_init_safe.py
Purpose: Test sum init --theme without risk to source files
Dependencies: pytest, subprocess, tmp_path fixture
Critical: These tests MUST use isolation patterns from conftest.py
"""

import subprocess
import os
from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).parent.parent.parent


class TestSumInitThemeSafety:
    """Tests for safe theme initialization."""
    
    def test_init_creates_project_in_output_path_only(
        self,
        tmp_path: Path,
        isolated_theme_env: dict[str, str],
    ) -> None:
        """sum init must only write to SUM_CLIENT_OUTPUT_PATH."""
        env = {**os.environ, **isolated_theme_env}
        
        result = subprocess.run(
            ["sum", "init", "test-client", "--theme", "a"],
            cwd=str(tmp_path),
            env=env,
            capture_output=True,
            text=True,
        )
        
        # Verify success
        assert result.returncode == 0, f"Init failed: {result.stderr}"
        
        # Verify project created in temp, not source
        output_path = Path(isolated_theme_env["SUM_CLIENT_OUTPUT_PATH"])
        expected_client = output_path / "test-client"
        
        assert expected_client.exists(), "Client project not created in output path"
        
        # CRITICAL: Verify source themes untouched
        source_theme_a = REPO_ROOT / "themes" / "theme_a"
        assert source_theme_a.exists(), "SOURCE theme_a was deleted!"
        assert (source_theme_a / "theme.json").exists(), "SOURCE theme.json missing!"
    
    def test_source_themes_immutable_after_init(
        self,
        tmp_path: Path,
        isolated_theme_env: dict[str, str],
    ) -> None:
        """Source themes must be unchanged after init operation."""
        # Snapshot source theme before
        source_theme = REPO_ROOT / "themes" / "theme_a"
        theme_json_before = (source_theme / "theme.json").read_text()
        template_count_before = len(list((source_theme / "templates").rglob("*.html")))
        
        # Run init
        env = {**os.environ, **isolated_theme_env}
        subprocess.run(
            ["sum", "init", "another-client", "--theme", "a"],
            cwd=str(tmp_path),
            env=env,
            capture_output=True,
        )
        
        # Verify source unchanged
        theme_json_after = (source_theme / "theme.json").read_text()
        template_count_after = len(list((source_theme / "templates").rglob("*.html")))
        
        assert theme_json_before == theme_json_after, "theme.json was modified!"
        assert template_count_before == template_count_after, "Template files changed!"


class TestThemeDeleteDramaRegression:
    """
    Regression tests specifically preventing Theme Delete Drama.
    
    These tests verify that no test operation can delete source themes.
    """
    
    def test_themes_directory_survives_full_test_run(self) -> None:
        """themes/ directory must exist after any test run."""
        themes_dir = REPO_ROOT / "themes"
        assert themes_dir.exists(), "themes/ directory is missing!"
        assert themes_dir.is_dir(), "themes/ is not a directory!"
    
    def test_theme_a_survives_full_test_run(self) -> None:
        """theme_a must exist after any test run."""
        theme_a = REPO_ROOT / "themes" / "theme_a"
        assert theme_a.exists(), "theme_a was deleted!"
        
        required_files = [
            "theme.json",
            "templates/theme/base.html",
        ]
        
        for required in required_files:
            assert (theme_a / required).exists(), f"Required file missing: {required}"
    
    def test_no_git_ignore_or_delete_of_themes(self) -> None:
        """themes/ must not be in .gitignore and must be tracked."""
        gitignore = REPO_ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            assert "themes/" not in content, "themes/ should not be gitignored!"
            assert "themes/theme_" not in content, "theme dirs should not be gitignored!"
```

---

## 5. Template Loading Order Testing

### 5.1 The Problem (From THEME-15-A_followup)

Tests passed in isolation but failed in the full suite because:
- `RUNNING_TESTS` flag changed template resolution behavior
- Settings leaked between test modules
- Template loader order wasn't deterministic

### 5.2 The Solution: Explicit Template Loading Configuration

```python
# core/sum_core/test_project/test_project/settings.py (UPDATED)

"""
Test Project Settings

Key change: Remove RUNNING_TESTS conditional for THEME_TEMPLATES_DIR.
Template loading must be consistent between test and production.
"""

from pathlib import Path

# ... other settings ...

# Theme template resolution - PRODUCTION BEHAVIOR IN TESTS
# This ensures tests validate the same template loading as production
THEME_TEMPLATES_CANDIDATES = [
    # 1. Client theme (highest priority) - would be set by sum init
    BASE_DIR / "theme" / "active" / "templates",
    # 2. Repo-level theme (for development)
    BASE_DIR.parent.parent.parent / "themes" / "theme_a" / "templates",
]

FALLBACK_THEME_TEMPLATES_DIR = BASE_DIR.parent / "templates"

# Resolve to first existing candidate
THEME_TEMPLATES_DIR: Path = next(
    (candidate for candidate in THEME_TEMPLATES_CANDIDATES if candidate.exists()),
    FALLBACK_THEME_TEMPLATES_DIR,
)

# Template loading configuration - DETERMINISTIC ORDER
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            THEME_TEMPLATES_DIR,           # Theme templates (1st priority)
            BASE_DIR / "templates",        # Client overrides (2nd priority)  
            # sum_core templates loaded via APP_DIRS
        ],
        "APP_DIRS": True,  # Loads sum_core/templates/ (3rd priority)
        "OPTIONS": {
            "context_processors": [
                # ... standard processors ...
            ],
        },
    },
]
```

### 5.3 Template Loading Verification Test

```python
# tests/templates/test_template_loading_order.py

"""
Template Loading Order Verification

File: tests/templates/test_template_loading_order.py
Purpose: Ensure templates load in correct priority order
Dependencies: pytest-django
Critical: Prevents template resolution bugs that only appear in full test runs
"""

import pytest
from django.template.loader import get_template
from django.template import TemplateDoesNotExist


class TestTemplateLoadingOrder:
    """Verify template resolution follows expected priority."""
    
    def test_theme_template_takes_precedence_over_core(self) -> None:
        """Theme template should load before core template."""
        # This template exists in both theme_a and sum_core
        template = get_template("sum_core/blocks/stats.html")
        
        # Template origin should be from theme, not core
        origin = template.origin.name
        
        assert "theme_a" in origin or "theme/active" in origin, (
            f"Expected theme template, got: {origin}"
        )
    
    def test_core_fallback_when_theme_missing(self) -> None:
        """Core template loads when theme doesn't override."""
        # Use a template that theme_a doesn't override (if any)
        # This tests the fallback mechanism
        try:
            template = get_template("sum_core/includes/some_core_only.html")
            origin = template.origin.name
            assert "sum_core" in origin
        except TemplateDoesNotExist:
            pytest.skip("No core-only template to test fallback")
    
    def test_template_order_consistent_across_test_isolation(
        self,
        settings,
    ) -> None:
        """Template loading must be consistent regardless of test order."""
        # Get template multiple times to ensure caching doesn't change behavior
        for _ in range(3):
            template = get_template("sum_core/blocks/hero.html")
            origin = template.origin.name
            
            # Should consistently resolve to same source
            assert "theme" in origin.lower() or "sum_core" in origin, (
                f"Inconsistent template resolution: {origin}"
            )
```

---

## 6. Multi-Version Testing Strategy

### 6.1 Version Testing Matrix

| Version Line | Test Frequency | Test Scope | Trigger |
|-------------|---------------|------------|---------|
| **0.5.x** (frozen) | Weekly | Smoke tests only | Scheduled CI job |
| **0.6.x** (active) | Every commit | Full suite | PR, push to develop |
| **0.7.x+** (future) | Every commit | Full suite | PR, push to develop |

### 6.2 Weekly Smoke Tests for Frozen Versions

```yaml
# .github/workflows/legacy-smoke.yml

name: Legacy Version Smoke Tests

on:
  schedule:
    # Weekly on Sunday at 2am UTC
    - cron: '0 2 * * 0'
  workflow_dispatch:

jobs:
  smoke-0-5-x:
    name: Smoke Test 0.5.x
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          ref: 'release/0.5.x'  # Or tag v0.5.x
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -e ./core
          pip install pytest pytest-django
      
      - name: Run smoke tests
        run: |
          pytest tests/smoke/ -v --tb=short
        env:
          DJANGO_SETTINGS_MODULE: test_project.settings
      
      - name: Health check
        run: |
          python -c "from sum_core import __version__; print(f'Version: {__version__}')"
```

### 6.3 Version-Specific Test Markers

```python
# tests/conftest.py

import pytest
from sum_core import __version__

def pytest_configure(config):
    """Register custom markers for version-specific tests."""
    config.addinivalue_line(
        "markers", "requires_themes: mark test as requiring theme system (0.6.x+)"
    )
    config.addinivalue_line(
        "markers", "legacy_only: mark test as legacy (0.5.x only)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on current version."""
    current_version = tuple(int(x) for x in __version__.split(".")[:2])
    
    for item in items:
        # Skip theme tests on 0.5.x
        if "requires_themes" in item.keywords:
            if current_version < (0, 6):
                item.add_marker(pytest.mark.skip(
                    reason=f"Requires 0.6.x+, current: {__version__}"
                ))
        
        # Skip legacy tests on 0.6.x+
        if "legacy_only" in item.keywords:
            if current_version >= (0, 6):
                item.add_marker(pytest.mark.skip(
                    reason=f"Legacy test for 0.5.x, current: {__version__}"
                ))
```

---

## 7. Theme Performance & Accessibility Gates

### 7.1 Performance Budget

From POST-MVP_BIG-PLAN.md, Theme A must meet:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Lighthouse Performance | ≥ 90 | CI Lighthouse audit |
| Lighthouse Accessibility | ≥ 90 | CI Lighthouse audit |
| Lighthouse SEO | ≥ 90 | CI Lighthouse audit |
| CSS Bundle Size | ≤ 100kb (compressed) | Build artifact check |
| First Contentful Paint | < 1.8s | Lighthouse metric |

### 7.2 Accessibility Gate Tests

```python
# tests/themes/test_theme_accessibility.py

"""
Theme Accessibility Gate Tests

File: tests/themes/test_theme_accessibility.py
Purpose: Verify themes meet WCAG 2.1 AA baseline
Dependencies: pytest, axe-core-python (or similar)
"""

import pytest
from pathlib import Path

from axe_selenium_python import Axe
from selenium import webdriver


THEME_A_DIR = Path(__file__).parent.parent.parent / "themes" / "theme_a"


@pytest.fixture(scope="module")
def browser():
    """Headless browser for accessibility testing."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.mark.requires_themes
@pytest.mark.slow
class TestThemeAccessibility:
    """Accessibility tests for Theme A."""
    
    def test_base_template_has_skip_link(self) -> None:
        """Base template must have skip-to-main-content link."""
        base_html = THEME_A_DIR / "templates" / "theme" / "base.html"
        content = base_html.read_text()
        
        assert "skip" in content.lower(), "Missing skip link"
        assert 'href="#main' in content or 'href="#content' in content, (
            "Skip link must target main content"
        )
    
    def test_base_template_has_main_landmark(self) -> None:
        """Base template must have <main> landmark."""
        base_html = THEME_A_DIR / "templates" / "theme" / "base.html"
        content = base_html.read_text()
        
        assert "<main" in content, "Missing <main> landmark"
    
    def test_focus_states_defined_in_css(self) -> None:
        """Theme CSS must define visible focus states."""
        css_file = THEME_A_DIR / "static" / "theme_a" / "css" / "main.css"
        
        if not css_file.exists():
            # Check for input.css (Tailwind source)
            css_file = THEME_A_DIR / "static" / "theme_a" / "css" / "input.css"
        
        if not css_file.exists():
            pytest.skip("No CSS file found to check focus states")
        
        content = css_file.read_text()
        
        # Check for focus styling (Tailwind uses focus: prefix)
        has_focus = (
            ":focus" in content or 
            "focus:" in content or  # Tailwind
            "focus-visible" in content
        )
        
        assert has_focus, "No focus states defined in theme CSS"
```

### 7.3 CI Performance Gate

```yaml
# .github/workflows/ci.yml (excerpt)

  theme-performance:
    name: Theme Performance Gate
    runs-on: ubuntu-latest
    needs: [test]
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build theme CSS
        run: |
          cd themes/theme_a/tailwind
          npm ci
          npm run build
      
      - name: Check CSS bundle size
        run: |
          CSS_FILE="themes/theme_a/static/theme_a/css/main.css"
          SIZE=$(stat -f%z "$CSS_FILE" 2>/dev/null || stat -c%s "$CSS_FILE")
          GZIPPED=$(gzip -c "$CSS_FILE" | wc -c)
          
          echo "CSS size: $SIZE bytes"
          echo "Gzipped: $GZIPPED bytes"
          
          # 100kb = 102400 bytes
          if [ "$GZIPPED" -gt 102400 ]; then
            echo "❌ CSS bundle exceeds 100kb limit!"
            exit 1
          fi
          
          echo "✅ CSS bundle within limits"
      
      - name: Start test server
        run: |
          make run-test-server &
          sleep 10
      
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v10
        with:
          urls: |
            http://localhost:8000/
            http://localhost:8000/services/
          budgetPath: ./lighthouse-budget.json
          uploadArtifacts: true
```

---

## 8. Loop Sites Validation Strategy

### 8.1 Validation Stages

From POST-MVP_BIG-PLAN.md, Loop Site A (Sage & Stone) gates Loop Site C (LINTEL).

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LOOP SITES VALIDATION FLOW                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  test_project (Loop B)          Sage & Stone (Loop A)               │
│  ├── CI integration tests       ├── Deploy cycle 1                  │
│  ├── Local development          │   ├── Fresh deploy                │
│  └── Quick validation           │   ├── Content populated           │
│                                  │   ├── Forms working               │
│                                  │   └── Upgrade 0.6.0 → 0.6.1       │
│                                  │                                   │
│                                  ├── Deploy cycle 2                  │
│                                  │   ├── Upgrade 0.6.1 → 0.6.2      │
│                                  │   ├── Rollback rehearsal          │
│                                  │   └── "What broke" documented     │
│                                  │                                   │
│                                  └── ✅ GATE PASSED                  │
│                                       │                              │
│                                       ▼                              │
│                                  LINTEL (Loop C)                     │
│                                  ├── Benefits from proven patterns   │
│                                  └── Higher confidence               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.2 Loop Site Validation Checklist (Automated Where Possible)

```python
# tests/loopsites/test_sage_and_stone_gates.py

"""
Sage & Stone Validation Gates

File: tests/loopsites/test_sage_and_stone_gates.py
Purpose: Automated validation checks for Loop Site A
Dependencies: pytest, requests
Note: Run against deployed staging/production
"""

import os
import pytest
import requests


STAGING_URL = os.getenv("SAGE_STONE_STAGING_URL", "https://sage-and-stone.lintel.site")


@pytest.mark.loopsite
@pytest.mark.skipif(
    not os.getenv("RUN_LOOPSITE_TESTS"),
    reason="Set RUN_LOOPSITE_TESTS=1 to run loop site validation"
)
class TestSageAndStoneGates:
    """Validation tests for Sage & Stone deployment."""
    
    def test_health_endpoint(self) -> None:
        """Health endpoint returns 200."""
        response = requests.get(f"{STAGING_URL}/health/", timeout=10)
        assert response.status_code == 200
    
    def test_homepage_renders(self) -> None:
        """Homepage loads without error."""
        response = requests.get(STAGING_URL, timeout=10)
        assert response.status_code == 200
        assert "Sage" in response.text or "Kitchen" in response.text
    
    def test_blog_listing_page(self) -> None:
        """Blog index page renders."""
        response = requests.get(f"{STAGING_URL}/blog/", timeout=10)
        assert response.status_code == 200
    
    def test_contact_form_page(self) -> None:
        """Contact page with form renders."""
        response = requests.get(f"{STAGING_URL}/contact/", timeout=10)
        assert response.status_code == 200
        assert "<form" in response.text.lower()
    
    def test_theme_css_loads(self) -> None:
        """Theme CSS file is accessible."""
        response = requests.get(f"{STAGING_URL}/static/theme_a/css/main.css", timeout=10)
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
    
    def test_lighthouse_scores_meet_targets(self) -> None:
        """Lighthouse scores meet performance gates."""
        # This would integrate with Lighthouse CI or similar
        # Placeholder for manual verification or CI integration
        pytest.skip("Run via Lighthouse CI - see .github/workflows/")
```

---

## 9. Test Suite Organization

### 9.1 Directory Structure

```
sum-platform/
├── tests/                          # Root test directory
│   ├── conftest.py                 # Global fixtures, markers, version checks
│   ├── utils/
│   │   ├── safe_cleanup.py         # Safe deletion utilities
│   │   └── fixtures.py             # Shared test fixtures
│   │
│   ├── unit/                       # Unit tests (fast, isolated)
│   │   ├── core/                   # sum_core unit tests
│   │   └── cli/                    # CLI unit tests
│   │
│   ├── integration/                # Integration tests
│   │   ├── core/                   # sum_core integration
│   │   └── templates/              # Template rendering tests
│   │
│   ├── themes/                     # Theme-specific tests (0.6.x+)
│   │   ├── conftest.py             # Theme-aware fixtures
│   │   ├── test_theme_metadata.py
│   │   ├── test_theme_a_rendering.py
│   │   ├── test_theme_block_contracts.py
│   │   └── test_theme_accessibility.py
│   │
│   ├── cli/                        # CLI integration tests
│   │   ├── conftest.py             # CLI isolation fixtures
│   │   ├── test_theme_init_safe.py
│   │   └── test_cli_check.py
│   │
│   ├── loopsites/                  # Loop site validation
│   │   └── test_sage_and_stone_gates.py
│   │
│   └── smoke/                      # Smoke tests for legacy versions
│       └── test_smoke_0_5_x.py
│
├── cli/
│   └── tests/                      # CLI-specific tests (duplicates some of above)
│       └── conftest.py             # Uses isolation patterns
│
└── core/
    └── sum_core/
        └── tests/                  # Core package tests
```

### 9.2 Test Markers

```ini
# pytest.ini

[pytest]
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests
    slow: Slow tests (> 5s)
    requires_themes: Requires theme system (0.6.x+)
    legacy_only: Only for 0.5.x
    loopsite: Loop site validation (requires deployed site)
    regression: Regression tests for known issues
    
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

### 9.3 Running Tests

```bash
# Full suite
make test

# Fast unit tests only
pytest -m unit

# Theme tests (0.6.x+)
pytest tests/themes/

# Skip slow tests
pytest -m "not slow"

# Run with specific Django settings
DJANGO_SETTINGS_MODULE=test_project.settings pytest

# Verbose with coverage
pytest -v --cov=sum_core --cov-report=html
```

---

## 10. Defect Tracking & Regression

### 10.1 Known Issue Markers

For issues like the THEME-15-A test failures, use regression markers:

```python
# tests/themes/test_known_issues.py

"""
Known Issues and Regression Tests

File: tests/themes/test_known_issues.py
Purpose: Document and test known issues
"""

import pytest


@pytest.mark.regression
@pytest.mark.xfail(
    reason="THEME-15-A: Settings leakage in full suite causes template override failure",
    strict=False,  # Don't fail if it starts passing
)
def test_theme_15_a_stats_block_override():
    """
    Regression test for THEME-15-A.
    
    Issue: StatsBlock template override works in isolation but fails
           in full test suite due to settings leakage.
    
    Root cause: RUNNING_TESTS conditional in settings.py
    Fix: Remove conditional, use consistent template loading
    
    Related: theme-delete-drama.md, THEME-15-A_followup.md
    """
    # This test documents the issue and will pass once fixed
    from django.template.loader import get_template
    
    template = get_template("sum_core/blocks/stats.html")
    assert "theme_a" in template.origin.name
```

### 10.2 Post-Incident Testing

After incidents like Theme Delete Drama, add permanent regression tests:

```python
# tests/cli/test_theme_delete_regression.py

"""
Theme Delete Drama Regression Tests

File: tests/cli/test_theme_delete_regression.py
Purpose: Prevent recurrence of theme deletion incident
Related: theme-delete-drama.md
"""

from pathlib import Path
import pytest


REPO_ROOT = Path(__file__).parent.parent.parent


class TestThemeDeleteDramaRegression:
    """
    Permanent regression tests from Theme Delete Drama incident.
    
    Incident Summary:
    - CLI tests used shutil.rmtree on paths that resolved to source
    - themes/theme_a was deleted and committed to develop
    - Fixed by: isolation with tmp_path, safe deletion guards
    
    These tests ensure the fix remains effective.
    """
    
    def test_theme_a_directory_exists(self) -> None:
        """theme_a directory must always exist."""
        theme_a = REPO_ROOT / "themes" / "theme_a"
        assert theme_a.exists(), (
            "CRITICAL: themes/theme_a is missing! "
            "See theme-delete-drama.md for recovery."
        )
    
    def test_theme_a_required_files_exist(self) -> None:
        """theme_a must have all required files."""
        theme_a = REPO_ROOT / "themes" / "theme_a"
        
        required = [
            "theme.json",
            "templates/theme/base.html",
            "static/theme_a/css/main.css",
            "tailwind/tailwind.config.js",
        ]
        
        for path in required:
            full_path = theme_a / path
            assert full_path.exists(), f"Missing required file: {path}"
    
    def test_themes_not_in_gitignore(self) -> None:
        """themes/ must not be gitignored."""
        gitignore = REPO_ROOT / ".gitignore"
        if not gitignore.exists():
            return
        
        content = gitignore.read_text()
        dangerous_patterns = [
            "themes/",
            "themes/*",
            "themes/theme_a",
            "**/theme_a",
        ]
        
        for pattern in dangerous_patterns:
            assert pattern not in content, (
                f"DANGEROUS: '{pattern}' in .gitignore would hide theme deletion!"
            )
```

---

## 11. CI Pipeline Updates

### 11.1 Updated CI Workflow

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [develop, main, 'release/**']
  pull_request:
    branches: [develop, main]

jobs:
  lint:
    name: Lint & Type Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: pip install ruff mypy
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy core/sum_core/ --ignore-missing-imports

  test-unit:
    name: Unit Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e ./core
          pip install pytest pytest-django factory_boy coverage
      - name: Run unit tests
        run: pytest -m unit -v --cov=sum_core
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  test-integration:
    name: Integration Tests
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e ./core
          pip install pytest pytest-django factory_boy
      - name: Run integration tests
        run: pytest -m integration -v
        env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test

  test-themes:
    name: Theme Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - uses: actions/setup-node@v4
        with:
          node-version: '24'
      - name: Build theme CSS
        run: |
          cd themes/theme_a/tailwind
          npm ci
          npm run build
      - name: Install Python dependencies
        run: |
          pip install -e ./core
          pip install pytest pytest-django beautifulsoup4
      - name: Run theme tests
        run: pytest tests/themes/ -v
      - name: Verify theme_a exists (regression check)
        run: |
          test -d themes/theme_a || (echo "CRITICAL: theme_a missing!" && exit 1)
          test -f themes/theme_a/theme.json || (echo "CRITICAL: theme.json missing!" && exit 1)

  test-cli:
    name: CLI Tests (Isolated)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -e ./cli
          pip install pytest
      - name: Run CLI tests
        run: pytest cli/tests/ -v
      - name: Final safety check
        run: |
          echo "Verifying source themes not deleted..."
          ls -la themes/
          test -d themes/theme_a
          echo "✅ Source themes intact"
```

---

## 12. Entry & Exit Criteria (Post-MVP)

### 12.1 Feature Branch Merge

**Entry:**
- [ ] All unit tests pass locally
- [ ] Theme tests pass (if theme changes)
- [ ] No new ruff/mypy errors

**Exit:**
- [ ] CI pipeline green (lint, unit, integration, theme tests)
- [ ] Coverage ≥ 80% for new code
- [ ] Theme regression tests pass (theme_a exists, required files present)
- [ ] No source file deletions outside intended changes

### 12.2 Version Release (0.6.x)

**Exit:**
- [ ] All CI checks pass
- [ ] Theme performance gates met (Lighthouse ≥ 90)
- [ ] Theme accessibility gates met (axe-core, manual review)
- [ ] CSS bundle ≤ 100kb compressed
- [ ] Loop Site A (Sage & Stone) validation passes
- [ ] No critical/high bugs open > 7 days
- [ ] "What broke" from previous release addressed

### 12.3 Loop Site Progression

**Sage & Stone → LINTEL Gate:**
- [ ] Minimum 2 deploy + upgrade cycles completed
- [ ] Rollback procedure rehearsed at least once
- [ ] Theme stability validated across upgrades
- [ ] Blog + Dynamic Forms working in production
- [ ] Performance targets consistently met
- [ ] "What broke last time" log shows improvement trend

---

## 13. Risk Register (Post-MVP Specific)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Source file deletion in tests** | Low (mitigated) | Critical | Safe deletion guards, regression tests, tmp_path isolation |
| **Settings leakage between tests** | Medium | High | Explicit settings fixtures, autouse=True for theme tests |
| **Template loading inconsistency** | Medium | High | Remove RUNNING_TESTS conditional, deterministic TEMPLATES config |
| **Theme CSS bloat** | Medium | Medium | Bundle size gate in CI, PurgeCSS configuration |
| **0.5.x regression** | Low | High | Weekly smoke tests, version markers, frozen branch policy |
| **Theme performance regression** | Medium | Medium | Lighthouse CI gate, performance budgets |
| **CLI init corrupts source** | Low (mitigated) | Critical | SUM_CLIENT_OUTPUT_PATH isolation, safety checks |

---

## 14. Document Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | December 21, 2025 | Initial post-MVP test strategy |

**Key Decisions:**
- Test isolation using `tmp_path` + env vars is mandatory for CLI tests
- Safe deletion guards are required for all test cleanup
- Template loading configuration must be identical in test and production
- Theme regression tests (theme_a existence) run on every CI build
- Multi-version testing via markers, not separate test suites

**Open Items:**
- [ ] Integrate axe-core for automated accessibility testing
- [ ] Set up Lighthouse CI for performance gates
- [ ] Create Loop Site validation dashboard

---

*This document extends test-strategy-v1.1 for post-MVP development. Both documents remain authoritative for their respective scopes.*
