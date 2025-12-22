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

    item = soup.select_one("[data-faq-item]")
    assert item is not None
    assert item.select_one("[data-faq-trigger]") is not None
    assert item.select_one("[data-faq-content]") is not None


@pytest.mark.django_db
def test_theme_a_faq_json_ld_and_allow_multiple_flag():
    block = FAQBlock()
    block_value = {
        "heading": "FAQs",
        "items": [{"question": "What is included?", "answer": "Full design build."}],
        "allow_multiple_open": False,
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None
    assert section.get("data-faq-allow-multiple") == "false"

    json_ld = soup.find("script", attrs={"type": "application/ld+json"})
    assert json_ld is not None
    json_ld_text = json_ld.get_text()
    assert "FAQPage" in json_ld_text
    assert "What is included?" in json_ld_text
