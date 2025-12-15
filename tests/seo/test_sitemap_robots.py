import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from sum_core.pages.services import ServiceIndexPage, ServicePage
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site


def publish(page: Page) -> None:
    page.save_revision().publish()
    page.refresh_from_db()


@pytest.mark.django_db
class TestSitemap:
    @pytest.fixture
    def root_page(self) -> Page:
        return Page.get_first_root_node()

    @pytest.fixture
    def home_page(self, root_page: Page) -> HomePage:
        for existing in root_page.get_children().filter(slug="home"):
            existing.delete()
        root_page.refresh_from_db()
        home = HomePage(title="Home", slug="home", intro="Welcome")
        root_page.add_child(instance=home)
        publish(home)
        return home

    @pytest.fixture(autouse=True)
    def site(self, home_page: HomePage, wagtail_default_site: Site) -> Site:
        wagtail_default_site.root_page = home_page
        wagtail_default_site.site_name = "Test Site"
        wagtail_default_site.save()
        Site.clear_site_root_paths_cache()
        return wagtail_default_site

    @pytest.fixture(autouse=True)
    def site_settings(self, site: Site) -> SiteSettings:
        settings = SiteSettings.for_site(site)
        settings.company_name = "ACME Corp"
        settings.save()
        return settings

    @pytest.fixture
    def service_pages(
        self, home_page: HomePage
    ) -> tuple[ServiceIndexPage, ServicePage]:
        # Create service index
        index = ServiceIndexPage(title="Services", slug="services")
        home_page.add_child(instance=index)
        publish(index)

        # Create service page
        service = ServicePage(title="Plumbing", slug="plumbing")
        index.add_child(instance=service)
        publish(service)

        return index, service

    @pytest.fixture
    def standard_page(self, home_page: HomePage) -> StandardPage:
        page = StandardPage(title="About Us", slug="about")
        home_page.add_child(instance=page)
        publish(page)
        return page

    def test_sitemap_returns_200_with_xml_content_type(self, client) -> None:
        """Sitemap endpoint returns 200 with correct content type."""
        response = client.get("/sitemap.xml")

        assert response.status_code == 200
        assert response["Content-Type"].startswith("application/xml")

    def test_sitemap_contains_xml_declaration(self, client) -> None:
        """Sitemap contains valid XML declaration and urlset."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        assert '<?xml version="1.0" encoding="UTF-8"?>' in content
        assert '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' in content
        assert "</urlset>" in content

    def test_sitemap_includes_published_home_page(
        self, client, home_page: HomePage
    ) -> None:
        """Sitemap includes the published HomePage URL."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        assert "<loc>http://testserver/</loc>" in content

    def test_sitemap_includes_all_published_pages(
        self,
        client,
        home_page: HomePage,
        service_pages: tuple,
        standard_page: StandardPage,
    ) -> None:
        """Sitemap includes all published pages."""
        index, service = service_pages
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        # Check all pages are included
        assert f"<loc>http://testserver{home_page.url}</loc>" in content
        assert f"<loc>http://testserver{index.url}</loc>" in content
        assert f"<loc>http://testserver{service.url}</loc>" in content
        assert f"<loc>http://testserver{standard_page.url}</loc>" in content

    def test_sitemap_excludes_unpublished_pages(
        self, client, home_page: HomePage
    ) -> None:
        """Sitemap excludes unpublished (draft) pages."""
        # Create a draft page (not published)
        draft_page = StandardPage(title="Draft Page", slug="draft", live=False)
        home_page.add_child(instance=draft_page)
        draft_page.save()
        # Don't publish

        response = client.get("/sitemap.xml")
        content = response.content.decode()

        assert "<loc>http://testserver/draft/</loc>" not in content

    def test_sitemap_excludes_noindex_pages(self, client, home_page: HomePage) -> None:
        """Sitemap excludes pages with seo_noindex=True."""
        # Create a page with noindex
        noindex_page = StandardPage(
            title="Secret Page", slug="secret", seo_noindex=True
        )
        home_page.add_child(instance=noindex_page)
        publish(noindex_page)

        response = client.get("/sitemap.xml")
        content = response.content.decode()

        assert "<loc>http://testserver/secret/</loc>" not in content

    def test_sitemap_entries_include_required_elements(
        self, client, home_page: HomePage
    ) -> None:
        """Each sitemap URL entry includes loc, lastmod, changefreq, priority."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        # Check for presence of required elements
        assert "<loc>" in content
        assert "<lastmod>" in content
        assert "<changefreq>" in content
        assert "<priority>" in content

    def test_sitemap_lastmod_format(self, client, home_page: HomePage) -> None:
        """Lastmod uses ISO 8601 date format (YYYY-MM-DD)."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        # Should contain a date in YYYY-MM-DD format
        import re

        date_pattern = r"<lastmod>\d{4}-\d{2}-\d{2}</lastmod>"
        assert re.search(date_pattern, content) is not None

    def test_sitemap_priority_homepage_is_highest(
        self, client, home_page: HomePage, standard_page: StandardPage
    ) -> None:
        """HomePage has priority 1.0 (highest)."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        # Extract URLs and priorities
        # HomePage should have priority 1.0
        # We can look for the HomePage URL followed by priority
        home_section = content[
            content.find(f"<loc>http://testserver{home_page.url}</loc>") :
        ]
        next_url = home_section.find("<loc>", 1)
        if next_url > 0:
            home_section = home_section[:next_url]

        assert "<priority>1.0</priority>" in home_section

    def test_sitemap_changefreq_values(
        self, client, home_page: HomePage, service_pages: tuple
    ) -> None:
        """Changefreq values are valid (weekly, monthly, etc.)."""
        response = client.get("/sitemap.xml")
        content = response.content.decode()

        # Valid changefreq values
        valid_freqs = [
            "always",
            "hourly",
            "daily",
            "weekly",
            "monthly",
            "yearly",
            "never",
        ]

        # Extract all changefreq values
        import re

        changefreqs = re.findall(r"<changefreq>(.*?)</changefreq>", content)

        for freq in changefreqs:
            assert freq in valid_freqs

    def test_sitemap_scoped_to_current_site(
        self, client, home_page: HomePage, root_page: Page
    ) -> None:
        """Sitemap only includes pages from current site, not other sites."""
        # Create another site with different root (use StandardPage to avoid HomePage uniqueness constraint)
        other_root = StandardPage(title="Other Root", slug="other-root")
        root_page.add_child(instance=other_root)
        publish(other_root)

        other_site = Site.objects.create(
            hostname="other.example.com",
            port=80,
            root_page=other_root,
            site_name="Other Site",
        )
        Site.clear_site_root_paths_cache()

        # Request sitemap from default site
        response = client.get("/sitemap.xml", HTTP_HOST="testserver")
        content = response.content.decode()

        # Should include default site's home
        assert "<loc>http://testserver/</loc>" in content
        # Should NOT include other site's root
        assert "other-root" not in content

        other_site.delete()


@pytest.mark.django_db
class TestRobotsTxt:
    @pytest.fixture
    def root_page(self) -> Page:
        return Page.get_first_root_node()

    @pytest.fixture
    def home_page(self, root_page: Page) -> HomePage:
        for existing in root_page.get_children().filter(slug="home"):
            existing.delete()
        root_page.refresh_from_db()
        home = HomePage(title="Home", slug="home", intro="Welcome")
        root_page.add_child(instance=home)
        publish(home)
        return home

    @pytest.fixture(autouse=True)
    def site(self, home_page: HomePage, wagtail_default_site: Site) -> Site:
        wagtail_default_site.root_page = home_page
        wagtail_default_site.site_name = "Test Site"
        wagtail_default_site.save()
        Site.clear_site_root_paths_cache()
        return wagtail_default_site

    @pytest.fixture(autouse=True)
    def site_settings(self, site: Site) -> SiteSettings:
        settings = SiteSettings.for_site(site)
        settings.company_name = "ACME Corp"
        settings.save()
        return settings

    def test_robots_returns_200_with_text_plain(self, client) -> None:
        """robots.txt returns 200 with text/plain content type."""
        response = client.get("/robots.txt")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"

    def test_robots_default_allows_all(self, client) -> None:
        """Default robots.txt allows all user agents."""
        response = client.get("/robots.txt")
        content = response.content.decode()

        assert "User-agent: *" in content
        assert "Disallow:" in content

    def test_robots_includes_sitemap_reference(self, client) -> None:
        """robots.txt includes absolute sitemap URL."""
        response = client.get("/robots.txt")
        content = response.content.decode()

        assert "Sitemap: http://testserver/sitemap.xml" in content

    def test_robots_custom_content_from_settings(
        self, client, site_settings: SiteSettings
    ) -> None:
        """robots.txt uses custom content from SiteSettings if configured."""
        custom_content = """User-agent: *
Disallow: /admin/
Disallow: /private/

User-agent: Googlebot
Allow: /"""

        site_settings.robots_txt = custom_content
        site_settings.save()

        response = client.get("/robots.txt")
        content = response.content.decode()

        assert "Disallow: /admin/" in content
        assert "Disallow: /private/" in content
        assert "User-agent: Googlebot" in content

    def test_robots_sitemap_appended_if_missing_from_custom(
        self, client, site_settings: SiteSettings
    ) -> None:
        """Sitemap reference is appended if missing from custom robots.txt."""
        custom_content = """User-agent: *
Disallow: /admin/"""

        site_settings.robots_txt = custom_content
        site_settings.save()

        response = client.get("/robots.txt")
        content = response.content.decode()

        # Custom content should be present
        assert "Disallow: /admin/" in content
        # Sitemap should be appended
        assert "Sitemap: http://testserver/sitemap.xml" in content

    def test_robots_sitemap_not_duplicated_if_already_present(
        self, client, site_settings: SiteSettings
    ) -> None:
        """Sitemap reference is not duplicated if already in custom robots.txt."""
        custom_content = """User-agent: *
Disallow: /admin/

Sitemap: http://testserver/sitemap.xml"""

        site_settings.robots_txt = custom_content
        site_settings.save()

        response = client.get("/robots.txt")
        content = response.content.decode()

        # Count occurrences of "Sitemap:"
        sitemap_count = content.count("Sitemap:")
        assert sitemap_count == 1

    def test_robots_fallback_when_no_settings(self, client) -> None:
        """robots.txt works even if SiteSettings doesn't exist or is empty."""
        # This is already tested by test_robots_default_allows_all
        # but explicitly testing the fallback
        response = client.get("/robots.txt")
        content = response.content.decode()

        assert "User-agent: *" in content
        assert "Sitemap:" in content
