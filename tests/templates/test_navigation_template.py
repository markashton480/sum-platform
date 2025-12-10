"""
Name: Navigation Template Tests
Path: tests/templates/test_navigation_template.py
Purpose: Validate navigation template renders with correct CSS classes and active states.
Family: Template/layout test suite.
Dependencies: Django templates, Wagtail Site & Page models, home.HomePage.
"""

from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from wagtail.models import Page, Site

from home.models import HomePage

pytestmark = pytest.mark.django_db


def test_navigation_template_renders_with_correct_classes() -> None:
    """Test that the navigation template renders with the expected CSS classes."""
    # Create and set up homepage
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home-nav")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    # Render the homepage using template like other tests
    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    # Assert navigation classes are present
    assert "site-nav__list" in rendered
    assert "site-nav__link" in rendered
    assert "site-nav__link--active" in rendered

    # Assert the home link has the active class
    assert 'href="/" class="site-nav__link site-nav__link--active"' in rendered
