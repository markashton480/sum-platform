from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from sum_core.blocks.services import ServiceCardsBlock


def _get_classes(tag: Tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


@pytest.mark.django_db
def test_service_cards_theme_structure():
    """
    Test that the ServiceCardsBlock renders with the Theme A overrides.
    """
    block = ServiceCardsBlock()
    # Create block data with 3 items (Featured + 2 Standard)
    block_value = {
        "heading": "Our Services",
        "cards": [
            {
                "title": "Featured Service",
                "description": "The big one",
                "link_url": "http://example.com",
            },
            {
                "title": "Standard 1",
                "description": "Standard service",
            },
            {
                "title": "Standard 2",
                "description": "Standard service",
            },
        ],
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    # 1. Assert Section Wrapper
    section = soup.find("section")
    assert section is not None
    section_classes = str(section.get("class"))
    assert "bg-sage-oat/30" in section_classes
    assert "py-20" in section_classes

    # 2. Assert Header logic
    assert "Our Services" in soup.get_text()

    # 3. Assert Grid
    grid = soup.find(class_="grid")
    assert grid is not None
    grid_classes = str(grid.get("class"))
    assert "grid-cols-1" in grid_classes
    assert "md:grid-cols-3" in grid_classes

    # 4. Assert Cards
    # In my template, cards are direct children of the grid
    cards = grid.find_all("div", recursive=False)
    # The grid might contain other things like the 'view all' link if I put it there?
    # No, view all link is outside the grid in my template.
    # However, I should check the length.
    assert len(cards) == 3

    # 5. Check Featured Card (First)
    featured_card = cards[0]
    featured_classes = str(featured_card.get("class"))
    assert "md:col-span-2" in featured_classes
    assert "Featured Service" in featured_card.get_text()

    # 6. Check Standard Card (Second)
    standard_card = cards[1]
    standard_classes = str(standard_card.get("class"))
    assert "md:col-span-2" not in standard_classes
    # Check for border logic (not last, so should have right border)
    # Actually my template has: {% if not forloop.last %}md:border-r{% endif %}
    assert "md:border-r" in standard_classes
    assert "Standard 1" in standard_card.get_text()


@pytest.mark.django_db
def test_service_cards_content_logic():
    """
    Test link labels, image vs icon, etc.
    """
    block = ServiceCardsBlock()
    block_value = {
        "heading": "Services",
        "cards": [
            {
                "title": "Featured",
                "link_url": "http://example.com/featured",
                # No label, should default
            },
            {
                "title": "Icon Card",
                "icon": "🎨",
                "link_url": "http://example.com/icon",
                "link_label": "Go there",
            },
        ],
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")
    grid = soup.find(class_="grid")
    assert grid is not None
    cards = grid.find_all("div", recursive=False)

    # Featured Card Defaults
    featured = cards[0]
    # Check default link label for featured
    # Template: {{ card.link_label|default:"Explore Process" }}
    assert "Explore Process" in featured.get_text()

    # Standard Card with Icon
    standard = cards[1]
    # Check custom link label
    assert "Go there" in standard.get_text()
    # Check icon
    assert "🎨" in standard.get_text()
