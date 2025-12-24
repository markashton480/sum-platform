from __future__ import annotations

from io import BytesIO

import pytest
from bs4 import BeautifulSoup
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


def _create_standard_page_with_gallery(slug: str, images) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Gallery Test", slug=slug)
    standard.body = [
        (
            "gallery",
            {
                "eyebrow": "Portfolio",
                "heading": "<p>Case Files</p>",
                "intro": "A selection of recent commissions.",
                "images": [
                    {
                        "image": images[0],
                        "alt_text": "Courtyard installation",
                        "caption": "Tranquil Courtyard",
                    },
                    {
                        "image": images[1],
                        "alt_text": "",
                        "caption": "",
                    },
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


class TestThemeAGalleryBlock:
    def test_gallery_block_renders_theme_template_and_content(
        self, client: Client, theme_active_copy
    ) -> None:
        images = [
            _create_image("Gallery Image One", "gallery_one.png"),
            _create_image("Gallery Image Two", "gallery_two.png"),
        ]
        page = _create_standard_page_with_gallery("gallery-theme-a", images)

        response = client.get(page.url)
        content = response.content.decode("utf-8")

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/gallery.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None) == "sum_core/blocks/gallery.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )

        soup = BeautifulSoup(content, "html.parser")
        images_rendered = soup.find_all("img")
        assert len(images_rendered) >= 1
        assert "Tranquil Courtyard" in content

        fallback_image = soup.find("img", alt="Gallery Image Two")
        assert fallback_image is not None
