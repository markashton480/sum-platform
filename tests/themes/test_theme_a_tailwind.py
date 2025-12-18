"""
Name: Theme A Tailwind Toolchain Tests
Path: tests/themes/test_theme_a_tailwind.py
Purpose: Automated tests proving Theme A has compiled Tailwind CSS and no legacy core bleed.
         These tests are part of the v0.6 Theme Toolchain v1 contract (M6-A-001).
Family: sum_core tests
Dependencies: sum_core.themes, pathlib
"""
from __future__ import annotations

from pathlib import Path


class TestThemeATailwindCSS:
    """Tests for Theme A compiled Tailwind CSS.

    These verify the Theme Toolchain v1 contract:
    - Compiled CSS exists and is non-trivial
    - Contains Tailwind utility signatures
    - No legacy sum_core CSS import
    """

    @staticmethod
    def _get_theme_a_css_path() -> Path:
        """Get the path to Theme A's compiled main.css."""
        repo_root = Path(__file__).resolve().parents[2]
        return (
            repo_root
            / "core"
            / "sum_core"
            / "themes"
            / "theme_a"
            / "static"
            / "theme_a"
            / "css"
            / "main.css"
        )

    def test_compiled_css_exists(self) -> None:
        """Theme A compiled CSS file must exist."""
        css_path = self._get_theme_a_css_path()
        assert css_path.exists(), f"Compiled CSS not found at {css_path}"

    def test_compiled_css_non_trivial_size(self) -> None:
        """Compiled CSS must be non-trivial (at least 5KB indicates real content)."""
        css_path = self._get_theme_a_css_path()
        file_size = css_path.stat().st_size
        min_expected = 5000  # 5KB minimum for real Tailwind output
        assert file_size >= min_expected, (
            f"Compiled CSS is only {file_size} bytes; expected at least {min_expected}. "
            "This suggests Tailwind didn't compile correctly."
        )

    def test_compiled_css_contains_tailwind_utilities(self) -> None:
        """Compiled CSS must contain known Tailwind utility rules."""
        css_path = self._get_theme_a_css_path()
        content = css_path.read_text()

        # Check for standard Tailwind utility patterns
        assert (
            ".flex{display:flex}" in content
        ), "Missing .flex utility - Tailwind didn't compile"
        assert (
            ".hidden{display:none}" in content
        ), "Missing .hidden utility - Tailwind didn't compile"
        assert (
            ".relative{position:relative}" in content
        ), "Missing .relative utility - Tailwind didn't compile"

    def test_no_legacy_core_css_import(self) -> None:
        """Compiled CSS must NOT import legacy sum_core/css/main.css."""
        css_path = self._get_theme_a_css_path()
        content = css_path.read_text()

        # Check for any @import statements (Tailwind output shouldn't have any)
        assert "@import" not in content, (
            "Compiled CSS contains @import statement. "
            "Theme A CSS must be self-contained without legacy core imports."
        )

        # Explicit check for old core CSS path
        assert "sum_core/css/main.css" not in content, (
            "Compiled CSS references legacy sum_core/css/main.css. "
            "This violates the v0.6 theme ownership contract."
        )

    def test_css_variables_for_branding(self) -> None:
        """Compiled CSS must include CSS variables so branding works without rebuild."""
        css_path = self._get_theme_a_css_path()
        content = css_path.read_text()

        # Check for branding-related CSS variables
        assert (
            "--color-sage-terra" in content
        ), "Missing --color-sage-terra CSS variable for branding"
        assert (
            "--color-sage-black" in content
        ), "Missing --color-sage-black CSS variable for branding"

    def test_theme_a_custom_components_present(self) -> None:
        """Compiled CSS must include Theme A custom component styles."""
        css_path = self._get_theme_a_css_path()
        content = css_path.read_text()

        # Check for Theme A signature classes
        assert ".reveal" in content, "Missing .reveal animation class"
        assert ".mega-panel" in content, "Missing .mega-panel class"
        assert (
            ".accordion-grid-wrapper" in content
        ), "Missing .accordion-grid-wrapper class"
        assert ".banner-grid-wrapper" in content, "Missing .banner-grid-wrapper class"


class TestThemeATailwindToolchain:
    """Tests for Theme A Tailwind build toolchain files."""

    @staticmethod
    def _get_theme_a_path() -> Path:
        """Get the path to Theme A directory."""
        repo_root = Path(__file__).resolve().parents[2]
        return repo_root / "core" / "sum_core" / "themes" / "theme_a"

    def test_package_json_exists(self) -> None:
        """package.json must exist for maintainer toolchain."""
        theme_path = self._get_theme_a_path()
        assert (theme_path / "package.json").exists()

    def test_tailwind_config_exists(self) -> None:
        """tailwind.config.js must exist."""
        theme_path = self._get_theme_a_path()
        assert (theme_path / "tailwind.config.js").exists()

    def test_input_css_exists(self) -> None:
        """input.css (Tailwind source) must exist."""
        theme_path = self._get_theme_a_path()
        assert (theme_path / "static" / "theme_a" / "css" / "input.css").exists()

    def test_lockfile_exists(self) -> None:
        """npm-shrinkwrap.json or package-lock.json must exist for reproducible builds."""
        theme_path = self._get_theme_a_path()
        has_shrinkwrap = (theme_path / "npm-shrinkwrap.json").exists()
        has_lockfile = (theme_path / "package-lock.json").exists()
        assert has_shrinkwrap or has_lockfile, (
            "No npm lockfile found. Add npm-shrinkwrap.json or package-lock.json "
            "to prevent build drift."
        )
