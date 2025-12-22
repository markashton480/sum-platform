from __future__ import annotations

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

    def test_core_only_template_resolves_from_core(self) -> None:
        """Template only in core (trust_strip.html) falls back correctly.

        trust_strip.html exists in core/sum_core/templates but NOT in
        themes/theme_a/templates, so it must resolve from core regardless
        of theme configuration. This tests the APP_DIRS fallback path.
        """
        template = get_template("sum_core/blocks/trust_strip.html")
        origin = template.origin.name

        assert (
            "sum_core" in origin and "themes" not in origin
        ), f"Expected trust_strip.html from core (not in theme), got: {origin}"
