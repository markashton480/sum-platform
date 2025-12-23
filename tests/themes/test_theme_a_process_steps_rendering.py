from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _get_classes(tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


def _create_standard_page_with_process_steps(slug: str) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage.objects.first()
    if homepage is None:
        homepage = HomePage(title="Theme Test Home", slug="theme-home-process-steps")
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Process Steps Test", slug=slug)
    standard.body = [
        (
            "process",
            {
                "eyebrow": "The Timeline",
                "heading": "<p>From Concept to Commission.</p>",
                "intro": "<p>We value your privacy and your time.</p>",
                "steps": [
                    {
                        "title": "Consultation",
                        "description": "<p>We listen before we lift a tool.</p>",
                    },
                    {
                        "number": 7,
                        "title": "Preparation",
                        "description": "<p>Protection and planning.</p>",
                    },
                    {
                        "title": "Installation",
                        "description": "<p>The core technical work.</p>",
                    },
                    {
                        "title": "Calibration",
                        "description": "<p>Fine-tuning every detail.</p>",
                    },
                    {
                        "title": "Handover",
                        "description": "<p>Care and maintenance guidance.</p>",
                    },
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


class TestThemeAProcessStepsRendering:
    def _assert_template_origin(
        self, response, theme_active_copy, template_name: str
    ) -> None:
        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert template_name in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None) == template_name
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )

    def test_process_steps_renders_theme_template(
        self, client: Client, theme_active_copy
    ) -> None:
        page = _create_standard_page_with_process_steps("process-steps-theme-a")

        response = client.get(page.url)
        assert response.status_code == 200
        self._assert_template_origin(
            response, theme_active_copy, "sum_core/blocks/process_steps.html"
        )

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        section = soup.find(
            "section",
            class_=lambda value: value and "bg-sage-oat/30" in str(value),
        )
        assert section is not None
        section_classes = _get_classes(section)
        assert "py-28" in section_classes
        assert "bg-sage-oat/30" in section_classes
        assert "border-y" in section_classes

        header = soup.find(
            "div",
            class_=lambda value: value and "lg:sticky" in str(value),
        )
        assert header is not None
        assert "The Timeline" in header.get_text()
        assert "From Concept to Commission." in header.get_text()

        timeline_grid = soup.find(
            "div",
            class_=lambda value: value and "lg:grid-cols-5" in str(value),
        )
        assert timeline_grid is not None

        cards = timeline_grid.find_all(
            "div",
            class_=lambda value: value
            and "p-8" in str(value)
            and "border-sage-black/5" in str(value),
        )
        assert len(cards) == 5
        assert timeline_grid.find("div", class_="bg-sage-black") is not None
        assert "01" in timeline_grid.get_text()
        assert "07" in timeline_grid.get_text()
