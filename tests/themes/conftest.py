"""
Name: Theme Tests Configuration
Path: tests/themes/conftest.py
Purpose: Provide standard fixtures and helpers for theme test suite.
Family: Shared fixtures for theme tests.
Dependencies: pytest, tests.utils.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.utils import REPO_ROOT, create_filesystem_sandbox

# =============================================================================
# Path Fixtures (session-scoped)
# =============================================================================


@pytest.fixture(scope="session")
def themes_root_dir() -> Path:
    """Return the canonical themes directory.

    Single source of truth for all theme-related paths in tests.
    """
    return REPO_ROOT / "themes"


@pytest.fixture(scope="session")
def available_theme_slugs(themes_root_dir: Path) -> list[str]:
    """Discover available theme slugs dynamically.

    Scans the themes/ directory for subdirectories containing theme.json.
    Returns a sorted list of theme slugs.
    """
    slugs = []
    if themes_root_dir.exists():
        for subdir in themes_root_dir.iterdir():
            if subdir.is_dir() and (subdir / "theme.json").exists():
                slugs.append(subdir.name)
    return sorted(slugs)


@pytest.fixture(scope="session")
def theme_a_dir(themes_root_dir: Path) -> Path:
    """Return Theme A directory path.

    Convenience shortcut for tests explicitly targeting Theme A.
    Theme A is the canonical reference theme for the platform.
    """
    return themes_root_dir / "theme_a"


# =============================================================================
# Parametrized Fixtures
# =============================================================================


THEMES_ROOT = REPO_ROOT / "themes"


@pytest.fixture(
    scope="session", params=[p.name for p in THEMES_ROOT.iterdir() if p.is_dir()]
)
def theme_dir(request) -> Path:
    """Yield each available theme directory."""
    return THEMES_ROOT / request.param


# =============================================================================
# Helper Functions (not fixtures, import directly)
# =============================================================================


def theme_templates_dir(theme_path: Path) -> Path:
    """Return templates directory for a given theme path."""
    return theme_path / "templates"


def theme_static_dir(theme_path: Path, slug: str) -> Path:
    """Return static directory for a given theme path and slug."""
    return theme_path / "static" / slug


def assert_theme_template_origin(
    response,
    expected_theme_slug: str,
    template_name: str,
) -> None:
    """Assert that a response used a template from the expected theme.

    Verifies the rendered template's origin path contains the expected
    theme's templates directory.

    Args:
        response: Django test client response object.
        expected_theme_slug: Theme slug to verify (e.g., "theme_a").
        template_name: Name of the template to check.

    Raises:
        AssertionError: If template not found or origin doesn't match.
    """
    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]

    assert template_name in template_names, (
        f"Template '{template_name}' not found in response templates.\n"
        f"Available: {template_names}"
    )

    for template in templates:
        if getattr(template, "name", None) == template_name:
            origin = getattr(template, "origin", None)
            if origin:
                origin_path = str(getattr(origin, "name", ""))
                expected_path_fragment = f"themes/{expected_theme_slug}/templates"
                assert expected_path_fragment in origin_path, (
                    f"Template '{template_name}' origin does not match expected theme.\n"
                    f"Expected path fragment: {expected_path_fragment}\n"
                    f"Actual origin: {origin_path}"
                )
                return

    raise AssertionError(
        f"Could not verify origin for template '{template_name}'.\n"
        f"Template may not have origin information."
    )


# =============================================================================
# Autouse Safety Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def theme_filesystem_sandbox(request, tmp_path_factory):
    """Ensure theme tests operate safely without modifying repo files.

    Autouse fixture that provides a filesystem sandbox for theme tests.
    This prevents accidental writes to protected directories.
    """
    tmp_base = Path(tmp_path_factory.getbasetemp()).resolve()
    sandbox = create_filesystem_sandbox(REPO_ROOT, tmp_base, request)
    request.node.theme_filesystem_sandbox = sandbox
    return sandbox
