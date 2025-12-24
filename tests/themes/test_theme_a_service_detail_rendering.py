from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from sum_core.blocks.services import ServiceDetailBlock
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file


def _get_classes(tag: Tag | None) -> list[str]:
    if tag is None:
        return []

    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


@pytest.mark.django_db
def test_service_detail_renders_text_only_variant() -> None:
    block = ServiceDetailBlock()
    block_value = {
        "eyebrow": "Featured service",
        "heading": "<p>Deep energy audit</p>",
        "body": "<p>Measure twice. Integrate once.</p>",
        "highlights": ["Blower door testing", "Infrared mapping"],
        "layout": "no_image",
        "cta_text": "Book a consult",
        "cta_url": "https://example.com/consult",
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None
    assert "Featured service" in section.get_text()
    assert "Deep energy audit" in section.get_text()
    assert "Book a consult" in section.get_text()
    assert not section.find("img"), "No image should render for text-only layout"

    highlights = section.find_all("li")
    assert len(highlights) == 2
    assert "Blower door testing" in highlights[0].get_text()


@pytest.mark.django_db
def test_service_detail_respects_image_alignment_and_alt_text() -> None:
    image = Image.objects.create(title="Service Detail", file=get_test_image_file())

    block = ServiceDetailBlock()
    block_value = {
        "heading": "<p>Design-build</p>",
        "body": "<p>Full stack delivery.</p>",
        "image": image,
        "image_alt": "Staged fabrication",
        "layout": "image_right",
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    content_wrapper = soup.find(
        "div", class_=lambda value: value and "space-y-6" in str(value)
    )
    assert content_wrapper is not None
    assert "lg:order-1" in _get_classes(content_wrapper)

    media = soup.find(
        "div", class_=lambda value: value and "overflow-hidden" in str(value)
    )
    assert media is not None
    media_wrapper_classes = _get_classes(media.parent)
    assert "lg:order-2" in media_wrapper_classes

    img = media.find("img")
    assert img is not None
    assert img.get("alt") == "Staged fabrication"
