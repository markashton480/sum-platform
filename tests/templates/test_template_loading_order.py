from __future__ import annotations

from pathlib import Path

import pytest
from django.template.loader import get_template

from tests.conftest import _reset_django_template_loaders

pytestmark = [pytest.mark.usefixtures("theme_active_copy")]


class TestTemplateLoadingOrder:
    """Ensure template resolution order stays deterministic (THEME-15-A)."""

    def test_theme_template_has_priority(self) -> None:
        template = get_template("sum_core/blocks/stats.html")
        origin = template.origin.name

        assert (
            "theme_a" in origin or "theme-active" in origin
        ), f"Expected Theme A to satisfy stats.html, got: {origin}"

    def test_template_origin_consistent(self) -> None:
        template_name = "sum_core/blocks/hero_image.html"
        first_origin = get_template(template_name).origin.name
        for _ in range(3):
            assert (
                get_template(template_name).origin.name == first_origin
            ), "Template origin switched mid-run"

    def test_core_fallback_when_theme_disabled(self, settings) -> None:
        theme_dir_count = len(getattr(settings, "THEME_TEMPLATE_DIRS", []))
        if not theme_dir_count:
            pytest.skip("No theme directories configured for fallback test")

        original_dirs = list(settings.TEMPLATES[0]["DIRS"])
        settings.TEMPLATES[0]["DIRS"] = original_dirs[theme_dir_count:]
        try:
            _reset_django_template_loaders()
            origin = get_template("sum_core/blocks/stats.html").origin.name
            assert (
                "sum_core" in origin
            ), "Expected stats.html to fall back to core when theme dirs removed"
        finally:
            settings.TEMPLATES[0]["DIRS"] = original_dirs
            _reset_django_template_loaders()

    def test_core_only_template_resolves_from_core(
        self, tmp_path: Path, settings
    ) -> None:
        """Template only in core falls back correctly (hermetic test).

        Sets the template search path to ONLY an empty temporary theme directory,
        completely removing all existing theme dirs. Verifies that templates
        correctly fall back to core via APP_DIRS when not found in the empty theme.
        This is fully hermetic and doesn't depend on the actual contents of any theme.
        """
        # Create empty theme dir that will be the ONLY configured theme dir
        empty_theme_templates = tmp_path / "empty_theme" / "templates"
        empty_theme_templates.mkdir(parents=True)

        # Template we know exists in core but won't be in our empty theme
        core_only_template = "sum_core/blocks/stats.html"

        # Replace all theme dirs with ONLY the empty theme (fully isolated)
        original_dirs = list(settings.TEMPLATES[0]["DIRS"])
        settings.TEMPLATES[0]["DIRS"] = [str(empty_theme_templates)]

        try:
            _reset_django_template_loaders()

            # Resolve template - must come from core since empty theme has nothing
            template = get_template(core_only_template)
            origin = template.origin.name

            # Should resolve from core (not our empty theme)
            assert "sum_core" in origin and str(empty_theme_templates) not in origin, (
                f"Expected {core_only_template} to fall back to core when "
                f"only empty theme configured, got: {origin}"
            )
        finally:
            settings.TEMPLATES[0]["DIRS"] = original_dirs
            _reset_django_template_loaders()
