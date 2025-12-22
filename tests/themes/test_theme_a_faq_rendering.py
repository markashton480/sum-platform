from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from sum_core.blocks.process_faq import FAQBlock


def _get_classes(tag: Tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


@pytest.mark.django_db
def test_theme_a_faq_structure_and_content():
    block = FAQBlock()
    block_value = {
        "eyebrow": "FAQ",
        "heading": "Common Questions",
        "intro": "Reference: 2025",
        "allow_multiple_open": True,
        "items": [
            {"question": "How long does it take?", "answer": "Typically 8-12 weeks."},
            {"question": "Do you travel?", "answer": "Yes, nationwide."},
        ],
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None
    section_classes = _get_classes(section)
    assert "bg-sage-linen" in section_classes
    assert "py-24" in section_classes
    assert section.get("data-faq-allow-multiple") == "true"

    assert "FAQ" in soup.get_text()
    assert "Common Questions" in soup.get_text()
    assert "Reference: 2025" in soup.get_text()
    assert "How long does it take?" in soup.get_text()
    assert "Typically 8-12 weeks." in soup.get_text()

    items = soup.select("[data-faq-item]")
    assert len(items) == 2

    first_item = items[0]
    first_button = first_item.select_one("[data-faq-trigger]")
    first_content = first_item.select_one("[data-faq-content]")
    assert first_button is not None
    assert first_content is not None
    assert first_button.get("aria-expanded") == "true"
    assert "open" in _get_classes(first_content)
    assert first_content.get("aria-hidden") == "false"

    second_item = items[1]
    second_button = second_item.select_one("[data-faq-trigger]")
    second_content = second_item.select_one("[data-faq-content]")
    assert second_button is not None
    assert second_content is not None
    assert second_button.get("aria-expanded") == "false"
    assert "open" not in _get_classes(second_content)
    assert second_content.get("aria-hidden") == "true"


@pytest.mark.django_db
def test_theme_a_faq_json_ld_and_allow_multiple_flag():
    block = FAQBlock()
    block_value = {
        "heading": "FAQs",
        "items": [
            {"question": "What is included?", "answer": "Full design build."},
            {"question": "Do you customize?", "answer": "Yes, fully bespoke."},
        ],
        "allow_multiple_open": False,
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None
    assert section.get("data-faq-allow-multiple") == "false"
    assert len(soup.select("[data-faq-item]")) == 2

    json_ld = soup.find("script", attrs={"type": "application/ld+json"})
    assert json_ld is not None
    json_ld_text = json_ld.get_text()
    assert "FAQPage" in json_ld_text
    assert "What is included?" in json_ld_text
