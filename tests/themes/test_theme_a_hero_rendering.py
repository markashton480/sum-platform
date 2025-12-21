from io import BytesIO

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from sum_core.blocks.hero import HeroImageBlock
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
        title="Test Hero Image",
        file=SimpleUploadedFile("test_hero.png", content, content_type="image/png"),
    )


def test_theme_a_hero_markers(image):
    """Verify strict wireframe markers in rendered HTML."""
    block = HeroImageBlock()
    value = block.to_python(
        {
            "image": image.id,
            "image_alt": "Hero Alt",
            "headline": "My Headline",
            "subheadline": "My Subhead",
            "overlay_opacity": "medium",
            "ctas": [
                {"label": "Primary", "url": "http://p.com", "style": "primary"},
                {"label": "Secondary", "url": "http://s.com", "style": "secondary"},
            ],
            "status": "Welcome",
        }
    )

    html = block.render(value)
    soup = BeautifulSoup(html, "html.parser")

    container = soup.select_one("div.h-screen")
    assert container, "Missing h-screen container"
    assert "min-h-[700px]" in container["class"]
    assert "bg-sage-black" in container["class"]

    overlay = soup.find("div", class_="bg-black/60")
    assert overlay, "Medium opacity should map to bg-black/60"

    primary_btn = soup.find("a", string=lambda t: "Primary" in str(t))
    assert primary_btn
    assert "btn-primary" in primary_btn["class"]

    secondary_btn = soup.find("a", href="http://s.com")
    assert secondary_btn
    classes = " ".join(secondary_btn.get("class", []))
    assert "btn-outline-inverse" in classes


@pytest.mark.parametrize(
    "opacity_val, expected_class",
    [
        ("none", "bg-black/0"),
        ("light", "bg-black/30"),
        ("medium", "bg-black/60"),
        ("strong", "bg-black/75"),
    ],
)
def test_theme_a_hero_overlay_mapping(image, opacity_val, expected_class):
    block = HeroImageBlock()
    value = block.to_python(
        {
            "image": image.id,
            "image_alt": "Alt",
            "headline": "Head",
            "overlay_opacity": opacity_val,
        }
    )

    html = block.render(value)
    soup = BeautifulSoup(html, "html.parser")

    found = soup.find("div", class_=expected_class)
    assert found, f"Opacity '{opacity_val}' did not yield class '{expected_class}'"


@pytest.mark.django_db
def test_theme_a_floating_card_logic(image):
    block = HeroImageBlock()

    val1 = block.to_python(
        {
            "image": image.id,
            "image_alt": "Alt",
            "headline": "H",
            "floating_card_label": "Savings",
            "floating_card_value": "",
        }
    )
    html1 = block.render(val1)
    assert "Savings" not in html1

    val2 = block.to_python(
        {
            "image": image.id,
            "image_alt": "Alt",
            "headline": "H",
            "floating_card_label": "",
            "floating_card_value": "£500",
        }
    )
    html2 = block.render(val2)
    assert "£500" not in html2

    val3 = block.to_python(
        {
            "image": image.id,
            "image_alt": "Alt",
            "headline": "H",
            "floating_card_label": "Savings",
            "floating_card_value": "£900",
        }
    )
    html3 = block.render(val3)
    assert "Savings" in html3
    assert "£900" in html3
    assert "backdrop-blur-md" in html3
