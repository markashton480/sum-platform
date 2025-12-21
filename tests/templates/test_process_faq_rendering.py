"""
Name: Process & FAQ Template Tests
Path: tests/templates/test_process_faq_rendering.py
Purpose: Integration tests for rendering Process and FAQ blocks on the homepage.
"""

import pytest
from django.test import Client
from home.models import HomePage
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_homepage_renders_process_and_faq_blocks():
    site = Site.objects.get(is_default_site=True)
    root = site.root_page

    # Create homepage
    home = HomePage(title="Home Process FAQ", slug="home-process-faq")
    root.add_child(instance=home)
    home.save()

    # Define process block data
    process_data = {
        "type": "process",
        "value": {
            "eyebrow": "Our Workflow",
            "heading": "<p>How We Work</p>",
            "intro": "<p>Simple 3 step process.</p>",
            "steps": [
                {
                    "title": "Step One",
                    "description": "<p>First do this.</p>",
                    "number": 1,
                },
                {
                    "title": "Step Two",
                    "description": "<p>Then this.</p>",
                },  # Auto number
                {
                    "title": "Step Three",
                    "description": "<p>Finally this.</p>",
                },  # Auto number
            ],
        },
    }

    # Define FAQ block data
    faq_data = {
        "type": "faq",
        "value": {
            "eyebrow": "Help",
            "heading": "<p>Common Questions</p>",
            "items": [
                {"question": "Is this real?", "answer": "<p>Yes it is.</p>"},
                {"question": "Can I return it?", "answer": "<p>No returns.</p>"},
            ],
            "allow_multiple_open": False,
        },
    }

    home.body = [process_data, faq_data]
    home.save()

    # Render
    client = Client()
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode()

    # --- Process Block Checks ---
    assert "bg-sage-linen" in content
    assert "Our Workflow" in content
    assert "How We Work" in content
    assert "lg:grid-cols-12" in content
    assert "border-sage-moss/20" in content

    # Check steps content
    assert "Step One" in content
    assert "First do this." in content
    # Check numbering
    # Step 1 has manual number '1'
    # Step 2 has auto number (index 2)
    # Step 3 has auto number (index 3)
    # In template we check {{ step.number }} or {{ forloop.counter }}
    # We should search for where these numbers appear.
    # But since they are just numbers, it's hard to assert exactly.
    # We can check structure though.

    # --- FAQ Block Checks ---
    assert "data-faq-block" in content
    assert 'data-allow-multiple="false"' in content
    assert "Common Questions" in content
    assert "accordion-item" in content

    # Check questions and answers
    assert "Is this real?" in content
    assert "Yes it is." in content
    assert "Can I return it?" in content

    # Check JSON-LD
    assert '<script type="application/ld+json">' in content
    assert '"@type": "FAQPage"' in content
    assert '"name": "Is this real?"' in content
    assert '"text": "Yes it is."' in content
