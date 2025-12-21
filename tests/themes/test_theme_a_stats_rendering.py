import pytest
from bs4 import BeautifulSoup
from sum_core.blocks.trust import StatsBlock


@pytest.mark.django_db
def test_stats_block_structure():
    """
    Test that the StatsBlock renders with the correct reference structure and classes.
    """
    block = StatsBlock()
    # Create block data with 4 items
    block_value = {
        "eyebrow": "Key Metrics",
        "items": [
            {"label": "Metric 1", "value": "100"},
            {"label": "Metric 2", "value": "200"},
            {"label": "Metric 3", "value": "300"},
            {"label": "Metric 4", "value": "400"},
        ],
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    # Assert outer wrapper classes (Operational Proof Strip reference)
    # Assert outer wrapper classes (Operational Proof Strip reference)
    # Note: The template might use section or div, the plan specified replacing root section classes.
    # We'll check for the class presence on any container if the specific tag check fails,
    # but based on plan we expect a root element with these classes.

    root = soup.find(class_="bg-sage-linen")
    assert root is not None
    assert "border-b" in root.get("class", [])
    assert "border-sage-black/5" in root.get("class", [])
    assert "py-12" in root.get("class", [])

    # Assert inner grid container
    grid = soup.find(class_="grid")
    assert grid is not None
    classes = grid.get("class", [])
    assert "grid-cols-2" in classes
    assert "md:grid-cols-4" in classes
    assert "gap-8" in classes
    assert "text-center" in classes

    # Assert 4 items rendered
    items = grid.find_all("div", recursive=False)
    assert len(items) == 4


@pytest.mark.django_db
def test_stats_value_composition():
    """
    Test that stats values are correctly composed with prefix and suffix.
    """
    block = StatsBlock()
    block_value = {
        "items": [{"label": "Revenue", "value": "50", "prefix": "£", "suffix": "M"}]
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    # Find the value element.
    # Plan: Value: `block font-display text-xl text-sage-black` containing `{{ prefix }}{{ value }}{{ suffix }}`
    value_el = soup.find(class_="block font-display text-xl text-sage-black")
    assert value_el is not None

    # Verify exact text content concatenation
    # Depending on implementation, there might be whitespace, but the visual result needs to key components
    text = value_el.get_text(strip=True)
    assert "£50M" in text

    # Check label
    label_el = soup.find(class_="text-sage-terra")
    assert label_el is not None
    assert "REVENUE" in label_el.get_text(strip=True).upper()


@pytest.mark.django_db
def test_stats_optional_content():
    """
    Test rendering of optional eyebrow and intro fields.
    """
    block = StatsBlock()
    block_value = {
        "eyebrow": "Performance",
        "intro": "A summary of our success.",
        "items": [{"label": "A", "value": "1"}],
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    # Eyebrow check
    assert "Performance" in soup.get_text()

    # Intro check
    assert "A summary of our success." in soup.get_text()

    # Render without them
    minimal_value = {"items": [{"label": "A", "value": "1"}]}
    html_min = block.render(minimal_value)
    soup_min = BeautifulSoup(html_min, "html.parser")

    # Should not find the eyebrow text logic (unless defaults exist, which they shouldn't)
    assert "Performance" not in soup_min.get_text()
