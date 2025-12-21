from io import BytesIO

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from sum_core.blocks.content import PortfolioBlock
from wagtail.images import get_image_model

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


@pytest.fixture
def image():
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (100, 100), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title="Test Portfolio Image",
        file=SimpleUploadedFile(
            "test_portfolio.png", content, content_type="image/png"
        ),
    )


def test_portfolio_block_tailwind_markers(image):
    """
    Assert that PortfolioBlock renders with the specific Tailwind markers required by THEME-013.
    """
    block = PortfolioBlock()
    block_data = {
        "eyebrow": "Our Work",
        "heading": "<h1>Featured Projects</h1>",
        "items": [
            {
                "image": None,  # Will be mocked/ignored in rendering if we don't use {% image %} or mock it
                "alt_text": "Project 1",
                "title": "Project One",
                "link_url": "https://example.com/1",
            }
        ],
    }

    # To avoid 'NoneType' errors in {% image %}, we use the created fixture.
    block_data["items"][0][
        "image"
    ] = image.id  # StructBlock expects ID for ImageChooserBlock

    # Render via the block's render method to ensure proper handling
    html = block.render(block.to_python(block_data))

    # Section markers
    assert "bg-sage-linen" in html

    # Header markers
    assert "max-w-7xl mx-auto px-6 mb-12 flex justify-between items-end" in html

    # Scroll container markers
    assert "no-scrollbar snap-x snap-mandatory" in html
    assert "overflow-x-auto" in html

    # Card markers
    assert "snap-center" in html
    assert "focus:ring-4 focus:ring-sage-terra" in html

    # Image wrapper markers
    assert "bg-sage-oat mb-6" in html
    assert "!group-hover/card:scale-105" in html

    # Title hover markers
    assert "!group-hover/card:text-sage-terra" in html

    # Metadata grid markers
    assert "text-xs font-display text-sage-black/70" in html

    # Fade overlay
    assert "bg-gradient-to-l from-sage-linen to-transparent" in html


def test_portfolio_metadata_fallback(image):
    """
    Assert that PortfolioBlock metadata falls back correctly.
    """
    block = PortfolioBlock()
    # Case A: has constraint/material/outcome
    block_data_a = {
        "heading": "<h1>Projects</h1>",
        "items": [
            {
                "image": image.id,
                "alt_text": "A",
                "title": "Project A",
                "constraint": "Tight Budget",
                "material": "Oak",
                "outcome": "Success",
                "location": "London",
                "services": "Design",
            }
        ],
    }
    html_a = block.render(block.to_python(block_data_a))
    assert "Tight Budget" in html_a
    assert "Oak" in html_a
    assert "Success" in html_a

    # Case B: lacks all three
    block_data_b = {
        "heading": "<h1>Projects</h1>",
        "items": [
            {
                "image": image.id,
                "alt_text": "B",
                "title": "Project B",
                "location": "Manchester",
                "services": "Build",
            }
        ],
    }
    html_b = block.render(block.to_python(block_data_b))
    assert "Manchester" in html_b
    assert "Build" in html_b


def test_portfolio_view_all_conditional():
    """
    Assert "View All" link rendering logic.
    """
    block = PortfolioBlock()
    # Both present
    data_both = {
        "heading": "<h1>Projects</h1>",
        "view_all_label": "Explore More",
        "view_all_link": "/portfolio/",
        "items": [],
    }
    html_both = block.render(block.to_python(data_both))
    assert "Explore More" in html_both
    assert "/portfolio/" in html_both

    # Missing one
    data_missing = {
        "heading": "<h1>Projects</h1>",
        "view_all_label": "Explore More",
        "items": [],
    }
    html_missing = block.render(block.to_python(data_missing))
    assert "Explore More" not in html_missing
