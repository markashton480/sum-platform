"""
Name: Standard Page Rendering Tests
Path: tests/templates/test_standard_page_rendering.py
Purpose: Validate StandardPage template rendering with various blocks.
Family: Part of the template test suite exercising page rendering.
Dependencies: Django test client, Wagtail models, sum_core.pages.StandardPage.
"""

from __future__ import annotations

import pytest
from django.test import Client
from sum_core.pages import StandardPage
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_standard_page_renders_successfully() -> None:
    """StandardPage renders with HTTP 200 status."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Test Render Page", slug="test-render-page")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)

    assert response.status_code == 200


def test_standard_page_renders_page_title_when_no_hero() -> None:
    """StandardPage renders page title in header when no hero block present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="About Us", slug="about-us-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Title should appear in page header
    assert "About Us" in content
    # Should have heading-xl class for title
    assert "heading-xl" in content
    # Should have section header pattern
    assert "section__header" in content
    assert "section__heading" in content


def test_standard_page_hides_header_when_hero_present() -> None:
    """StandardPage does not render page header when hero block is present."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Landing Page", slug="landing-test")
    root.add_child(instance=page)

    # Add hero gradient block
    page.body = [
        (
            "hero_gradient",
            {
                "headline": "<p>Welcome to Our Site</p>",
                "subheadline": "Subhead text",
                "ctas": [],
                "status": "",
                "gradient_style": "primary",
            },
        )
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content should appear
    assert "Welcome to Our Site" in content
    # Page title should NOT appear as separate header when hero exists
    # The page header section with heading-xl and section__header should not wrap title
    # (it will still be in <title> tag, but not in the body header)
    assert '<h1 class="heading-xl">Landing Page</h1>' not in content


def test_standard_page_renders_rich_text_block() -> None:
    """StandardPage renders rich_text block content."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Content Page", slug="content-page-test")
    root.add_child(instance=page)

    page.body = [
        ("rich_text", "<h2>Our Mission</h2><p>We are committed to excellence.</p>")
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Our Mission" in content
    assert "We are committed to excellence." in content


def test_standard_page_renders_hero_and_content_blocks() -> None:
    """StandardPage renders both hero and content blocks correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page
    image = Image.objects.create(title="Hero Bg", file=get_test_image_file())

    page = StandardPage(title="Full Page", slug="full-page-test")
    root.add_child(instance=page)

    page.body = [
        (
            "hero_image",
            {
                "headline": "<p>Welcome to <em>Our Services</em></p>",
                "subheadline": "Quality solutions for your needs",
                "ctas": [],
                "status": "",
                "image": image,
                "image_alt": "Hero background image",
                "overlay_opacity": "medium",
                "floating_card_label": "",
                "floating_card_value": "",
            },
        ),
        ("rich_text", "<h2>About Our Company</h2><p>Founded in 2020.</p>"),
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Hero content
    assert "Welcome to" in content
    assert "Our Services" in content
    assert "Quality solutions" in content
    # Content block
    assert "About Our Company" in content
    assert "Founded in 2020" in content


def test_standard_page_renders_service_cards_block() -> None:
    """StandardPage renders ServiceCardsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Services", slug="services-test")
    root.add_child(instance=page)

    page.body = [
        (
            "service_cards",
            {
                "eyebrow": "What We Do",
                "heading": "<p>Our <em>Services</em></p>",
                "intro": "Professional solutions for every need.",
                "cards": [
                    {
                        "title": "Consulting",
                        "description": "<p>Expert advice for your business.</p>",
                    },
                    {
                        "title": "Development",
                        "description": "<p>Building solutions that scale.</p>",
                    },
                ],
                "layout_style": "default",
            },
        )
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "What We Do" in content
    assert "Our" in content
    assert "Services" in content
    assert "Consulting" in content
    assert "Development" in content
    assert "services__grid" in content
    assert "services__card" in content


def test_standard_page_renders_testimonials_block() -> None:
    """StandardPage renders TestimonialsBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Reviews", slug="reviews-test")
    root.add_child(instance=page)

    page.body = [
        (
            "testimonials",
            {
                "eyebrow": "Customer Stories",
                "heading": "<p>What People <em>Say</em></p>",
                "testimonials": [
                    {
                        "quote": "Excellent service and great results!",
                        "author_name": "Jane Doe",
                        "company": "Acme Inc",
                        "rating": 5,
                    },
                    {
                        "quote": "Highly recommend to everyone.",
                        "author_name": "John Smith",
                        "rating": 4,
                    },
                ],
            },
        )
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Customer Stories" in content
    assert "What People" in content
    assert "Excellent service" in content
    assert "Jane Doe" in content
    assert "testimonials__grid" in content
    assert "testimonial-card" in content


def test_standard_page_renders_faq_block() -> None:
    """StandardPage renders FAQBlock correctly."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="FAQ", slug="faq-test")
    root.add_child(instance=page)

    page.body = [
        (
            "faq",
            {
                "eyebrow": "Questions",
                "heading": "<p>Frequently Asked</p>",
                "intro": "",
                "items": [
                    {
                        "question": "What is your return policy?",
                        "answer": "<p>We offer 30-day returns.</p>",
                    },
                    {
                        "question": "How do I contact support?",
                        "answer": "<p>Email us at support@example.com.</p>",
                    },
                ],
                "allow_multiple_open": True,
            },
        )
    ]
    page.save()

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    assert "Questions" in content
    assert "Frequently Asked" in content
    assert "What is your return policy?" in content
    assert "30-day returns" in content
    assert "faq-item" in content


def test_standard_page_no_inline_styles() -> None:
    """StandardPage template contains no inline styles."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Style Test", slug="style-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    # Check there are no style attributes with hardcoded values
    # (Note: some Wagtail image renditions may include width/height, which is OK)
    # We specifically check for no color or px values in style attributes
    assert 'style="color:' not in content
    assert 'style="font-size:' not in content
    assert 'style="margin:' not in content
    assert 'style="padding:' not in content


def test_standard_page_uses_layout_classes() -> None:
    """StandardPage renders with proper layout classes from CSS system."""
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    page = StandardPage(title="Layout Test", slug="layout-test")
    root.add_child(instance=page)

    client = Client()
    response = client.get(page.url)
    content = response.content.decode()

    assert response.status_code == 200
    # Main layout elements from base template
    assert "<main>" in content or "<main id=" in content
    assert "<header" in content
    assert "<footer" in content
    # Container class for proper width constraints
    assert "container" in content
    # Section class for proper spacing
    assert "section" in content
