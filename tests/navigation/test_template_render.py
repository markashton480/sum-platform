"""
Name: Navigation Template Render Integration Tests
Path: tests/navigation/test_template_render.py
Purpose: Smoke tests that verify navigation templates render without exception.
Family: Navigation test suite - integration coverage.
Dependencies: Django templates, Wagtail, sum_core.navigation template tags.
"""

from __future__ import annotations

import pytest
from django.core.cache import cache
from django.template import Template
from django.template.loader import render_to_string
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test to prevent flakiness."""
    cache.clear()
    yield
    cache.clear()


class TestNavigationTemplateRender:
    """Integration tests that verify templates render without errors."""

    def test_header_template_renders_without_exception(self):
        """Render header.html include and verify it contains expected landmarks."""
        site = Site.objects.get(is_default_site=True)

        # Ensure navigation settings exist
        header_nav = HeaderNavigation.for_site(site)
        header_nav.save()

        # Set up branding
        settings = SiteSettings.for_site(site)
        settings.company_name = "Test Company"
        settings.save()

        # Create a request context
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render the header template directly using loader
        context = {"request": request}
        rendered = render_to_string(
            "sum_core/includes/header.html",
            context=context,
            request=request,
        )

        # Basic smoke assertions - should render without exception
        assert "<header" in rendered
        assert "nav" in rendered.lower()
        # Should have main navigation landmark
        assert 'aria-label="Main navigation"' in rendered

    def test_footer_template_renders_without_exception(self):
        """Render footer.html include and verify it contains expected landmarks."""
        site = Site.objects.get(is_default_site=True)

        # Ensure navigation settings exist
        footer_nav = FooterNavigation.for_site(site)
        footer_nav.save()

        # Set up branding
        settings = SiteSettings.for_site(site)
        settings.company_name = "Test Company"
        settings.save()

        # Create a request context
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render the footer template directly using loader
        context = {"request": request}
        rendered = render_to_string(
            "sum_core/includes/footer.html",
            context=context,
            request=request,
        )

        # Basic smoke assertions - should render without exception
        assert "<footer" in rendered
        # Footer typically has a role or semantic element
        assert "footer__" in rendered or "footer" in rendered

    def test_sticky_cta_template_renders_without_exception(self):
        """Render sticky_cta.html include and verify it renders without error."""
        site = Site.objects.get(is_default_site=True)

        # Ensure navigation settings exist with sticky CTA enabled
        header_nav = HeaderNavigation.for_site(site)
        header_nav.mobile_cta_enabled = True
        header_nav.save()

        # Set up branding
        settings = SiteSettings.for_site(site)
        settings.company_name = "Test Company"
        settings.phone_number = "+44 123 456 7890"
        settings.save()

        # Create a request context
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render the sticky CTA template
        context = {"request": request}
        rendered = render_to_string(
            "sum_core/includes/sticky_cta.html",
            context=context,
            request=request,
        )

        # Should render without exception (may be empty if not enabled)
        assert rendered is not None

    def test_base_template_renders_with_navigation(self):
        """Render base.html and verify header+footer are included."""
        site = Site.objects.get(is_default_site=True)
        home_page = Page.objects.filter(depth=2).first()

        # Ensure navigation settings exist
        HeaderNavigation.for_site(site).save()
        FooterNavigation.for_site(site).save()

        # Set up branding
        settings = SiteSettings.for_site(site)
        settings.company_name = "Integration Test Corp"
        settings.save()

        # Create a request context with page
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render base template
        context = {
            "request": request,
            "page": home_page,
            "self": home_page,
        }

        rendered = render_to_string(
            "sum_core/base.html",
            context=context,
            request=request,
        )

        # Should include both header and footer elements
        assert "<header" in rendered
        assert "<footer" in rendered
        # Should include the company name somewhere
        assert "Integration Test Corp" in rendered


class TestNavigationTagInTemplate:
    """Test that navigation template tags work correctly in templates."""

    def test_header_nav_tag_renders_in_template(self):
        """Verify header_nav tag can be used in a custom template."""
        site = Site.objects.get(is_default_site=True)

        # Set up basic header navigation (no menu items)
        header_nav = HeaderNavigation.for_site(site)
        header_nav.show_phone_in_header = True
        header_nav.save()

        # Set up branding with phone
        settings = SiteSettings.for_site(site)
        settings.phone_number = "+44 123 456 7890"
        settings.save()

        # Create a request
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render a simple test template
        template = Template(
            "{% load navigation_tags %}"
            "{% header_nav as nav %}"
            "{% if nav.show_phone %}"
            "<span>{{ nav.phone_number }}</span>"
            "{% endif %}"
        )

        from django.template import RequestContext

        rendered = template.render(RequestContext(request, {}))

        # Should contain the phone number from branding
        assert "+44 123 456 7890" in rendered

    def test_footer_nav_tag_renders_tagline(self):
        """Verify footer_nav tag returns tagline from settings."""
        site = Site.objects.get(is_default_site=True)

        # Set up branding with tagline
        settings = SiteSettings.for_site(site)
        settings.tagline = "Quality Workmanship Since 1990"
        settings.save()

        # Create footer (empty, falls back to branding)
        FooterNavigation.for_site(site).save()

        # Create a request
        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        # Render a simple test template
        template = Template(
            "{% load navigation_tags %}"
            "{% footer_nav as footer %}"
            "{{ footer.tagline }}"
        )

        from django.template import RequestContext

        rendered = template.render(RequestContext(request, {}))

        # Should contain the tagline from branding
        assert "Quality Workmanship Since 1990" in rendered
