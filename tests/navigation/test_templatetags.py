"""
Name: Navigation Template Tags Tests
Path: tests/navigation/test_templatetags.py
Purpose: Unit tests for navigation template tags (header_nav, footer_nav, sticky_cta).
Family: Navigation System Test Suite
Dependencies: pytest, django.template, wagtail.models

Test Coverage:
    - test_header_nav_returns_context (structure + expected keys)
    - test_header_nav_active_detection (page + descendant behaviour)
    - test_footer_nav_returns_context (sections + social + business keys)
    - test_sticky_cta_returns_context (toggles + hrefs)
    - test_tag_uses_cache (second call returns cached content)
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from django.core.cache import cache
from django.test import RequestFactory
from django.utils import timezone
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.navigation.templatetags.navigation_tags import (
    _apply_header_active_states,
    _make_cache_key,
    footer_nav,
    header_nav,
    sticky_cta,
)
from wagtail.models import Page

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def request_factory():
    """Provide Django RequestFactory."""
    return RequestFactory()


@pytest.fixture
def default_site(wagtail_default_site):
    """Returns the default Wagtail Site."""
    return wagtail_default_site


@pytest.fixture
def branding_settings(default_site):
    """Create Branding SiteSettings with test values."""
    settings, _ = SiteSettings.objects.get_or_create(
        site=default_site,
        defaults={
            "tagline": "Test Tagline",
            "company_name": "Test Company",
            "phone_number": "555-1234",
            "email": "test@example.com",
            "address": "123 Test Street",
            "facebook_url": "https://facebook.com/test",
            "instagram_url": "https://instagram.com/test",
            "linkedin_url": "https://linkedin.com/test",
            "youtube_url": "https://youtube.com/test",
            "twitter_url": "https://twitter.com/test",
            "tiktok_url": "https://tiktok.com/@test",
        },
    )
    # Ensure fields are set
    settings.tagline = "Test Tagline"
    settings.company_name = "Test Company"
    settings.phone_number = "555-1234"
    settings.email = "test@example.com"
    settings.address = "123 Test Street"
    settings.facebook_url = "https://facebook.com/test"
    settings.instagram_url = "https://instagram.com/test"
    settings.linkedin_url = "https://linkedin.com/test"
    settings.youtube_url = "https://youtube.com/test"
    settings.twitter_url = "https://twitter.com/test"
    settings.tiktok_url = "https://tiktok.com/@test"
    settings.save()
    return settings


@pytest.fixture
def header_navigation(default_site):
    """Create HeaderNavigation with test values."""
    nav, _ = HeaderNavigation.objects.get_or_create(
        site=default_site,
        defaults={
            "show_phone_in_header": True,
            "header_cta_enabled": True,
            "header_cta_text": "Get a Quote",
            "mobile_cta_enabled": True,
            "mobile_cta_phone_enabled": True,
            "mobile_cta_button_enabled": True,
            "mobile_cta_button_text": "Call Now",
        },
    )
    nav.show_phone_in_header = True
    nav.header_cta_enabled = True
    nav.header_cta_text = "Get a Quote"
    nav.mobile_cta_enabled = True
    nav.mobile_cta_phone_enabled = True
    nav.mobile_cta_button_enabled = True
    nav.mobile_cta_button_text = "Call Now"
    nav.save()
    return nav


@pytest.fixture
def footer_navigation(default_site):
    """Create FooterNavigation with test values."""
    nav, _ = FooterNavigation.objects.get_or_create(
        site=default_site,
        defaults={
            "tagline": "Footer Tagline",
            "copyright_text": "© {year} {company_name}. All rights reserved.",
        },
    )
    nav.tagline = "Footer Tagline"
    nav.copyright_text = "© {year} {company_name}. All rights reserved."
    nav.save()
    return nav


@pytest.fixture
def mock_request(request_factory, default_site):
    """Create a mock request for the default site."""
    request = request_factory.get("/")
    request.META["HTTP_HOST"] = "testserver"
    request.META["SERVER_PORT"] = "80"
    return request


@pytest.fixture
def template_context(mock_request):
    """Create a template context with the mock request."""
    return {"request": mock_request}


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


# =============================================================================
# Header Nav Context Tests
# =============================================================================


class TestHeaderNavReturnsContext:
    """Tests that header_nav returns expected context structure."""

    def test_returns_dict(self, template_context, branding_settings, header_navigation):
        """header_nav returns a dictionary."""
        result = header_nav(template_context)

        assert isinstance(result, dict)

    def test_contains_menu_items_key(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav result contains menu_items key."""
        result = header_nav(template_context)

        assert "menu_items" in result
        assert isinstance(result["menu_items"], list)

    def test_contains_show_phone_key(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav result contains show_phone key."""
        result = header_nav(template_context)

        assert "show_phone" in result
        assert result["show_phone"] is True

    def test_contains_phone_number_when_enabled(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav includes phone_number when show_phone is True."""
        result = header_nav(template_context)

        assert "phone_number" in result
        assert result["phone_number"] == "555-1234"

    def test_contains_phone_href(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav includes phone_href as tel: link."""
        result = header_nav(template_context)

        assert "phone_href" in result
        assert result["phone_href"] == "tel:5551234"

    def test_contains_header_cta(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav includes header_cta dict."""
        result = header_nav(template_context)

        assert "header_cta" in result
        cta = result["header_cta"]
        assert isinstance(cta, dict)
        assert "enabled" in cta
        assert "text" in cta
        assert "href" in cta
        assert "attrs" in cta

    def test_header_cta_values(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav header_cta has expected values."""
        result = header_nav(template_context)

        cta = result["header_cta"]
        assert cta["enabled"] is True
        assert cta["text"] == "Get a Quote"

    def test_contains_current_page(
        self, template_context, branding_settings, header_navigation
    ):
        """header_nav includes current_page key."""
        result = header_nav(template_context)

        assert "current_page" in result

    def test_phone_hidden_when_disabled(
        self, template_context, branding_settings, default_site
    ):
        """When show_phone_in_header=False, phone fields are empty."""
        nav, _ = HeaderNavigation.objects.get_or_create(site=default_site)
        nav.show_phone_in_header = False
        nav.save()

        result = header_nav(template_context)

        assert result["show_phone"] is False
        assert result["phone_number"] == ""
        assert result["phone_href"] == ""

    def test_returns_empty_dict_without_request(self):
        """header_nav returns empty dict if no request in context."""
        result = header_nav({})

        assert result == {}


# =============================================================================
# Header Nav Active Detection Tests
# =============================================================================


class TestHeaderNavActiveDetection:
    """Tests for active page detection in header_nav."""

    @pytest.fixture(autouse=True)
    def cleanup_test_pages(self):
        """Clean up test pages after each test to maintain isolation."""
        yield
        # Clean up pages created during tests (exclude root page)
        root = Page.get_first_root_node()
        Page.objects.exclude(pk=root.pk).filter(slug__startswith="nav-test-").delete()

    def test_is_current_true_for_exact_page_match(
        self, default_site, request_factory, branding_settings, header_navigation
    ):
        """Menu item is_current=True when current page matches linked page."""
        import uuid

        # Create a test page with unique slug
        root = Page.get_first_root_node()
        test_page = root.add_child(
            instance=Page(
                title="Test Page", slug=f"nav-test-page-{uuid.uuid4().hex[:8]}"
            )
        )

        # Test the helper function directly
        from sum_core.navigation.templatetags.navigation_tags import _is_current_page

        assert _is_current_page(test_page, test_page) is True

    def test_is_current_false_for_different_pages(self, default_site):
        """Menu item is_current=False when pages don't match."""
        import uuid

        from sum_core.navigation.templatetags.navigation_tags import _is_current_page

        root = Page.get_first_root_node()
        suffix = uuid.uuid4().hex[:8]
        page1 = root.add_child(
            instance=Page(title="Page 1", slug=f"nav-test-page1-{suffix}")
        )
        page2 = root.add_child(
            instance=Page(title="Page 2", slug=f"nav-test-page2-{suffix}")
        )

        assert _is_current_page(page1, page2) is False

    def test_is_active_true_for_exact_page_match(self, default_site):
        """is_active_section returns True for exact page match."""
        import uuid

        from sum_core.navigation.templatetags.navigation_tags import _is_active_section

        root = Page.get_first_root_node()
        test_page = root.add_child(
            instance=Page(
                title="Test Page", slug=f"nav-test-active-{uuid.uuid4().hex[:8]}"
            )
        )

        assert _is_active_section(test_page, test_page) is True

    def test_is_active_true_for_descendant_page(self, default_site):
        """is_active_section returns True when current is descendant of linked."""
        import uuid

        from sum_core.navigation.templatetags.navigation_tags import _is_active_section

        root = Page.get_first_root_node()
        suffix = uuid.uuid4().hex[:8]
        parent_page = root.add_child(
            instance=Page(title="Services", slug=f"nav-test-services-{suffix}")
        )
        child_page = parent_page.add_child(
            instance=Page(title="Roofing", slug=f"nav-test-roofing-{suffix}")
        )

        # Services link is active when viewing Roofing page
        assert _is_active_section(parent_page, child_page) is True

    def test_is_active_false_for_non_descendant(self, default_site):
        """is_active_section returns False when pages are unrelated."""
        import uuid

        from sum_core.navigation.templatetags.navigation_tags import _is_active_section

        root = Page.get_first_root_node()
        suffix = uuid.uuid4().hex[:8]
        services = root.add_child(
            instance=Page(title="Services", slug=f"nav-test-svc-{suffix}")
        )
        about = root.add_child(
            instance=Page(title="About", slug=f"nav-test-about-{suffix}")
        )

        # Services link is not active when viewing About page
        assert _is_active_section(services, about) is False

    def test_is_active_false_for_ancestor_viewing_parent(self, default_site):
        """is_active_section returns False when linked page is a child of current."""
        import uuid

        from sum_core.navigation.templatetags.navigation_tags import _is_active_section

        root = Page.get_first_root_node()
        suffix = uuid.uuid4().hex[:8]
        parent_page = root.add_child(
            instance=Page(title="Services", slug=f"nav-test-parent-{suffix}")
        )
        child_page = parent_page.add_child(
            instance=Page(title="Roofing", slug=f"nav-test-child-{suffix}")
        )

        # Roofing link is NOT active when viewing Services (parent)
        assert _is_active_section(child_page, parent_page) is False

    def test_active_detection_uses_single_query(
        self, default_site, request_factory, django_assert_num_queries
    ):
        """Active state computation should not scale queries with menu size."""
        import uuid

        root = Page.get_first_root_node()
        suffix = uuid.uuid4().hex[:8]

        parent_page = root.add_child(
            instance=Page(title="Services", slug=f"nav-test-svc-{suffix}")
        )
        current_page = parent_page.add_child(
            instance=Page(title="Roofing", slug=f"nav-test-roofing-{suffix}")
        )
        other_pages = [
            root.add_child(
                instance=Page(title=f"Page {i}", slug=f"nav-test-p{i}-{suffix}")
            )
            for i in range(6)
        ]

        menu_pages = [parent_page, current_page, *other_pages]

        def _menu_item_base(page: Page) -> dict[str, Any]:
            return {
                "label": page.title,
                "href": f"/{page.slug}/",
                "is_external": False,
                "opens_new_tab": False,
                "attrs": {},
                "attrs_str": "",
                "has_children": False,
                "children_base": [],
                "_page_pk": page.pk,
                "_link_type": "page",
            }

        base_data = {
            "menu_items_base": [_menu_item_base(page) for page in menu_pages],
            "show_phone": False,
            "phone_number": "",
            "phone_href": "",
            "header_cta": {"enabled": False, "text": "", "href": "#", "attrs": {}},
        }

        request = request_factory.get("/")

        with django_assert_num_queries(1):
            result = _apply_header_active_states(base_data, current_page, request)

        menu_items = result["menu_items"]
        assert menu_items[0]["is_active"] is True
        assert menu_items[0]["is_current"] is False
        assert menu_items[1]["is_active"] is True
        assert menu_items[1]["is_current"] is True


# =============================================================================
# Footer Nav Context Tests
# =============================================================================


class TestFooterNavReturnsContext:
    """Tests that footer_nav returns expected context structure."""

    def test_returns_dict(self, template_context, branding_settings, footer_navigation):
        """footer_nav returns a dictionary."""
        result = footer_nav(template_context)

        assert isinstance(result, dict)

    def test_contains_tagline(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav includes tagline."""
        result = footer_nav(template_context)

        assert "tagline" in result
        assert result["tagline"] == "Footer Tagline"

    def test_contains_link_sections(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav includes link_sections list."""
        result = footer_nav(template_context)

        assert "link_sections" in result
        assert isinstance(result["link_sections"], list)

    def test_contains_social_dict(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav includes social dict with canonical keys."""
        result = footer_nav(template_context)

        assert "social" in result
        social = result["social"]
        assert isinstance(social, dict)
        assert "facebook" in social
        assert "instagram" in social
        assert "linkedin" in social
        assert "youtube" in social
        assert "x" in social
        assert "tiktok" in social

    def test_social_values_from_branding(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav social values come from branding settings."""
        result = footer_nav(template_context)

        social = result["social"]
        assert social["facebook"] == "https://facebook.com/test"
        assert social["instagram"] == "https://instagram.com/test"
        assert social["tiktok"] == "https://tiktok.com/@test"

    def test_contains_business_dict(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav includes business dict with expected keys."""
        result = footer_nav(template_context)

        assert "business" in result
        business = result["business"]
        assert "company_name" in business
        assert "phone_number" in business
        assert "email" in business
        assert "address" in business

    def test_business_values(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav business values are correct."""
        result = footer_nav(template_context)

        business = result["business"]
        assert business["company_name"] == "Test Company"
        assert business["phone_number"] == "555-1234"
        assert business["email"] == "test@example.com"
        assert business["address"] == "123 Test Street"

    def test_contains_copyright(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav includes copyright dict with raw and rendered."""
        result = footer_nav(template_context)

        assert "copyright" in result
        copyright_data = result["copyright"]
        assert "raw" in copyright_data
        assert "rendered" in copyright_data

    def test_copyright_year_placeholder(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav replaces {year} placeholder in copyright."""
        result = footer_nav(template_context)

        current_year = str(timezone.now().year)
        assert current_year in result["copyright"]["rendered"]

    def test_copyright_company_placeholder(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav replaces {company_name} placeholder in copyright."""
        result = footer_nav(template_context)

        assert "Test Company" in result["copyright"]["rendered"]

    def test_copyright_raw_preserves_placeholders(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav copyright.raw preserves original placeholders."""
        result = footer_nav(template_context)

        assert "{year}" in result["copyright"]["raw"]
        assert "{company_name}" in result["copyright"]["raw"]

    def test_copyright_unknown_placeholder_safe(
        self, template_context, branding_settings, footer_navigation
    ):
        """footer_nav leaves unknown placeholders untouched."""
        footer_navigation.copyright_text = "© {year} {company_name} {unknown}."
        footer_navigation.save()

        result = footer_nav(template_context)

        assert "{unknown}" in result["copyright"]["rendered"]

    def test_returns_empty_dict_without_request(self):
        """footer_nav returns empty dict if no request in context."""
        result = footer_nav({})

        assert result == {}


# =============================================================================
# Sticky CTA Context Tests
# =============================================================================


class TestStickyCTAReturnsContext:
    """Tests that sticky_cta returns expected context structure."""

    def test_returns_dict(self, template_context, branding_settings, header_navigation):
        """sticky_cta returns a dictionary."""
        result = sticky_cta(template_context)

        assert isinstance(result, dict)

    def test_contains_enabled(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes enabled toggle."""
        result = sticky_cta(template_context)

        assert "enabled" in result
        assert result["enabled"] is True

    def test_contains_phone_enabled(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes phone_enabled toggle."""
        result = sticky_cta(template_context)

        assert "phone_enabled" in result
        assert result["phone_enabled"] is True

    def test_contains_phone_number(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes phone_number."""
        result = sticky_cta(template_context)

        assert "phone_number" in result
        assert result["phone_number"] == "555-1234"

    def test_contains_phone_href(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes phone_href as tel: link."""
        result = sticky_cta(template_context)

        assert "phone_href" in result
        assert result["phone_href"] == "tel:5551234"

    def test_contains_button_enabled(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes button_enabled toggle."""
        result = sticky_cta(template_context)

        assert "button_enabled" in result
        assert result["button_enabled"] is True

    def test_contains_button_text(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes button_text."""
        result = sticky_cta(template_context)

        assert "button_text" in result
        assert result["button_text"] == "Call Now"

    def test_contains_button_href(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes button_href."""
        result = sticky_cta(template_context)

        assert "button_href" in result

    def test_contains_button_attrs(
        self, template_context, branding_settings, header_navigation
    ):
        """sticky_cta includes button_attrs dict."""
        result = sticky_cta(template_context)

        assert "button_attrs" in result
        assert isinstance(result["button_attrs"], dict)

    def test_returns_empty_dict_without_request(self):
        """sticky_cta returns empty dict if no request in context."""
        result = sticky_cta({})

        assert result == {}


# =============================================================================
# Cache Tests
# =============================================================================


class TestTagUsesCache:
    """Tests for read-through caching behavior."""

    def test_footer_nav_uses_cache_key_format(self, default_site):
        """Cache key format matches spec: nav:footer:{site_id}."""
        cache_key = _make_cache_key("footer", default_site.id)

        assert cache_key == f"nav:footer:{default_site.id}"

    def test_sticky_cta_uses_cache_key_format(self, default_site):
        """Cache key format matches spec: nav:sticky:{site_id}."""
        cache_key = _make_cache_key("sticky", default_site.id)

        assert cache_key == f"nav:sticky:{default_site.id}"

    def test_header_cta_uses_cache_key_format(self, default_site):
        """Cache key format matches spec: nav:header:{site_id}."""
        cache_key = _make_cache_key("header", default_site.id)

        assert cache_key == f"nav:header:{default_site.id}"

    def test_footer_nav_caches_result(
        self, template_context, branding_settings, footer_navigation, default_site
    ):
        """footer_nav caches its result after first call."""
        cache_key = _make_cache_key("footer", default_site.id)

        # First call - should build and cache
        result1 = footer_nav(template_context)

        # Verify cached
        cached = cache.get(cache_key)
        assert cached is not None
        assert cached["copyright"]["raw"] == result1["copyright"]["raw"]
        assert "rendered" not in cached["copyright"]

    def test_sticky_cta_caches_result(
        self, template_context, branding_settings, header_navigation, default_site
    ):
        """sticky_cta caches its result after first call."""
        cache_key = _make_cache_key("sticky", default_site.id)

        # First call - should build and cache
        result1 = sticky_cta(template_context)

        # Verify cached
        cached = cache.get(cache_key)
        assert cached is not None
        assert cached == result1

    def test_second_call_returns_cached_content(
        self, template_context, branding_settings, footer_navigation, default_site
    ):
        """Second call returns cached content when cache is not invalidated."""
        cache_key = _make_cache_key("footer", default_site.id)

        # Pre-populate cache with test data directly (bypass DB)
        test_data = {
            "tagline": "Cached Value",
            "business": {"company_name": "Cached Co"},
            "copyright": {"raw": "© {year} {company_name}."},
        }
        cache.set(cache_key, test_data)

        # Call should return cached value
        result = footer_nav(template_context)

        # Should match cached data
        assert result["tagline"] == "Cached Value"
        assert "Cached Co" in result["copyright"]["rendered"]

    def test_cache_hit_does_not_rebuild(
        self, template_context, branding_settings, footer_navigation, default_site
    ):
        """
        When cache is hit, the builder function is not called.

        We verify this by pre-populating cache and checking the cached data is returned.
        """
        cache_key = _make_cache_key("footer", default_site.id)

        # Pre-populate cache with test data
        test_data = {
            "tagline": "Cached Tagline",
            "business": {"company_name": "Cached Company"},
            "copyright": {"raw": "© {year} {company_name}"},
        }
        cache.set(cache_key, test_data)

        # Call should return cached value without querying DB
        result = footer_nav(template_context)

        # Should use cached base data
        assert result["tagline"] == "Cached Tagline"
        assert "Cached Company" in result["copyright"]["rendered"]

    def test_cache_graceful_fallback_on_get_failure(
        self, template_context, branding_settings, footer_navigation
    ):
        """Tag falls back to building if cache.get fails."""
        with patch(
            "sum_core.navigation.templatetags.navigation_tags.cache"
        ) as mock_cache:
            mock_cache.get.side_effect = Exception("Cache get failed")
            mock_cache.set = MagicMock()

            # Should not raise, should return valid result
            result = footer_nav(template_context)

            assert result is not None
            assert "tagline" in result

    def test_cache_graceful_fallback_on_set_failure(
        self, template_context, branding_settings, footer_navigation
    ):
        """Tag works even if cache.set fails."""
        with patch(
            "sum_core.navigation.templatetags.navigation_tags.cache"
        ) as mock_cache:
            mock_cache.get.return_value = None
            mock_cache.set.side_effect = Exception("Cache set failed")

            # Should not raise, should return valid result
            result = footer_nav(template_context)

            assert result is not None
            assert "tagline" in result


# =============================================================================
# Site Isolation Tests
# =============================================================================


class TestSiteIsolation:
    """Tests that cache is properly scoped to site."""

    def test_different_sites_have_different_cache_keys(self):
        """Different sites produce different cache keys."""
        key1 = _make_cache_key("footer", 1)
        key2 = _make_cache_key("footer", 2)

        assert key1 != key2
        assert "1" in key1
        assert "2" in key2
