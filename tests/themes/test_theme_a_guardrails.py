"""
Name: Theme A Guardrails Tests
Path: tests/themes/test_theme_a_guardrails.py
Purpose: Prevent compiled Tailwind CSS drift and regressions
Family: Themes / Toolchain
Dependencies: filesystem, hashlib, pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import the fingerprint module
repo_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(repo_root / "core"))

from sum_core.themes.theme_a.build_fingerprint import (  # noqa: E402
    compute_fingerprint,
    get_theme_a_root,
)


class TestThemeABuildFingerprint:
    """Tests that validate Theme A's build fingerprint freshness.

    These tests prevent compiled CSS drift by ensuring the fingerprint
    is regenerated whenever Tailwind inputs change.
    """

    @staticmethod
    def _get_fingerprint_path() -> Path:
        """Get path to the committed fingerprint file."""
        theme_root = get_theme_a_root()
        return Path(theme_root / "static" / "theme_a" / "css" / ".build_fingerprint")

    @staticmethod
    def _read_committed_fingerprint() -> str:
        """Read the committed fingerprint hash."""
        fingerprint_path = TestThemeABuildFingerprint._get_fingerprint_path()
        if not fingerprint_path.exists():
            raise FileNotFoundError(
                f"Build fingerprint not found at {fingerprint_path}\n\n"
                "This file must exist to validate Theme A build freshness.\n"
                "Generate it by running:\n"
                "  cd core/sum_core/themes/theme_a\n"
                "  python -m sum_core.themes.theme_a.build_fingerprint\n"
                "  git add static/theme_a/css/.build_fingerprint\n"
                "  git commit\n"
            )
        return fingerprint_path.read_text().strip()

    def test_fingerprint_file_exists(self) -> None:
        """Build fingerprint file must exist in the repository."""
        fingerprint_path = self._get_fingerprint_path()
        assert fingerprint_path.exists(), (
            f"Build fingerprint missing at {fingerprint_path}\n\n"
            "Generate it by running:\n"
            "  cd core/sum_core/themes/theme_a\n"
            "  python -m sum_core.themes.theme_a.build_fingerprint\n"
        )

    def test_fingerprint_is_current(self) -> None:
        """Build fingerprint must match current Tailwind input state.

        This test prevents CSS drift by ensuring that whenever:
        - tailwind.config.js changes
        - postcss.config.js changes
        - input.css changes
        - any template file changes

        ...the fingerprint is regenerated and main.css is rebuilt.

        Failure indicates inputs changed without rebuilding CSS.
        """
        theme_root = get_theme_a_root()
        committed_hash = self._read_committed_fingerprint()
        current_hash = compute_fingerprint(theme_root)

        assert committed_hash == current_hash, (
            f"Build fingerprint is STALE!\n\n"
            f"Committed: {committed_hash}\n"
            f"Current:   {current_hash}\n\n"
            f"Tailwind inputs have changed but CSS was not rebuilt.\n\n"
            f"Fix:\n"
            f"  1. cd core/sum_core/themes/theme_a\n"
            f"  2. npm run build\n"
            f"  3. python -m sum_core.themes.theme_a.build_fingerprint\n"
            f"  4. git add static/theme_a/css/main.css static/theme_a/css/.build_fingerprint\n"
            f"  5. git commit -m 'chore:theme-a-rebuild CSS after config changes'\n"
        )


class TestThemeACompiledCSSValidity:
    """Tests that validate Theme A's compiled CSS quality and integrity.

    These tests ensure:
    - CSS exists and is non-trivial
    - Contains expected Tailwind utilities
    - Free from legacy core CSS contamination
    """

    @staticmethod
    def _get_main_css_path() -> Path:
        """Get path to Theme A's compiled main.css."""
        theme_root = get_theme_a_root()
        return Path(theme_root / "static" / "theme_a" / "css" / "main.css")

    @staticmethod
    def _read_main_css() -> str:
        """Read compiled CSS content."""
        css_path = TestThemeACompiledCSSValidity._get_main_css_path()
        if not css_path.exists():
            raise FileNotFoundError(
                f"Compiled CSS not found at {css_path}\n\n"
                "CSS must be built before running tests.\n"
                "Generate it by running:\n"
                "  cd core/sum_core/themes/theme_a\n"
                "  npm run build\n"
                "  python -m sum_core.themes.theme_a.build_fingerprint\n"
            )
        return css_path.read_text()

    def test_compiled_css_exists(self) -> None:
        """Compiled main.css must exist."""
        css_path = self._get_main_css_path()
        assert css_path.exists(), (
            f"Compiled CSS not found at {css_path}\n\n"
            "Theme A requires compiled Tailwind CSS.\n"
            "Generate it by running:\n"
            "  cd core/sum_core/themes/theme_a\n"
            "  npm run build\n"
        )

    def test_compiled_css_non_trivial_size(self) -> None:
        """Compiled CSS must be substantial (> 5KB).

        A tiny CSS file indicates Tailwind didn't compile correctly
        or configuration is broken.
        """
        css_path = self._get_main_css_path()
        file_size = css_path.stat().st_size
        min_size = 5000  # 5KB

        assert file_size > min_size, (
            f"Compiled CSS is only {file_size} bytes (expected > {min_size}).\n\n"
            f"This suggests Tailwind compilation failed or is incomplete.\n"
            f"Rebuild by running:\n"
            f"  cd core/sum_core/themes/theme_a\n"
            f"  npm run build\n"
        )

    def test_compiled_css_contains_flex_utility(self) -> None:
        """Compiled CSS must contain .flex utility (Tailwind signature)."""
        content = self._read_main_css()

        assert ".flex{display:flex}" in content, (
            "Missing .flex{display:flex} utility in compiled CSS.\n\n"
            "This is a core Tailwind utility that should always be present.\n"
            "If missing, Tailwind compilation is broken.\n"
            "Rebuild by running:\n"
            "  cd core/sum_core/themes/theme_a\n"
            "  npm run build\n"
        )

    def test_compiled_css_contains_hidden_utility(self) -> None:
        """Compiled CSS must contain .hidden utility (Tailwind signature)."""
        content = self._read_main_css()

        assert ".hidden{display:none}" in content, (
            "Missing .hidden{display:none} utility in compiled CSS.\n\n"
            "This is a core Tailwind utility that should always be present.\n"
            "If missing, Tailwind compilation is broken.\n"
            "Rebuild by running:\n"
            "  cd core/sum_core/themes/theme_a\n"
            "  npm run build\n"
        )

    def test_no_legacy_core_css_import_statement(self) -> None:
        """Compiled CSS must NOT contain @import statements.

        Tailwind output should be self-contained. Any @import indicates
        legacy core CSS bleed, which violates the v0.6 theme contract.
        """
        content = self._read_main_css()

        assert '@import url("/static/sum_core/css/main.css")' not in content, (
            "Compiled CSS contains legacy core CSS import!\n\n"
            'Found: @import url("/static/sum_core/css/main.css")\n\n'
            "This violates the v0.6 theme ownership contract.\n"
            "Theme A must be self-contained without core CSS dependencies.\n\n"
            "Fix:\n"
            "  1. Remove @import from input.css or Tailwind config\n"
            "  2. cd core/sum_core/themes/theme_a\n"
            "  3. npm run build\n"
            "  4. python -m sum_core.themes.theme_a.build_fingerprint\n"
        )

    def test_no_legacy_core_css_reference(self) -> None:
        """Compiled CSS must NOT reference sum_core/css/main.css anywhere.

        Any reference to the legacy core CSS path indicates contamination
        or improper configuration.
        """
        content = self._read_main_css()

        assert "sum_core/css/main.css" not in content, (
            "Compiled CSS references legacy core CSS path!\n\n"
            "Found: sum_core/css/main.css\n\n"
            "This violates the v0.6 theme ownership contract.\n"
            "Theme A must be completely independent of core styling.\n\n"
            "Fix:\n"
            "  1. Remove all references to sum_core/css/main.css\n"
            "  2. cd core/sum_core/themes/theme_a\n"
            "  3. npm run build\n"
            "  4. python -m sum_core.themes.theme_a.build_fingerprint\n"
        )

    def test_no_at_import_statements(self) -> None:
        """Compiled CSS should not contain any @import statements.

        Tailwind processes all @import during build. If @import remains
        in the output, it suggests incomplete processing or configuration issues.
        """
        content = self._read_main_css()

        assert "@import" not in content, (
            "Compiled CSS contains @import statement(s).\n\n"
            "Tailwind should resolve all imports during build.\n"
            "Remaining @import statements indicate:\n"
            "  - PostCSS import plugin misconfiguration\n"
            "  - Incomplete build process\n"
            "  - Legacy CSS contamination\n\n"
            "Review input.css and Tailwind/PostCSS configuration.\n"
        )


class TestThemeAGuardrailsIntegration:
    """Integration tests to verify guardrails work end-to-end."""

    def test_fingerprint_module_is_runnable(self) -> None:
        """The build_fingerprint module must be runnable via python -m."""
        theme_root = get_theme_a_root()
        fingerprint_module = theme_root / "build_fingerprint.py"

        assert (
            fingerprint_module.exists()
        ), f"Fingerprint module not found at {fingerprint_module}"

        # Verify it has a main block
        content = fingerprint_module.read_text()
        assert (
            'if __name__ == "__main__":' in content
        ), "Fingerprint module must be runnable via python -m"
        assert "def main()" in content, "Fingerprint module must define main() function"

    def test_all_required_inputs_exist(self) -> None:
        """All fingerprint input files must exist."""
        theme_root = get_theme_a_root()

        # Required files
        required = [
            theme_root / "tailwind.config.js",
            theme_root / "static" / "theme_a" / "css" / "input.css",
            theme_root / "templates" / "theme",
        ]

        for path in required:
            assert path.exists(), (
                f"Required fingerprint input missing: {path}\n\n"
                f"All Tailwind inputs must be present to compute fingerprint."
            )

    def test_templates_directory_has_html_files(self) -> None:
        """Templates directory must contain .html files."""
        theme_root = get_theme_a_root()
        templates_dir = theme_root / "templates" / "theme"

        html_files = list(templates_dir.rglob("*.html"))
        assert len(html_files) > 0, (
            f"No HTML templates found in {templates_dir}\n\n"
            f"Theme A requires template files for fingerprint computation."
        )
