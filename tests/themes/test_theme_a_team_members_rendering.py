from io import BytesIO

import pytest
from bs4 import BeautifulSoup
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image as PILImage
from sum_core.blocks.content import TeamMemberBlock
from wagtail.images import get_image_model

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("theme_active_copy")]


@pytest.fixture
def image():
    image_model = get_image_model()
    f = BytesIO()
    img = PILImage.new("RGB", (120, 120), "white")
    img.save(f, "PNG")
    content = f.getvalue()
    return image_model.objects.create(
        title="Test Team Image",
        file=SimpleUploadedFile("test_team.png", content, content_type="image/png"),
    )


def test_team_members_block_contract(image):
    block = TeamMemberBlock()
    block_data = {
        "eyebrow": "Our Team",
        "heading": "<h2>Meet the crew</h2>",
        "members": [
            {
                "photo": image.id,
                "name": "Alex Rivera",
                "role": "Founder",
                "bio": "Builder, strategist, and coffee snob.",
            },
            {
                "photo": image.id,
                "name": "Morgan Lee",
                "role": "Design Lead",
                "bio": "Design systems and playful prototyping.",
            },
        ],
    }

    html = block.render(block.to_python(block_data))
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None

    heading = soup.find(attrs={"data-team-heading": True})
    assert heading is not None or section.get("aria-label")

    grid = soup.find(attrs={"data-team-grid": True})
    assert grid is not None

    cards = soup.find_all(attrs={"data-team-member": True})
    assert len(cards) == 2
    assert cards[0].find("img") is not None
