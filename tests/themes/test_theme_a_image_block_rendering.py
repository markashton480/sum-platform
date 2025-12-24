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


def _get_classes(tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


def _create_image():
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (1200, 800), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title="Theme A Image Block",
        file=SimpleUploadedFile(
            "theme_a_image_block.png", content, content_type="image/png"
        ),
    )


def _create_standard_page_with_image(
    slug: str,
    image,
    alt_text: str,
    caption: str,
    full_width: bool,
) -> Page:
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage.objects.first()
    if homepage is None:
        homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
        root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Image Test", slug=slug)
    standard.body = [
        (
            "image_block",
            {
                "image": image,
                "alt_text": alt_text,
                "caption": caption,
                "full_width": full_width,
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


class TestThemeAImageBlock:
    def test_image_block_renders_theme_template_and_alt_text(
        self, client: Client, theme_active_copy
    ) -> None:
        image = _create_image()
        page = _create_standard_page_with_image(
            "image-theme-a",
            image,
            "Stacks of oak timber",
            "Figure A: The Stacking Process",
            False,
        )

        response = client.get(page.url)
        assert response.status_code == 200

        templates = getattr(response, "templates", [])
        template_names = [t.name for t in templates if hasattr(t, "name")]
        assert "sum_core/blocks/content_image.html" in template_names

        origin_paths = [
            str(getattr(template.origin, "name", ""))
            for template in templates
            if getattr(template, "name", None) == "sum_core/blocks/content_image.html"
        ]
        expected_fragments = (
            str(theme_active_copy),
            "themes/theme_a/templates",
        )
        assert any(
            any(fragment in path for fragment in expected_fragments)
            for path in origin_paths
        )

        soup = BeautifulSoup(response.content.decode("utf-8"), "html.parser")
        img = soup.find("img", alt="Stacks of oak timber")
        assert img is not None
        section = soup.find(
            "section",
            class_=lambda value: value and "section" in str(value).split(),
        )
        assert section is not None
        assert "reveal" in response.content.decode("utf-8")

    def test_caption_is_optional(self, client: Client) -> None:
        image = _create_image()
        with_caption = _create_standard_page_with_image(
            "image-theme-a-caption",
            image,
            "Workshop bench",
            "Captioned image",
            False,
        )
        without_caption = _create_standard_page_with_image(
            "image-theme-a-no-caption",
            image,
            "Workshop bench",
            "",
            False,
        )

        with_response = client.get(with_caption.url)
        with_soup = BeautifulSoup(with_response.content.decode("utf-8"), "html.parser")
        with_figcaption = with_soup.find("figcaption")
        assert with_figcaption is not None
        assert "Captioned image" in with_figcaption.get_text()

        without_response = client.get(without_caption.url)
        without_soup = BeautifulSoup(
            without_response.content.decode("utf-8"), "html.parser"
        )
        assert without_soup.find("figcaption") is None

    def test_full_width_class_toggle(self, client: Client) -> None:
        image = _create_image()
        narrow_page = _create_standard_page_with_image(
            "image-theme-a-narrow",
            image,
            "Workshop bench",
            "",
            False,
        )
        wide_page = _create_standard_page_with_image(
            "image-theme-a-wide",
            image,
            "Workshop bench",
            "",
            True,
        )

        narrow_response = client.get(narrow_page.url)
        narrow_soup = BeautifulSoup(
            narrow_response.content.decode("utf-8"), "html.parser"
        )
        narrow_figure = narrow_soup.find("figure")
        assert narrow_figure is not None
        narrow_classes = _get_classes(narrow_figure)
        assert "max-w-3xl" in narrow_classes
        assert "mx-auto" in narrow_classes

        wide_response = client.get(wide_page.url)
        wide_soup = BeautifulSoup(wide_response.content.decode("utf-8"), "html.parser")
        wide_figure = wide_soup.find("figure")
        assert wide_figure is not None
        wide_classes = _get_classes(wide_figure)
        assert "-mx-6" in wide_classes
        assert "md:-mx-12" in wide_classes
        assert "lg:mx-0" in wide_classes
