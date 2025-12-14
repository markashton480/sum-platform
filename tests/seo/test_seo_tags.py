import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings
from sum_core.pages.services import ServiceIndexPage, ServicePage
from wagtail.images.models import Image
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page, Site


def publish(page: Page) -> None:
    page.save_revision().publish()
    page.refresh_from_db()


@pytest.mark.django_db
class TestSeoTags:
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
    def service_page(self, home_page: HomePage) -> ServicePage:
        index = ServiceIndexPage(title="Services", slug="services")
        home_page.add_child(instance=index)
        publish(index)

        service = ServicePage(title="Plumbing", slug="plumbing")
        index.add_child(instance=service)
        publish(service)
        return service

    def test_meta_title_default(self, client, home_page: HomePage) -> None:
        response = client.get(home_page.url)
        content = response.content.decode()

        assert "<title>Home | ACME Corp</title>" in content

    def test_meta_title_meta_title_wins(self, client, home_page: HomePage) -> None:
        home_page.meta_title = "Platform Meta Title"
        home_page.seo_title = "Wagtail SEO Title"
        publish(home_page)

        response = client.get(home_page.url)
        content = response.content.decode()

        assert "<title>Platform Meta Title</title>" in content

    def test_meta_title_seo_title_fallback(self, client, home_page: HomePage) -> None:
        home_page.meta_title = ""
        home_page.seo_title = "Wagtail SEO Title"
        publish(home_page)

        response = client.get(home_page.url)
        content = response.content.decode()

        assert "<title>Wagtail SEO Title</title>" in content

    @pytest.mark.parametrize(
        ("meta_description", "search_description", "expected_present"),
        [
            ("Platform description.", "Wagtail description.", "Platform description."),
            ("", "Wagtail description.", "Wagtail description."),
            ("", "", None),
        ],
    )
    def test_meta_description_precedence(
        self,
        client,
        home_page: HomePage,
        meta_description: str,
        search_description: str,
        expected_present: str | None,
    ) -> None:
        home_page.meta_description = meta_description
        home_page.search_description = search_description
        publish(home_page)

        response = client.get(home_page.url)
        content = response.content.decode()

        if expected_present is None:
            assert '<meta name="description"' not in content
        else:
            assert f'<meta name="description" content="{expected_present}">' in content

    @pytest.mark.parametrize(
        ("noindex", "nofollow", "expected"),
        [
            (False, False, "index, follow"),
            (True, False, "noindex, follow"),
            (False, True, "index, nofollow"),
            (True, True, "noindex, nofollow"),
        ],
    )
    def test_robots_truth_table(
        self, client, home_page: HomePage, noindex: bool, nofollow: bool, expected: str
    ) -> None:
        home_page.seo_noindex = noindex
        home_page.seo_nofollow = nofollow
        publish(home_page)

        response = client.get(home_page.url)
        content = response.content.decode()

        assert f'<meta name="robots" content="{expected}">' in content

    def test_canonical_url_is_absolute(self, client, home_page: HomePage) -> None:
        response = client.get(home_page.url)
        content = response.content.decode()

        assert '<link rel="canonical" href="http://testserver/">' in content

    def test_canonical_and_og_url_use_request_host_and_path(
        self, client, service_page: ServicePage
    ) -> None:
        response = client.get(service_page.url)
        content = response.content.decode()

        expected = f"http://testserver{service_page.url}"
        assert f'<link rel="canonical" href="{expected}">' in content
        assert f'<meta property="og:url" content="{expected}">' in content

    def test_og_defaults_and_omissions(self, client, home_page: HomePage) -> None:
        response = client.get(home_page.url)
        content = response.content.decode()

        assert '<meta property="og:type" content="website">' in content
        assert '<meta property="og:title" content="Home | ACME Corp">' in content
        assert '<meta property="og:url" content="http://testserver/">' in content
        assert '<meta property="og:site_name" content="ACME Corp">' in content

        assert '<meta property="og:description"' not in content
        assert '<meta property="og:image"' not in content

    def test_og_description_falls_back_to_search_description(
        self, client, home_page: HomePage
    ) -> None:
        home_page.meta_description = ""
        home_page.search_description = "Wagtail description."
        publish(home_page)

        response = client.get(home_page.url)
        content = response.content.decode()

        assert (
            '<meta property="og:description" content="Wagtail description.">' in content
        )

    def test_og_image_fallback_order(
        self, client, service_page: ServicePage, site_settings: SiteSettings
    ) -> None:
        response = client.get(service_page.url)
        content = response.content.decode()
        assert '<meta property="og:image"' not in content

        site_default = Image.objects.create(title="Site OG", file=get_test_image_file())
        site_settings.og_default_image = site_default
        site_settings.save()
        response = client.get(service_page.url)
        content = response.content.decode()
        expected = f"http://testserver{site_default.get_rendition('original').url}"
        assert f'property="og:image" content="{expected}"' in content

        featured = Image.objects.create(title="Featured", file=get_test_image_file())
        service_page.featured_image = featured
        publish(service_page)
        response = client.get(service_page.url)
        content = response.content.decode()
        expected = f"http://testserver{featured.get_rendition('original').url}"
        assert f'property="og:image" content="{expected}"' in content

        explicit = Image.objects.create(title="Explicit OG", file=get_test_image_file())
        service_page.og_image = explicit
        publish(service_page)
        response = client.get(service_page.url)
        content = response.content.decode()
        expected = f"http://testserver{explicit.get_rendition('original').url}"
        assert f'property="og:image" content="{expected}"' in content
