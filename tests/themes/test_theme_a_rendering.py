"""
Name: Theme A Rendering Tests
Path: tests/themes/test_theme_a_rendering.py
Purpose: Integration tests proving Theme A (Sage & Stone) renders correctly with critical DOM hooks
Family: sum_core tests
Dependencies: pytest, wagtail, django
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from django.conf import settings
from django.template import engines
from django.test import Client
from home.models import HomePage
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


@pytest.fixture(scope="module", autouse=True)
def active_theme_a(tmp_path_factory, safe_rmtree):
    """
    Install Theme A templates into a simulated client-owned theme/active/templates/
    directory and ensure it is first in template resolution.
    """
    repo_root = Path(__file__).resolve().parents[2]
    source_templates_dir = repo_root / "themes" / "theme_a" / "templates"
    active_root_dir = Path(tmp_path_factory.mktemp("theme-active"))
    active_templates_dir = active_root_dir / "templates"

    original_theme_templates_dir = Path(settings.THEME_TEMPLATES_DIR)
    original_template_dirs = list(settings.TEMPLATES[0]["DIRS"])

    settings.THEME_TEMPLATES_DIR = str(active_templates_dir)
    settings.TEMPLATES[0]["DIRS"] = [
        Path(settings.THEME_TEMPLATES_DIR),
        Path(settings.CLIENT_OVERRIDES_DIR),
    ]

    active_templates_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_templates_dir, active_templates_dir, dirs_exist_ok=True)
    for loader in engines["django"].engine.template_loaders:
        if hasattr(loader, "reset"):
            loader.reset()
    try:
        yield
    finally:
        safe_rmtree(active_root_dir)
        settings.THEME_TEMPLATES_DIR = str(original_theme_templates_dir)
        settings.TEMPLATES[0]["DIRS"] = original_template_dirs
        for loader in engines["django"].engine.template_loaders:
            if hasattr(loader, "reset"):
                loader.reset()


class TestThemeAHomePage:
    """Tests for HomePage rendering with Theme A.

    Under the v0.6 rendering contract, page models reference theme/... templates and
    Django resolves them via theme/active/templates (client-owned theme).
    """

    def _create_homepage(self, slug: str) -> HomePage:
        """Helper to create a HomePage with given slug."""
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug=slug)
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

        return homepage

    def test_homepage_renders_with_200(self, client: Client) -> None:
        """Test that HomePage renders successfully."""
        self._create_homepage("theme-test-home-200")
        response = client.get("/")
        assert response.status_code == 200

    def test_homepage_contains_theme_marker(self, client: Client) -> None:
        """Test that Theme A marker comment is present."""
        self._create_homepage("theme-test-home-marker")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert "<!-- THEME: theme_a -->" in content

    def test_homepage_contains_main_header_id(self, client: Client) -> None:
        """Test that main-header ID is present for header scroll JS."""
        self._create_homepage("theme-test-home-header-id")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert 'id="main-header"' in content

    def test_homepage_contains_main_id(self, client: Client) -> None:
        """Test that main element has id for skip link."""
        self._create_homepage("theme-test-home-main-id")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert 'id="main"' in content

    def test_homepage_contains_mobile_menu_elements(self, client: Client) -> None:
        """Test that mobile menu elements are present."""
        self._create_homepage("theme-test-home-mobile")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert 'id="mobile-menu"' in content
        assert 'id="mobile-menu-btn"' in content

    def test_homepage_loads_theme_css(self, client: Client) -> None:
        """Test that theme CSS is loaded."""
        self._create_homepage("theme-test-home-css")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert "theme_a/css/main.css" in content

    def test_homepage_loads_theme_js(self, client: Client) -> None:
        """Test that theme JS is loaded."""
        self._create_homepage("theme-test-home-js")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert "theme_a/js/main.js" in content

    def test_homepage_has_skip_link(self, client: Client) -> None:
        """Test that skip link for accessibility is present."""
        self._create_homepage("theme-test-home-skip")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert 'href="#main"' in content
        assert "Skip to main content" in content

    def test_homepage_has_scroll_smooth(self, client: Client) -> None:
        """Test that html element has scroll-smooth class."""
        self._create_homepage("theme-test-home-smooth")
        response = client.get("/")
        content = response.content.decode("utf-8")
        assert 'class="scroll-smooth"' in content


class TestThemeAStandardPage:
    """Tests for StandardPage rendering with Theme A.

    StandardPage uses a theme/... template path under the v0.6 rendering contract,
    and Theme A provides the canonical template shape.
    """

    def _create_homepage_and_standard(self, suffix: str):
        """Helper to create a HomePage and StandardPage."""
        from sum_core.pages.models import StandardPage

        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug=f"theme-home-std-{suffix}")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

        standard = StandardPage(title="Test Standard", slug=f"test-standard-{suffix}")
        homepage.add_child(instance=standard)
        return standard

    def test_standard_page_renders_with_200(self, client: Client) -> None:
        """Test that StandardPage renders successfully."""
        standard = self._create_homepage_and_standard("200")
        response = client.get(standard.url)
        assert response.status_code == 200

    def test_standard_page_uses_theme_a_template(self, client: Client) -> None:
        """Test that StandardPage renders with Theme A structure."""
        standard = self._create_homepage_and_standard("template")
        response = client.get(standard.url)
        content = response.content.decode("utf-8")
        # Theme A header has id="main-header", core header uses class="header"
        assert 'id="main-header"' in content


class TestThemeAMegaMenu:
    """Tests for mega menu DOM hooks (when nav has children)."""

    def test_mega_menu_mobile_menu_present(self, client: Client) -> None:
        """Test that mobile menu elements are always present."""
        root = Page.get_first_root_node()
        homepage = HomePage(title="Theme Test Home", slug="theme-test-mega")
        root.add_child(instance=homepage)

        site = Site.objects.get(is_default_site=True)
        site.root_page = homepage
        site.save()
        Site.clear_site_root_paths_cache()

        response = client.get("/")
        content = response.content.decode("utf-8")
        # The mobile menu is always present in Theme A header
        assert 'id="mobile-menu"' in content
