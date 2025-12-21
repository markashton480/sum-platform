"""
Name: Navigation Template Wiring Tests
Path: tests/templates/test_navigation_template.py
Purpose: Validate navigation templates render correctly with template tags.
         Tests both empty/fallback states and configured navigation states.
Family: Template/layout test suite.
Dependencies: Django templates, Wagtail Site & Page models, home.HomePage,
              navigation models and template tags.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from django.core.cache import cache
from django.template import RequestContext, Template
from django.test import RequestFactory
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestHeaderWiring:
    """Tests for header.html wiring to navigation template tags."""

    def test_header_renders_with_correct_classes(self) -> None:
        """Test that the header template renders with expected CSS classes."""
        root = Page.get_first_root_node()
        homepage = HomePage(title="Test Home", slug="test-home-nav")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        template = Template(
            "{% extends 'theme/home_page.html' %}"
            "{% block content %}<p>Content</p>{% endblock %}"
        )
        rendered = template.render(RequestContext(request, {"page": homepage}))

        # Core structure
        assert "header" in rendered
        assert "nav-link" in rendered
        assert "mobile-menu-btn" in rendered
        assert "top-stack" in rendered
        assert 'href="/"' in rendered

    def test_header_renders_menu_items_from_settings(self) -> None:
        """Test that header renders menu items from HeaderNavigation settings."""
        site = Site.objects.get(is_default_site=True)

        # Set up navigation with menu items
        nav = HeaderNavigation.for_site(site)
        nav.menu_items = [
            {
                "type": "item",
                "value": {
                    "label": "About",
                    "link": {
                        "link_type": "url",
                        "url": "/about/",
                    },
                    "children": [],
                },
            },
            {
                "type": "item",
                "value": {
                    "label": "Services",
                    "link": {
                        "link_type": "url",
                        "url": "/services/",
                    },
                    "children": [],
                },
            },
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        header_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'theme/includes/header.html' %}"
        ).render(context)

        assert "About" in header_html
        assert 'href="/about/"' in header_html
        assert "Services" in header_html
        assert 'href="/services/"' in header_html

    def test_header_renders_mobile_drawer_and_button_wiring(self) -> None:
        """Test that header includes the mobile drawer and menu button controls it."""
        site = Site.objects.get(is_default_site=True)

        # Ensure navigation settings exist
        HeaderNavigation.for_site(site).save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        header_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'theme/includes/header.html' %}"
        ).render(context)

        assert 'id="mobile-menu-btn"' in header_html
        assert 'aria-controls="mobile-menu"' in header_html
        assert 'id="mobile-menu"' in header_html

    def test_header_renders_nested_mobile_menu_groups(self) -> None:
        """Items with children render as nested mobile groups in the drawer."""
        site = Site.objects.get(is_default_site=True)

        nav = HeaderNavigation.for_site(site)
        nav.menu_items = [
            {
                "type": "item",
                "value": {
                    "label": "Expertise",
                    "link": {
                        "link_type": "url",
                        "url": "/expertise/",
                    },
                    "children": [
                        {
                            "label": "Solar Integration",
                            "link": {
                                "link_type": "url",
                                "url": "/expertise/solar/",
                            },
                            "children": [
                                {
                                    "label": "Roof Integrated",
                                    "link": {
                                        "link_type": "url",
                                        "url": "/expertise/solar/roof/",
                                    },
                                }
                            ],
                        },
                        {
                            "label": "Battery Storage",
                            "link": {
                                "link_type": "url",
                                "url": "/expertise/battery/",
                            },
                            "children": [],
                        },
                    ],
                },
            }
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        header_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'theme/includes/header.html' %}"
        ).render(context)

        assert 'data-menu-level="1"' in header_html
        assert 'data-menu-level="0"' in header_html
        assert "Solar Integration" in header_html
        assert "Battery Storage" in header_html

    def test_header_renders_cta_button(self) -> None:
        """Test that header renders CTA button when configured."""
        site = Site.objects.get(is_default_site=True)

        nav = HeaderNavigation.for_site(site)
        nav.header_cta_enabled = True
        nav.header_cta_text = "Get Quote"
        nav.header_cta_link = [
            {
                "type": "link",
                "value": {
                    "link_type": "url",
                    "url": "/contact/",
                },
            }
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        header_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'theme/includes/header.html' %}"
        ).render(context)

        assert "Get Quote" in header_html
        assert 'href="/contact/"' in header_html
        assert "btn-header" in header_html

    def test_header_renders_fallback_when_no_menu_items(self) -> None:
        """Test that header shows fallback Home link when no menu items configured."""
        site = Site.objects.get(is_default_site=True)

        # Ensure no menu items configured
        nav = HeaderNavigation.for_site(site)
        nav.menu_items = []
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        header_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'theme/includes/header.html' %}"
        ).render(context)

        # Fallback should show Home link
        assert 'href="/"' in header_html
        assert "Home" in header_html


def test_header_css_does_not_underline_active_nav_items() -> None:
    """
    Regression test: active/current nav items should not get a persistent underline.

    The design reference uses an underline on hover only, not for `.is-active` or
    `aria-current="page"` states.
    """
    css_path = Path("core/sum_core/static/sum_core/css/components.header.css")
    css = css_path.read_text(encoding="utf-8")

    assert ".nav-item.is-active::after" not in css
    assert '.nav-item[aria-current="page"]::after' not in css


class TestFooterWiring:
    """Tests for footer.html wiring to navigation template tags."""

    def test_footer_renders_tagline_from_branding(self) -> None:
        """Test that footer shows tagline from SiteSettings when nav not overridden."""
        site = Site.objects.get(is_default_site=True)

        settings = SiteSettings.for_site(site)
        settings.company_name = "Footer Test Co"
        settings.tagline = "Quality you can trust"
        settings.save()

        # Ensure navigation has no overrides
        nav = FooterNavigation.for_site(site)
        nav.tagline = ""
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        footer_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'sum_core/includes/footer.html' %}"
        ).render(context)

        assert "Footer Test Co" in footer_html
        assert "Quality you can trust" in footer_html

    def test_footer_renders_link_sections(self) -> None:
        """Test that footer renders link sections from FooterNavigation."""
        site = Site.objects.get(is_default_site=True)

        nav = FooterNavigation.for_site(site)
        # Note: For ListBlock items, we don't wrap in {type, value} - just pass direct value dicts
        nav.link_sections = [
            {
                "type": "section",
                "value": {
                    "title": "Company",
                    "links": [
                        {
                            "link_type": "url",
                            "url": "https://example.com/about/",
                            "link_text": "About Us",
                        },
                        {
                            "link_type": "url",
                            "url": "https://example.com/team/",
                            "link_text": "Our Team",
                        },
                    ],
                },
            },
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        footer_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'sum_core/includes/footer.html' %}"
        ).render(context)

        assert "Company" in footer_html
        assert "About Us" in footer_html
        assert 'href="https://example.com/about/"' in footer_html
        assert "Our Team" in footer_html
        assert 'href="https://example.com/team/"' in footer_html

    def test_footer_renders_business_info_fallback(self) -> None:
        """Test that footer shows business info from SiteSettings as fallback."""
        site = Site.objects.get(is_default_site=True)

        settings = SiteSettings.for_site(site)
        settings.phone_number = "01onal234 567890"
        settings.email = "contact@example.com"
        settings.address = "123 Main St\nTestville"
        settings.save()

        # No link sections configured, so contact fallback should show
        nav = FooterNavigation.for_site(site)
        nav.link_sections = []
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        footer_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'sum_core/includes/footer.html' %}"
        ).render(context)

        # Should have contact info in fallback section
        assert "contact@example.com" in footer_html

    def test_footer_renders_copyright(self) -> None:
        """Test that footer renders copyright text with placeholders resolved."""
        site = Site.objects.get(is_default_site=True)

        settings = SiteSettings.for_site(site)
        settings.company_name = "Test Company"
        settings.save()

        nav = FooterNavigation.for_site(site)
        nav.copyright_text = "© {year} {company_name}. All rights reserved."
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        footer_html = Template(
            "{% load branding_tags navigation_tags %}"
            "{% include 'sum_core/includes/footer.html' %}"
        ).render(context)

        # Year should be replaced (2025 in test context)
        assert "2025" in footer_html or "202" in footer_html  # Allow for year change
        assert "Test Company" in footer_html
        assert "All rights reserved" in footer_html


class TestStickyCTAWiring:
    """Tests for sticky_cta.html wiring to navigation template tags."""

    def test_sticky_cta_hidden_when_disabled(self) -> None:
        """Test that sticky CTA is not rendered when disabled."""
        site = Site.objects.get(is_default_site=True)

        nav = HeaderNavigation.for_site(site)
        nav.mobile_cta_enabled = False
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        html = Template(
            "{% load navigation_tags %}"
            "{% include 'sum_core/includes/sticky_cta.html' %}"
        ).render(context)

        assert "sticky-cta" not in html

    def test_sticky_cta_renders_when_enabled(self) -> None:
        """Test that sticky CTA renders with button when enabled."""
        site = Site.objects.get(is_default_site=True)

        settings = SiteSettings.for_site(site)
        settings.phone_number = "01onal234 567890"
        settings.save()

        nav = HeaderNavigation.for_site(site)
        nav.mobile_cta_enabled = True
        nav.mobile_cta_show_phone = True
        nav.mobile_cta_show_button = True
        nav.mobile_cta_button_text = "Get Started"
        nav.mobile_cta_button_link = [
            {
                "type": "link",
                "value": {
                    "link_type": "url",
                    "url": "/start/",
                },
            }
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
        context = RequestContext(request, {})

        html = Template(
            "{% load navigation_tags %}"
            "{% include 'sum_core/includes/sticky_cta.html' %}"
        ).render(context)

        assert "sticky-cta" in html
        assert "Get Started" in html
        assert 'href="/start/"' in html


class TestBaseTemplateIntegration:
    """Tests for base.html integration with navigation includes."""

    def test_base_template_includes_sticky_cta(self) -> None:
        """Test that base.html includes the sticky CTA template."""
        site = Site.objects.get(is_default_site=True)

        nav = HeaderNavigation.for_site(site)
        nav.mobile_cta_enabled = True
        nav.mobile_cta_show_button = True
        nav.mobile_cta_button_text = "Book Now"
        nav.mobile_cta_button_link = [
            {
                "type": "link",
                "value": {
                    "link_type": "url",
                    "url": "/book/",
                },
            }
        ]
        nav.save()

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        template = Template(
            "{% extends 'sum_core/base.html' %}"
            "{% block content %}Test content{% endblock %}"
        )
        rendered = template.render(RequestContext(request, {}))

        # Sticky CTA should be present
        assert "sticky-cta" in rendered
        assert "Book Now" in rendered

    def test_base_template_loads_navigation_js(self) -> None:
        """Test that base.html loads navigation.js."""
        site = Site.objects.get(is_default_site=True)

        request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

        template = Template(
            "{% extends 'sum_core/base.html' %}"
            "{% block content %}Content{% endblock %}"
        )
        rendered = template.render(RequestContext(request, {}))

        assert "navigation.js" in rendered
