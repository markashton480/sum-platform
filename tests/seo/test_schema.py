"""
Tests for JSON-LD schema generation.
"""

import json

import pytest
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from sum_core.branding.models import SiteSettings
from sum_core.pages.services import ServiceIndexPage, ServicePage
from sum_core.pages.standard import StandardPage
from wagtail.models import Page, Site


def publish(page: Page) -> None:
    page.save_revision().publish()
    page.refresh_from_db()


@pytest.mark.django_db
class TestSchemaGeneration:
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
        settings.phone_number = "+1-555-0100"
        settings.email = "info@acme.example"
        settings.address = "123 Main St, Anytown, USA"
        settings.business_hours = "Mon-Fri 9am-5pm"
        settings.save()
        return settings

    @pytest.fixture
    def service_page(self, home_page: HomePage) -> ServicePage:
        index = ServiceIndexPage(title="Services", slug="services")
        home_page.add_child(instance=index)
        publish(index)

        service = ServicePage(
            title="Plumbing Services",
            slug="plumbing",
            short_description="Expert plumbing for your home",
        )
        index.add_child(instance=service)
        publish(service)
        return service

    @pytest.fixture
    def standard_page_with_faq(self, home_page: HomePage) -> StandardPage:
        """Create a StandardPage with FAQBlock in body."""
        page = StandardPage(
            title="FAQ Page",
            slug="faq",
            body=[
                (
                    "faq",
                    {
                        "eyebrow": "Questions",
                        "heading": "Frequently Asked Questions",
                        "intro": "Common questions and answers",
                        "items": [
                            {
                                "question": "What is your service area?",
                                "answer": "<p>We serve the entire metro area.</p>",
                            },
                            {
                                "question": "Do you offer emergency services?",
                                "answer": "<p>Yes, 24/7 emergency service is available.</p>",
                            },
                        ],
                        "allow_multiple_open": True,
                    },
                ),
            ],
        )
        home_page.add_child(instance=page)
        publish(page)
        return page

    def test_homepage_emits_localbusiness_schema(
        self, client, home_page: HomePage
    ) -> None:
        """HomePage should emit LocalBusiness schema."""
        response = client.get(home_page.url)
        content = response.content.decode()

        assert '<script type="application/ld+json">' in content
        assert '"@type": "LocalBusiness"' in content
        assert '"name": "ACME Corp"' in content
        assert '"telephone": "+1-555-0100"' in content
        assert '"email": "info@acme.example"' in content

    def test_homepage_emits_breadcrumb_schema(
        self, client, home_page: HomePage
    ) -> None:
        """HomePage should emit BreadcrumbList schema."""
        response = client.get(home_page.url)
        content = response.content.decode()

        assert '"@type": "BreadcrumbList"' in content

    def test_service_page_emits_service_schema(
        self, client, service_page: ServicePage
    ) -> None:
        """ServicePage should emit Service schema."""
        response = client.get(service_page.url)
        content = response.content.decode()

        assert '"@type": "Service"' in content
        assert '"name": "Plumbing Services"' in content
        assert '"description": "Expert plumbing for your home"' in content
        assert '"provider"' in content
        assert '"name": "ACME Corp"' in content

    def test_faq_page_emits_faqpage_schema(
        self, client, standard_page_with_faq: StandardPage
    ) -> None:
        """Page with FAQBlock should emit FAQPage schema."""
        response = client.get(standard_page_with_faq.url)
        content = response.content.decode()

        assert '"@type": "FAQPage"' in content
        assert '"mainEntity"' in content
        assert '"What is your service area?"' in content
        assert '"We serve the entire metro area."' in content
        assert '"Do you offer emergency services?"' in content
        assert '"Yes, 24/7 emergency service is available."' in content

    def test_breadcrumb_list_structure(self, client, service_page: ServicePage) -> None:
        """BreadcrumbList should have correct structure and ordering."""
        response = client.get(service_page.url)
        content = response.content.decode()

        # Extract schema blocks
        schemas = []
        parts = content.split('<script type="application/ld+json">')
        for part in parts[1:]:
            schema_json = part.split("</script>")[0].strip()
            if schema_json:
                schemas.append(json.loads(schema_json))

        # Find breadcrumb schema
        breadcrumb = None
        for schema in schemas:
            if schema.get("@type") == "BreadcrumbList":
                breadcrumb = schema
                break

        assert breadcrumb is not None
        assert "itemListElement" in breadcrumb
        items = breadcrumb["itemListElement"]
        assert len(items) >= 2  # At least Home and Services

        # Check ordering and positions
        for i, item in enumerate(items, start=1):
            assert item["position"] == i
            assert "name" in item
            assert "item" in item

    def test_all_urls_are_absolute(self, client, service_page: ServicePage) -> None:
        """All URLs in schema should be absolute."""
        response = client.get(service_page.url)
        content = response.content.decode()

        # Extract schema blocks
        schemas = []
        parts = content.split('<script type="application/ld+json">')
        for part in parts[1:]:
            schema_json = part.split("</script>")[0].strip()
            if schema_json:
                schemas.append(json.loads(schema_json))

        # Check all URLs
        for schema in schemas:
            schema_type = schema.get("@type")
            if schema_type == "BreadcrumbList":
                for item in schema.get("itemListElement", []):
                    url = item.get("item", "")
                    if url:
                        assert url.startswith("http://"), f"URL not absolute: {url}"
            elif schema_type == "Service":
                url = schema.get("url", "")
                if url:
                    assert url.startswith("http://"), f"URL not absolute: {url}"

    def test_schema_is_valid_json(self, client, home_page: HomePage) -> None:
        """All emitted schema should be valid JSON."""
        response = client.get(home_page.url)
        content = response.content.decode()

        # Extract and parse all schema blocks
        parts = content.split('<script type="application/ld+json">')
        for part in parts[1:]:
            schema_json = part.split("</script>")[0].strip()
            if schema_json:
                # Should not raise exception
                json.loads(schema_json)

    def test_no_schema_when_page_missing(self, client) -> None:
        """render_schema should not crash when page is missing from context."""
        from django.template import Context, Template

        template = Template("{% load seo_tags %}{% render_schema page %}")
        context = Context({"request": None, "page": None})
        result = template.render(context)

        # Should render empty, not crash
        assert result.strip() == ""

    def test_missing_site_settings_does_not_crash(
        self, client, home_page: HomePage, site: Site
    ) -> None:
        """Missing site settings should not crash schema generation."""
        # Delete site settings
        SiteSettings.objects.filter(site=site).delete()

        response = client.get(home_page.url)
        assert response.status_code == 200
        content = response.content.decode()

        # Should still have breadcrumbs, but no LocalBusiness
        assert '"@type": "BreadcrumbList"' in content
        assert '"@type": "LocalBusiness"' not in content


@pytest.mark.django_db
class TestSchemaFunctions:
    """Unit tests for schema building functions."""

    @pytest.fixture
    def root_page(self) -> Page:
        return Page.get_first_root_node()

    @pytest.fixture
    def site(self, wagtail_default_site: Site) -> Site:
        return wagtail_default_site

    def test_build_localbusiness_schema_with_full_data(self, site: Site) -> None:
        from sum_core.seo.schema import build_localbusiness_schema

        settings = SiteSettings.for_site(site)
        settings.company_name = "Test Business"
        settings.phone_number = "+1-555-0200"
        settings.email = "test@example.com"
        settings.address = "456 Test Ave"
        settings.business_hours = "Mon-Fri 8am-6pm"
        settings.save()

        schema = build_localbusiness_schema(settings, None)

        assert schema is not None
        assert schema["@type"] == "LocalBusiness"
        assert schema["name"] == "Test Business"
        assert schema["telephone"] == "+1-555-0200"
        assert schema["email"] == "test@example.com"
        assert schema["address"] == "456 Test Ave"
        assert schema["openingHours"] == "Mon-Fri 8am-6pm"

    def test_build_localbusiness_schema_without_company_name(self, site: Site) -> None:
        from sum_core.seo.schema import build_localbusiness_schema

        settings = SiteSettings.for_site(site)
        settings.company_name = ""
        settings.save()

        schema = build_localbusiness_schema(settings, None)
        assert schema is None

    def test_build_breadcrumb_schema_ordering(self, root_page: Page) -> None:
        from sum_core.seo.schema import build_breadcrumb_schema

        home = HomePage(title="Home-Unit", slug="home-unit")
        root_page.add_child(instance=home)
        publish(home)

        child = StandardPage(title="About", slug="about")
        home.add_child(instance=child)
        publish(child)

        schema = build_breadcrumb_schema(child, None)

        assert schema is not None
        assert schema["@type"] == "BreadcrumbList"
        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[0]["position"] == 1
        assert items[0]["name"] == "Home-Unit"
        assert items[1]["position"] == 2
        assert items[1]["name"] == "About"

    def test_extract_faq_items_from_streamfield(self) -> None:
        from sum_core.seo.schema import extract_faq_items_from_streamfield

        # Create a StreamField with FAQ blocks
        body = PageStreamBlock().to_python(
            [
                {
                    "type": "faq",
                    "value": {
                        "eyebrow": "",
                        "heading": "FAQ",
                        "intro": "",
                        "items": [
                            {"question": "Q1", "answer": "<p>A1</p>"},
                            {"question": "Q2", "answer": "<p>A2</p>"},
                        ],
                        "allow_multiple_open": True,
                    },
                },
            ]
        )

        items = extract_faq_items_from_streamfield(body)

        assert len(items) == 2
        assert items[0]["question"] == "Q1"
        assert items[1]["question"] == "Q2"

    def test_build_faq_schema_strips_html(self) -> None:
        from sum_core.seo.schema import build_faq_schema

        items = [
            {"question": "Test Q", "answer": "<p>Test <strong>Answer</strong></p>"},
        ]

        schema = build_faq_schema(items)

        assert schema is not None
        assert schema["@type"] == "FAQPage"
        main_entity = schema["mainEntity"]
        assert len(main_entity) == 1
        assert main_entity[0]["name"] == "Test Q"
        # HTML should be stripped
        assert main_entity[0]["acceptedAnswer"]["text"] == "Test Answer"
