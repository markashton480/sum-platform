"""
Integration tests for the Sage & Stone site seeder.

Validates that running seed_sage_stone creates a complete, functional site
with all expected pages, navigation, branding, and content.
"""

from __future__ import annotations

import sys
from importlib import util
from io import StringIO

import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from sum_core.navigation.models import FooterNavigation, HeaderNavigation
from sum_core.pages.blog import BlogIndexPage, BlogPostPage, Category
from sum_core.pages.legal import LegalPage
from sum_core.pages.standard import StandardPage
from wagtail.images.models import Image
from wagtail.models import Site

from tests.utils import REPO_ROOT

MODULE_NAME = "seed_sage_stone_command_integration"

pytestmark = pytest.mark.integration


def _load_seed_module():
    """Load the seed_sage_stone module from the boilerplate."""
    if MODULE_NAME in sys.modules:
        return sys.modules[MODULE_NAME]
    path = (
        REPO_ROOT
        / "boilerplate/project_name/home/management/commands/seed_sage_stone.py"
    )
    spec = util.spec_from_file_location(MODULE_NAME, path)
    assert spec and spec.loader
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_seed_command():
    """Load the Command class from the seed module."""
    return _load_seed_module().Command


def _run_seed_command(
    clear: bool = False,
    images_only: bool = False,
    hostname: str = "localhost",
    port: int = 8000,
) -> None:
    """Run the seed_sage_stone management command."""
    command_cls = _load_seed_command()
    command = command_cls()
    command.stdout = StringIO()
    command.handle(
        clear=clear,
        images_only=images_only,
        hostname=hostname,
        port=port,
    )


@pytest.mark.django_db
class TestFullSeedWorkflow:
    """Integration tests for complete site seeding."""

    def test_full_seed_creates_complete_site(self, wagtail_default_site: Site) -> None:
        """Running seed_sage_stone should create fully functional site."""
        _run_seed_command()

        # Verify site exists with correct configuration
        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.site_name == "Sage & Stone"
        assert site.is_default_site is True

        # Verify page tree structure
        home = site.root_page.specific
        assert isinstance(home, HomePage)
        children = home.get_children().live()

        # Expected child pages
        child_slugs = {page.slug for page in children}
        assert "about" in child_slugs
        assert "services" in child_slugs
        assert "portfolio" in child_slugs
        assert "contact" in child_slugs
        assert "journal" in child_slugs  # Blog index
        assert "terms" in child_slugs  # Legal page

    def test_full_seed_creates_navigation(self, wagtail_default_site: Site) -> None:
        """Seed creates complete header and footer navigation."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)

        # Verify header navigation
        header = HeaderNavigation.for_site(site)
        assert header is not None
        assert len(header.menu_items) >= 5
        assert header.header_cta_enabled is True
        assert header.mobile_cta_enabled is True

        # Verify footer navigation
        footer = FooterNavigation.for_site(site)
        assert footer is not None
        assert len(footer.link_sections) >= 3
        assert footer.tagline == "Rooms that remember."

    def test_full_seed_creates_branding(self, wagtail_default_site: Site) -> None:
        """Seed creates complete branding/site settings."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)
        settings = SiteSettings.for_site(site)

        assert settings.company_name == "Sage & Stone"
        assert settings.primary_color == "#1A2F23"
        assert settings.heading_font == "Playfair Display"
        assert settings.phone_number is not None
        assert settings.header_logo is not None
        assert settings.favicon is not None

    def test_full_seed_creates_images(self, wagtail_default_site: Site) -> None:
        """Seed creates all required placeholder images."""
        _run_seed_command()

        module = _load_seed_module()
        prefix = module.IMAGE_PREFIX

        # All images should be prefixed with SS_
        images = Image.objects.filter(title__startswith=f"{prefix}_")
        assert images.count() >= len(module.IMAGE_MANIFEST)

        # Verify core images exist
        assert Image.objects.filter(title=f"{prefix}_HERO_IMAGE").exists()
        assert Image.objects.filter(title=f"{prefix}_LOGO").exists()
        assert Image.objects.filter(title=f"{prefix}_FAVICON").exists()

    def test_full_seed_creates_blog(self, wagtail_default_site: Site) -> None:
        """Seed creates blog index, categories, and posts."""
        _run_seed_command()

        # Verify categories
        categories = Category.objects.all()
        assert categories.count() >= 3

        category_slugs = {cat.slug for cat in categories}
        assert "material-science" in category_slugs
        assert "commission-stories" in category_slugs
        assert "the-workshop" in category_slugs

        # Verify blog index
        blog_index = BlogIndexPage.objects.get(slug="journal")
        assert blog_index.title == "The Ledger"
        assert blog_index.posts_per_page == 9

        # Verify blog posts
        posts = BlogPostPage.objects.live()
        assert posts.count() == 7

        # All posts should have content
        for post in posts:
            assert post.featured_image is not None
            assert len(post.body) > 0
            assert post.category is not None
            assert post.excerpt

    def test_full_seed_creates_legal_pages(self, wagtail_default_site: Site) -> None:
        """Seed creates legal pages with proper structure."""
        _run_seed_command()

        # Terms page with sections
        terms = LegalPage.objects.get(slug="terms")
        assert terms.title == "Terms of Supply"
        assert len(terms.sections) >= 6

        # Placeholder legal pages
        assert StandardPage.objects.filter(slug="privacy", live=True).exists()
        assert StandardPage.objects.filter(slug="accessibility", live=True).exists()

    def test_pages_have_streamfield_content(self, wagtail_default_site: Site) -> None:
        """All pages should have populated StreamField content."""
        _run_seed_command()

        home = HomePage.objects.get(slug="home")
        assert len(home.body) > 0

        for slug in ["about", "services", "portfolio", "contact"]:
            page = StandardPage.objects.get(slug=slug)
            assert len(page.body) > 0, f"{slug} page should have content"


@pytest.mark.django_db
class TestIdempotency:
    """Tests verifying safe re-runs of the seeder."""

    def test_idempotent_full_seed(self, wagtail_default_site: Site) -> None:
        """Should be safe to run seed multiple times."""
        _run_seed_command()
        first_home_id = HomePage.objects.get(slug="home").id
        first_site_id = Site.objects.get(hostname="localhost", port=8000).id

        _run_seed_command()

        # Should still have exactly one site and homepage
        assert Site.objects.filter(hostname="localhost", port=8000).count() == 1
        assert HomePage.objects.filter(slug="home").count() == 1

        # IDs should remain the same (update, not recreate)
        assert HomePage.objects.get(slug="home").id == first_home_id
        assert Site.objects.get(hostname="localhost", port=8000).id == first_site_id

    def test_idempotent_images(self, wagtail_default_site: Site) -> None:
        """Images should not be duplicated on re-run."""
        _run_seed_command()
        module = _load_seed_module()
        prefix = module.IMAGE_PREFIX

        first_count = Image.objects.filter(title__startswith=f"{prefix}_").count()
        logo_id = Image.objects.get(title=f"{prefix}_LOGO").id

        _run_seed_command()

        # Count should remain the same
        second_count = Image.objects.filter(title__startswith=f"{prefix}_").count()
        assert second_count == first_count

        # Same image should be reused
        assert Image.objects.get(title=f"{prefix}_LOGO").id == logo_id

    def test_idempotent_navigation(self, wagtail_default_site: Site) -> None:
        """Navigation should not be duplicated on re-run."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)
        first_header_id = HeaderNavigation.for_site(site).id
        first_footer_id = FooterNavigation.for_site(site).id

        _run_seed_command()

        # Same navigation objects should be reused
        assert HeaderNavigation.for_site(site).id == first_header_id
        assert FooterNavigation.for_site(site).id == first_footer_id

    def test_idempotent_pages(self, wagtail_default_site: Site) -> None:
        """Pages should not be duplicated on re-run."""
        _run_seed_command()

        page_ids = {}
        for slug in ["about", "services", "portfolio", "contact", "journal", "terms"]:
            if slug == "terms":
                page_ids[slug] = LegalPage.objects.get(slug=slug).id
            elif slug == "journal":
                page_ids[slug] = BlogIndexPage.objects.get(slug=slug).id
            else:
                page_ids[slug] = StandardPage.objects.get(slug=slug).id

        _run_seed_command()

        # All page IDs should remain the same
        for slug, original_id in page_ids.items():
            if slug == "terms":
                assert LegalPage.objects.get(slug=slug).id == original_id
            elif slug == "journal":
                assert BlogIndexPage.objects.get(slug=slug).id == original_id
            else:
                assert StandardPage.objects.get(slug=slug).id == original_id

    def test_idempotent_blog_content(self, wagtail_default_site: Site) -> None:
        """Blog categories and posts should not be duplicated on re-run."""
        _run_seed_command()

        first_category_count = Category.objects.count()
        first_post_count = BlogPostPage.objects.count()
        category_ids = {cat.slug: cat.id for cat in Category.objects.all()}

        _run_seed_command()

        # Counts should remain the same
        assert Category.objects.count() == first_category_count
        assert BlogPostPage.objects.count() == first_post_count

        # Same category objects should be reused
        for slug, original_id in category_ids.items():
            assert Category.objects.get(slug=slug).id == original_id


@pytest.mark.django_db
class TestClearFlag:
    """Tests for the --clear flag functionality."""

    def test_clear_flag_removes_content(self, wagtail_default_site: Site) -> None:
        """--clear flag should remove existing Sage & Stone content."""
        _run_seed_command()

        # Verify content exists
        site = Site.objects.get(hostname="localhost", port=8000)
        original_home_id = HomePage.objects.get(slug="home").id
        assert site is not None

        # Run with clear flag
        _run_seed_command(clear=True)

        # Original content should be gone
        assert not HomePage.objects.filter(id=original_home_id).exists()

        # New content should be created
        assert Site.objects.filter(hostname="localhost", port=8000).count() == 1
        assert HomePage.objects.filter(slug="home").count() == 1

    def test_clear_rebuilds_complete_site(self, wagtail_default_site: Site) -> None:
        """After clear, site should be fully rebuilt."""
        _run_seed_command()
        _run_seed_command(clear=True)

        # Verify complete site structure
        site = Site.objects.get(hostname="localhost", port=8000)
        assert site.site_name == "Sage & Stone"

        home = site.root_page.specific
        children = home.get_children().live()
        child_slugs = {page.slug for page in children}

        assert "about" in child_slugs
        assert "services" in child_slugs
        assert "portfolio" in child_slugs
        assert "journal" in child_slugs
        assert "terms" in child_slugs


@pytest.mark.django_db
class TestImagesOnlyFlag:
    """Tests for the --images-only flag functionality."""

    def test_images_only_creates_images(self, wagtail_default_site: Site) -> None:
        """--images-only should only generate images."""
        _run_seed_command(images_only=True)

        module = _load_seed_module()
        prefix = module.IMAGE_PREFIX

        # Images should be created
        images = Image.objects.filter(title__startswith=f"{prefix}_")
        assert images.count() >= len(module.IMAGE_MANIFEST)

        # But no site content should be created
        assert not Site.objects.filter(hostname="localhost", port=8000).exists()

    def test_images_only_idempotent(self, wagtail_default_site: Site) -> None:
        """--images-only should be idempotent."""
        _run_seed_command(images_only=True)
        module = _load_seed_module()
        prefix = module.IMAGE_PREFIX

        first_count = Image.objects.filter(title__startswith=f"{prefix}_").count()

        _run_seed_command(images_only=True)

        # Count should remain the same
        assert (
            Image.objects.filter(title__startswith=f"{prefix}_").count() == first_count
        )


@pytest.mark.django_db
class TestMegaMenuStructure:
    """Tests for the 3-level mega menu navigation structure."""

    def test_kitchens_mega_menu_structure(self, wagtail_default_site: Site) -> None:
        """Kitchens menu should have 3-level nested structure."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)
        header = HeaderNavigation.for_site(site)

        # Find Kitchens menu item
        kitchens = next(
            (
                item
                for item in header.menu_items
                if item.value.get("label") == "Kitchens"
            ),
            None,
        )
        assert kitchens is not None

        # Should have children (level 2)
        children = kitchens.value.get("children", [])
        assert len(children) >= 3

        # Find Collections submenu
        collections = next(
            (child for child in children if child.get("label") == "Collections"),
            None,
        )
        assert collections is not None

        # Collections should have children (level 3)
        collection_items = collections.get("children", [])
        assert len(collection_items) >= 1

    def test_navigation_links_to_pages(self, wagtail_default_site: Site) -> None:
        """Navigation items should link to existing pages."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)
        header = HeaderNavigation.for_site(site)

        # Check that some menu items have page links in their link structure
        has_page_links = False
        for item in header.menu_items:
            link = item.value.get("link", {})
            if link.get("link_type") == "page" and link.get("page"):
                has_page_links = True
                break

        assert has_page_links, "Navigation should have page links"


@pytest.mark.django_db
class TestSiteConfiguration:
    """Tests for site-level configuration."""

    def test_custom_hostname_port(self, wagtail_default_site: Site) -> None:
        """Seeder should support custom hostname and port."""
        _run_seed_command(hostname="example.com", port=80)

        site = Site.objects.get(hostname="example.com", port=80)
        assert site.site_name == "Sage & Stone"
        assert site.is_default_site is True

    def test_site_settings_complete(self, wagtail_default_site: Site) -> None:
        """All expected site settings should be configured."""
        _run_seed_command()

        site = Site.objects.get(hostname="localhost", port=8000)
        settings = SiteSettings.for_site(site)

        # Company info
        assert settings.company_name == "Sage & Stone"
        assert settings.phone_number

        # Brand colors
        assert settings.primary_color
        assert settings.secondary_color
        assert settings.accent_color

        # Typography
        assert settings.heading_font
        assert settings.body_font

        # Social media
        assert settings.instagram_url

        # Images
        assert settings.header_logo
        assert settings.footer_logo
        assert settings.favicon
        assert settings.og_default_image
