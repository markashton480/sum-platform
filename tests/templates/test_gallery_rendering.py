"""
Name: Gallery Template Tests
Path: tests/templates/test_gallery_rendering.py
Purpose: Integration tests for rendering the PortfolioBlock.
"""

import pytest
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTests
from wagtail.images.models import Image
from django.core.files.base import ContentFile
from bs4 import BeautifulSoup

from home.models import HomePage

@pytest.mark.django_db
class TestGalleryRendering(WagtailPageTests):

    def test_gallery_block_rendering(self):
        """Test that the gallery block renders correctly on a HomePage."""
        # 1. Setup - Create a HomePage
        # Ensure root page exists (usually created by migration but good to be safe or just get it)
        # In standard wagtail tests, root page usually exists at id=1 or 2.
        # We can just use Page.get_first_root_node() if unsure, or create a root.
        # But WagtailPageTests often cleans up. Let's assume standard tree.
        root = Page.get_first_root_node()
        # Ensure root exists
        if not root:
             root = Page.objects.create(title="Root", path="0001", depth=1)

        home = HomePage(title="Home", slug="home-gallery-test")
        root.add_child(instance=home)

        # Ensure site points to home
        from wagtail.models import Site
        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            site = Site.objects.create(hostname="localhost", root_page=home, is_default_site=True, port=80)
        else:
            site.root_page = home
            site.save()

        home.save_revision().publish()

        # 2. Setup - Create Image (Minimal valid JPEG)
        minimal_jpeg = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06'
            b'\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a'
            b'\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xdb\x00C\x01\t\t\t'
            b'\x0c\x0b\x0c\x18\r\r\x182!\x1c!22222222222222222222222222222222222222222222222222\xff\xc0'
            b'\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00'
            b'\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07'
            b'\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01'
            b'}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1'
            b'\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84'
            b'\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9'
            b'\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5'
            b'\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8'
            b'\xf9\xfa\xff\xc4\x00\x1f\x01\x00\x03\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
            b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x11\x00\x02\x01\x02\x04\x04\x03'
            b'\x04\x07\x05\x04\x04\x00\x01\x02w\x00\x01\x02\x03\x11\x04\x05!1\x06\x12AQ\x07aq\x13"2\x81\x08'
            b'\x14B\x91\xa1\xb1\xc1\t#3R\xf0\x15br\xd1\n\x16$4\xe1%\xf1\x17\x18\x19\x1a&\'()*56789:CDEFGHIJ'
            b'STUVWXYZcdefghijstuvwxyz\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99'
            b'\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5'
            b'\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea'
            b'\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xf7'
            b'\xfa(\xa2\x80\x3f\xff\xd9'
        )

        image = Image.objects.create(
            title="Test Image",
            file=ContentFile(minimal_jpeg, name="test_image.jpg")
        )

        block_data = [
            {
                "type": "portfolio",
                "value": {
                    "eyebrow": "Our Work",
                    "heading": "<p>Selected <b>Projects</b></p>", # Rich text raw html usually
                    "intro": "Check out our latest installations.",
                    "items": [
                        {
                            "image": image.pk,
                            "alt_text": "Project 1 Alt",
                            "title": "Project One",
                            "location": "London",
                            "services": "Solar",
                            "link_url": "https://example.com/project-1"
                        },
                         {
                            "image": image.pk,
                            "alt_text": "Project 2 Alt",
                            "title": "Project Two",
                            # Optional fields missing
                        }
                    ]
                }
            }
        ]

        home.body = block_data
        home.save_revision().publish()

        # 3. Request
        response = self.client.get(home.url)
        assert response.status_code == 200

        # 4. Assertions
        soup = BeautifulSoup(response.content, "html.parser")

        # Section exists
        section = soup.select_one(".section.gallery")
        assert section is not None

        # Header content
        eyebrow = section.select_one(".section__eyebrow")
        assert eyebrow and "Our Work" in eyebrow.text

        heading = section.select_one(".section__heading")
        assert heading and "Selected Projects" in heading.text

        intro = section.select_one(".section__intro")
        assert intro and "Check out our latest installations." in intro.text

        # Items exist
        items = section.select(".gallery__item")
        assert len(items) == 2

        # First item content
        item1 = items[0]
        assert "Project One" in item1.select_one(".gallery__title").text

        meta = item1.select_one(".gallery__meta")
        assert meta is not None
        assert "London" in meta.text
        assert "Solar" in meta.text

        link = item1.select_one("a.gallery__link")
        assert link is not None
        assert link["href"] == "https://example.com/project-1"

        img = item1.select_one(".gallery__image-wrapper img")
        assert img is not None
        assert img["alt"] == "Project 1 Alt"

        # Second item (minimal)
        item2 = items[1]
        assert "Project Two" in item2.select_one(".gallery__title").text
        assert item2.select_one(".gallery__meta") is None
        assert item2.select_one("a.gallery__link") is None
