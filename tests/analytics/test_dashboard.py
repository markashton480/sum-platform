from datetime import timedelta

import pytest
from django.utils import timezone
from sum_core.analytics.dashboard import get_lead_analytics
from sum_core.analytics.wagtail_hooks import LeadAnalyticsPanel
from sum_core.leads.models import Lead, LeadSource
from wagtail.models import Page, Site


@pytest.mark.django_db
class TestLeadAnalyticsDashboard:
    def test_get_lead_analytics_counts(self, wagtail_default_site):
        # Setup specific site structure to ensure path isolation
        # wagtail_default_site might point to tree root, which includes everything.
        root = Page.get_first_root_node()

        # Create dedicated home for site 1
        home1 = Page(title="Home 1", slug="home1")
        root.add_child(instance=home1)

        wagtail_default_site.root_page = home1
        wagtail_default_site.save()

        site = wagtail_default_site

        # Create a page under the site
        page = Page(title="Landing Page", slug="landing")
        home1.add_child(instance=page)

        now = timezone.now()
        yesterday = now - timedelta(days=1)
        old_date = now - timedelta(days=31)

        # Lead 1: New, Google Ads, Yesterday (Should be counted)
        Lead.objects.create(
            name="Lead 1",
            email="l1@example.com",
            message="Msg",
            status=Lead.Status.NEW,
            lead_source=LeadSource.GOOGLE_ADS,
            source_page=page,
            # Hack: submit_at is auto_now_add, so we need to update it after creation or mock time
            # But auto_now_add makes it tricky. We can update it with .update() which bypasses save().
        )
        # Update timestamp for Lead 1
        l1 = Lead.objects.get(email="l1@example.com")
        l1.submitted_at = yesterday
        l1.save()  # This might reset if auto_now is used, but auto_now_add is only on creation.
        # Check model definition: submitted_at = models.DateTimeField(auto_now_add=True)
        # So save() won't override it unless it's auto_now=True. It is auto_now_add=True.
        # But wait, usually you can't set auto_now_add field in create().
        # So update() is safer.
        Lead.objects.filter(email="l1@example.com").update(submitted_at=yesterday)

        # Lead 2: Won, SEO, Yesterday (Should be counted)
        Lead.objects.create(
            name="Lead 2",
            email="l2@example.com",
            message="Msg",
            status=Lead.Status.WON,
            lead_source=LeadSource.SEO,
            source_page=page,
        )
        Lead.objects.filter(email="l2@example.com").update(submitted_at=yesterday)

        # Lead 3: New, Direct, Old (Should NOT be counted)
        Lead.objects.create(
            name="Lead 3",
            email="l3@example.com",
            message="Msg",
            status=Lead.Status.NEW,
            lead_source=LeadSource.DIRECT,
            source_page=page,
        )
        Lead.objects.filter(email="l3@example.com").update(submitted_at=old_date)

        # Lead 4: New, Google Ads, Yesterday, but different site (orphaned page or other site)
        # Create another root/site
        other_root = Page.get_first_root_node().add_child(
            instance=Page(title="Other Root", slug="other")
        )
        other_site = Site.objects.create(hostname="other.com", root_page=other_root)
        other_page = other_root.add_child(
            instance=Page(title="Other Landing", slug="other-landing")
        )

        Lead.objects.create(
            name="Lead 4",
            email="l4@example.com",
            message="Msg",
            status=Lead.Status.NEW,
            lead_source=LeadSource.GOOGLE_ADS,
            source_page=other_page,
        )
        Lead.objects.filter(email="l4@example.com").update(submitted_at=yesterday)

        # Test aggregation for main site
        data = get_lead_analytics(site)

        assert data["total"] == 2
        assert data["by_status"]["New"] == 1
        assert data["by_status"]["Won"] == 1
        assert data["by_status"]["Lost"] == 0

        assert data["by_source"]["Google Ads"] == 1
        assert data["by_source"]["SEO"] == 1
        assert data["by_source"]["Direct"] == 0

        # Test aggregation for other site
        data_other = get_lead_analytics(other_site)
        assert data_other["total"] == 1
        assert data_other["by_status"]["New"] == 1

    def test_dashboard_panel_rendering(self, rf, wagtail_default_site):
        # Create a mock request
        request = rf.get("/admin/")
        request.site = wagtail_default_site  # Simulate site middleware or find_for_request logic availability

        panel = LeadAnalyticsPanel(request)

        # Determine if render work
        html = panel.render()

        assert "Lead Summary (Last 30 Days)" in html
        assert "Total Leads" in html
        assert "By Status" in html
        assert "By Source" in html

    def test_dashboard_panel_empty_rendering(self, rf, wagtail_default_site):
        # Create a mock request
        request = rf.get("/admin/")
        request.site = wagtail_default_site

        panel = LeadAnalyticsPanel(request)
        html = panel.render()

        assert "0" in html  # Should show 0 counts
        assert "Total Leads" in html
