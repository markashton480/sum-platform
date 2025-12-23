from __future__ import annotations

import pytest
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _create_standard_page_with_testimonials(slug: str):
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Testimonials Test", slug=slug)
    standard.body = [
        (
            "testimonials",
            {
                "eyebrow": "Client Stories",
                "heading": "<p>Trusted <em>clients</em></p>",
                "testimonials": [
                    {
                        "quote": "Quiet craftsmanship. Loud results.\nEvery detail held.",
                        "author_name": "Zelda Quinn",
                        "company": "Arc Atelier",
                        "rating": 4,
                    }
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()

    return standard


class TestThemeATestimonialsBlock:
    def test_testimonials_block_renders_theme_template(
        self, client: Client, theme_active_copy
    ) -> None:
        standard = _create_standard_page_with_testimonials("testimonials-theme-a")

        response = client.get(standard.url)
        content = response.content.decode("utf-8")

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/testimonials.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None) == "sum_core/blocks/testimonials.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )
        assert "Client Stories" in content
        assert "<em>clients</em>" in content
        assert "Rated 4 out of 5" in content
        assert "Zelda Quinn" in content
        assert "tracking-[0.2em]" in content
