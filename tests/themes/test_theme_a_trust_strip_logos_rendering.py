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
    return [str(classes)]


@pytest.fixture
def logo_image():
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (240, 120), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title="Trust Logo",
        file=SimpleUploadedFile("trust-logo.png", content, content_type="image/png"),
    )


def _build_page_with_trust_strip(slug: str, logo):
    from sum_core.pages.models import StandardPage

    root = Page.get_first_root_node()
    homepage = HomePage(title="Theme Test Home", slug=f"theme-home-{slug}")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()
    Site.clear_site_root_paths_cache()

    standard = StandardPage(title="Trust Strip Test", slug=slug)
    standard.body = [
        (
            "trust_strip_logos",
            {
                "eyebrow": "Trusted by custodians",
                "items": [
                    {
                        "logo": logo,
                        "alt_text": "Guild Certification",
                        "url": "https://example.com/guild",
                    },
                    {
                        "logo": logo,
                        "alt_text": "Craft Weekly",
                    },
                ],
            },
        )
    ]
    homepage.add_child(instance=standard)
    standard.save_revision().publish()
    return standard


def test_trust_strip_uses_theme_a_override(
    client: Client, theme_active_copy, logo_image
) -> None:
    page = _build_page_with_trust_strip("trust-strip-theme-a", logo_image)
    response = client.get(page.url)
    content = response.content.decode("utf-8")

    templates = getattr(response, "templates", [])
    template_names = [t.name for t in templates if hasattr(t, "name")]
    assert "sum_core/blocks/trust_strip_logos.html" in template_names

    origin_paths = [
        str(getattr(template.origin, "name", ""))
        for template in templates
        if getattr(template, "name", None) == "sum_core/blocks/trust_strip_logos.html"
    ]
    expected_fragments = (str(theme_active_copy), "themes/theme_a/templates")
    assert any(
        any(fragment in path for fragment in expected_fragments)
        for path in origin_paths
    )

    soup = BeautifulSoup(content, "html.parser")

    section = soup.find("section", class_="bg-sage-linen")
    assert section is not None

    section_classes = _get_classes(section)
    assert "border-y" in section_classes
    assert "border-sage-black/5" in section_classes
    assert "py-12" in section_classes

    assert "Trusted by custodians" in section.get_text()

    logo_rows = [
        tag
        for tag in section.find_all("div")
        if "flex" in _get_classes(tag) and "flex-wrap" in _get_classes(tag)
    ]
    assert logo_rows
    logo_row = logo_rows[0]

    logos = logo_row.find_all("img")
    assert len(logos) == 2
    assert any(img.get("alt") == "Guild Certification" for img in logos)

    linked_logo = logo_row.find("a", href="https://example.com/guild")
    assert linked_logo is not None
    assert "focus-visible:ring-2" in _get_classes(linked_logo)

    unlinked_logos = [
        img
        for img in logos
        if getattr(img.parent, "name", None) != "a" and img.get("alt")
    ]
    assert unlinked_logos, "Expected at least one unlinked logo in the strip"
