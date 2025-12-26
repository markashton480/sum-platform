import uuid

import pytest
from home.models import HomePage
from sum_core.branding.models import SiteSettings


@pytest.mark.django_db
class TestAnalyticsIntegration:
    def setup_page(self, site):
        root = site.root_page
        if not root:
            # Fallback if root is None (shouldn't happen with fixture)
            from wagtail.models import Page

            root = Page.get_first_root_node()

        slug = f"home-{uuid.uuid4()}"
        home = HomePage(title="Home", slug=slug)
        root.add_child(instance=home)
        site.root_page = home
        site.save()
        return home

    def setup_settings(self, site, gtm=None, ga4=None):
        settings = SiteSettings.for_site(site)
        settings.gtm_container_id = gtm or ""
        settings.ga_measurement_id = ga4 or ""
        settings.save()

    def test_render_home_with_gtm(self, client, wagtail_default_site):
        self.setup_page(wagtail_default_site)
        self.setup_settings(wagtail_default_site, gtm="GTM-INTEGRATION")

        response = client.get("/")
        content = response.content.decode()

        assert response.status_code == 200
        assert "GTM-INTEGRATION" in content
        assert "sum-analytics-config" in content
        assert "analytics_loader.js" in content
        assert "googletagmanager.com/gtm.js" not in content
        assert "googletagmanager.com/ns.html" not in content

    def test_render_home_with_ga4(self, client, wagtail_default_site):
        self.setup_page(wagtail_default_site)
        self.setup_settings(wagtail_default_site, ga4="G-INTEGRATION")

        response = client.get("/")
        content = response.content.decode()

        assert response.status_code == 200
        assert "G-INTEGRATION" in content
        assert "sum-analytics-config" in content
        assert "analytics_loader.js" in content
        assert "googletagmanager.com/gtag/js" not in content
        assert "googletagmanager.com/ns.html" not in content
