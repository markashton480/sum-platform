import pytest
from django.test import Client
from home.models import HomePage

pytestmark = pytest.mark.django_db


def test_homepage_renders_testimonials_block(wagtail_default_site):
    site = wagtail_default_site
    root = site.root_page

    # Create homepage
    home = HomePage(title="Home Test", slug="home-test-testimonials")
    root.add_child(instance=home)

    # Assign testimonials block data
    home.body = [
        (
            "testimonials",
            {
                "eyebrow": "Testimonials",
                "heading": "<p>Client Vibes</p>",
                "testimonials": [
                    {
                        "quote": "Amazing work!",
                        "author_name": "Alice Smith",
                        "rating": 5,
                    },
                    {"quote": "Pretty good.", "author_name": "Bob Jones", "rating": 4},
                ],
            },
        )
    ]
    home.save_revision().publish()

    # Function based rendering check via client
    client = Client()
    assert home.url is not None
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()

    # Check layout classes
    assert "bg-sage-darkmoss" in content
    assert "grid grid-cols-1" in content

    # Check content
    assert "Testimonials" in content
    assert "Client Vibes" in content
    assert "Amazing work!" in content
    assert "Alice Smith" in content

    # Check ratings render
    # There are 2 testimonials, each has 5 star spans. Total 10 star spans.
    assert (
        content.count('aria-hidden="true">★</span>')
        + content.count('aria-hidden="true">☆</span>')
        == 10
    )

    # First one is 5 stars (5 filled)
    # Second one is 4 stars (4 filled)
    # Total filled stars = 9
    assert content.count('aria-hidden="true">★</span>') == 9


def test_homepage_renders_gallery_block(wagtail_default_site):
    """Test that HomePage correctly renders a Gallery block with images."""
    from wagtail.images.models import Image
    from wagtail.images.tests.utils import get_test_image_file

    site = wagtail_default_site
    root = site.root_page

    # Create test images
    image1 = Image.objects.create(title="Project Photo 1", file=get_test_image_file())
    image2 = Image.objects.create(title="Project Photo 2", file=get_test_image_file())
    image3 = Image.objects.create(title="Project Photo 3", file=get_test_image_file())

    # Create homepage
    home = HomePage(title="Home Test Gallery", slug="home-test-gallery")
    root.add_child(instance=home)
    home.save()

    # Assign gallery block data
    # Note: StreamField assignments need actual Image objects, not just PKs
    home.body = [
        (
            "gallery",
            {
                "eyebrow": "Selected Works",
                "heading": "<p>Our Recent <em>Projects</em></p>",
                "intro": "Explore our craftsmanship across London.",
                "images": [
                    {
                        "image": image1,
                        "alt_text": "Custom alt text for image 1",
                        "caption": "Kensington Townhouse",
                    },
                    {
                        "image": image2,
                        "alt_text": "",  # Should fallback to image title
                        "caption": "Surrey Hills Estate",
                    },
                    {
                        "image": image3,
                        "alt_text": "Third project alt",
                        "caption": "",  # No caption
                    },
                ],
            },
        )
    ]
    home.save_revision().publish()

    # Function based rendering check via client
    client = Client()
    assert home.url is not None
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()

    # Check layout classes
    assert "bg-sage-oat" in content
    assert "lg:grid-cols-3" in content

    # Check header content
    assert "Selected Works" in content
    assert "Our Recent" in content
    assert "<em>Projects</em>" in content  # Italic emphasis in heading
    assert "Explore our craftsmanship across London." in content

    # Check correct number of items rendered (3 images)
    assert content.count("<figure") == 3

    # Check alt text behaviour
    # Image 1: custom alt text provided
    assert 'alt="Custom alt text for image 1"' in content
    # Image 2: should fallback to image title
    assert 'alt="Project Photo 2"' in content
    # Image 3: custom alt text
    assert 'alt="Third project alt"' in content

    # Check captions render where provided
    assert "Kensington Townhouse" in content
    assert "Surrey Hills Estate" in content
    # Image 3 has no caption - verify figcaption doesn't appear for it by count
    # We should have exactly 2 figcaptions (for images 1 and 2)
    assert content.count("<figcaption") == 2
