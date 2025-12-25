import pytest
from django.template import Context, Template
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings


@pytest.mark.django_db
class TestAnalyticsTags:
    def setup_settings(self, site, gtm=None, ga4=None, banner_enabled=None):
        settings = SiteSettings.for_site(site)
        settings.gtm_container_id = gtm or ""
        settings.ga_measurement_id = ga4 or ""
        if banner_enabled is not None:
            settings.cookie_banner_enabled = banner_enabled
        settings.save()
        return settings

    def render_template(self, template_string, context):
        template = Template(template_string)
        return template.render(Context(context))

    def test_analytics_head_gtm_only(self, wagtail_default_site):
        self.setup_settings(wagtail_default_site, gtm="GTM-1234", banner_enabled=True)
        request = RequestFactory().get("/")
        request.site = wagtail_default_site

        out = self.render_template(
            "{% load analytics_tags %}{% analytics_head %}", {"request": request}
        )
        assert "sum-analytics-config" in out
        assert "GTM-1234" in out
        assert '"cookie_banner_enabled": true' in out
        assert "googletagmanager.com/gtm.js" not in out

    def test_analytics_head_ga4_only(self, wagtail_default_site):
        self.setup_settings(wagtail_default_site, ga4="G-5678")
        request = RequestFactory().get("/")
        request.site = wagtail_default_site

        out = self.render_template(
            "{% load analytics_tags %}{% analytics_head %}", {"request": request}
        )
        assert "sum-analytics-config" in out
        assert "G-5678" in out
        assert "googletagmanager.com/gtag/js" not in out

    def test_analytics_head_gtm_priority(self, wagtail_default_site):
        self.setup_settings(wagtail_default_site, gtm="GTM-PRIORITY", ga4="G-IGNORED")
        request = RequestFactory().get("/")
        request.site = wagtail_default_site

        out = self.render_template(
            "{% load analytics_tags %}{% analytics_head %}", {"request": request}
        )
        assert "GTM-PRIORITY" in out
        assert "G-IGNORED" not in out

    def test_analytics_body_gtm(self, wagtail_default_site):
        self.setup_settings(wagtail_default_site, gtm="GTM-BODY")
        request = RequestFactory().get("/")
        request.site = wagtail_default_site

        out = self.render_template(
            "{% load analytics_tags %}{% analytics_body %}", {"request": request}
        )
        assert out.strip() == ""

    def test_analytics_body_ga4_ignored(self, wagtail_default_site):
        self.setup_settings(wagtail_default_site, ga4="G-ONLY")
        request = RequestFactory().get("/")
        request.site = wagtail_default_site

        out = self.render_template(
            "{% load analytics_tags %}{% analytics_body %}", {"request": request}
        )
        assert out.strip() == ""
