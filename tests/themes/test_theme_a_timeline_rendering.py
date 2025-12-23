from __future__ import annotations

from io import BytesIO

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from home.models import HomePage
from PIL import Image as PILImage
from wagtail.images import get_image_model
from wagtail.models import Page, Site

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


def _create_image(title: str, filename: str):
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (1200, 800), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title=title,
        file=SimpleUploadedFile(filename, content, content_type="image/png"),
    )


def _create_standard_page_with_timeline(slug: str, image) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Timeline Test", slug=slug)
    standard.body = [
        (
            "timeline",
            {
                "eyebrow": "Our Story",
                "heading": "<p>Milestones</p>",
                "intro": "<p>From our first install to today.</p>",
                "items": [
                    {
                        "date_label": "2018",
                        "heading": "Founded",
                        "body": "<p>Started with one van and a lot of grit.</p>",
                    },
                    {
                        "date_label": "2022",
                        "heading": "New HQ",
                        "body": "<p>Opened our new studio and warehouse.</p>",
                        "image": image,
                        "image_alt": "Team outside the new HQ",
                    },
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


def _assert_template_origin(response, theme_active_copy, template_name: str) -> None:
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


class TestThemeATimelineBlock:
    def test_timeline_block_renders_theme_template_and_content(
        self, client: Client, theme_active_copy
    ) -> None:
        image = _create_image("Timeline Image", "timeline.png")
        page = _create_standard_page_with_timeline("timeline-theme-a", image)

        response = client.get(page.url)
        assert response.status_code == 200
        _assert_template_origin(
            response, theme_active_copy, "sum_core/blocks/timeline.html"
        )

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        timeline_section = soup.find(
            "section", class_=lambda value: value and "py-24" in str(value)
        )
        assert isinstance(timeline_section, Tag)
        assert "Our Story" in timeline_section.get_text()
        assert "Milestones" in timeline_section.get_text()

        items = timeline_section.find_all("li")
        assert len(items) == 2
        date_labels = []
        for item in items:
            span = item.find("span")
            assert isinstance(span, Tag)
            date_labels.append(span.get_text(strip=True))
        assert "2018" in date_labels and "2022" in date_labels

        image_tag = timeline_section.find("img")
        assert image_tag is not None
        assert image_tag.get("alt") == "Team outside the new HQ"
