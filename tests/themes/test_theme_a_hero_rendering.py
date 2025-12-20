import shutil
from io import BytesIO
from pathlib import Path

import pytest
from bs4 import BeautifulSoup
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.template import engines
from PIL import Image as PILImage
from sum_core.blocks.hero import HeroImageBlock
from wagtail.images import get_image_model


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


@pytest.fixture(scope="module", autouse=True)
def active_theme_a():
    """Ensure Theme A templates are used."""
    repo_root = Path(__file__).resolve().parents[2]
    source_templates_dir = repo_root / "themes" / "theme_a" / "templates"
    active_templates_dir = Path(settings.THEME_TEMPLATES_DIR)
    active_root_dir = active_templates_dir.parent.parent

    if active_root_dir.exists():
        shutil.rmtree(active_root_dir)

    active_templates_dir.mkdir(parents=True, exist_ok=True)
    if source_templates_dir.exists():
        shutil.copytree(source_templates_dir, active_templates_dir, dirs_exist_ok=True)

    for loader in engines["django"].engine.template_loaders:
        if hasattr(loader, "reset"):
            loader.reset()
    yield
    if active_root_dir.exists():
        shutil.rmtree(active_root_dir)
    for loader in engines["django"].engine.template_loaders:
        if hasattr(loader, "reset"):
            loader.reset()


@pytest.mark.django_db
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
    assert "bg-sage-terra" in primary_btn["class"]

    secondary_btn = soup.find("a", href="http://s.com")
    assert secondary_btn
    classes = " ".join(secondary_btn.get("class", []))
    assert "border-sage-linen/30" in classes
    assert "border" in classes


@pytest.mark.django_db
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
