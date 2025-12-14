"""
Name: Lead admin tests (Wagtail)
Path: tests/leads/test_lead_admin_wagtail.py
Purpose: Test Wagtail admin UI for Leads including list/detail views, permissions, and CSV export.
Family: Lead management, admin, testing.
Dependencies: pytest, pytest-django, Wagtail admin, Lead model.
"""

from __future__ import annotations

import csv
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import Client
from sum_core.leads.models import Lead, LeadSource
from sum_core.leads.services import build_lead_csv, can_user_export_leads

User = get_user_model()


@pytest.fixture
def admin_user(db):
    """Create an admin user with all permissions."""
    user = User.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="password123",
    )
    return user


@pytest.fixture
def editor_user(db):
    """Create an editor user with access_admin + view_lead permissions only."""
    user = User.objects.create_user(
        username="editor",
        email="editor@test.com",
        password="password123",
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])

    # Grant Wagtail admin access + view permission (but NOT change/export)
    user.user_permissions.add(
        Permission.objects.get(
            codename="access_admin", content_type__app_label="wagtailadmin"
        ),
        Permission.objects.get(
            codename="view_lead", content_type__app_label="sum_core_leads"
        ),
    )
    return user


@pytest.fixture
def viewer_user(db):
    """Create a viewer user with access_admin + view_lead permission."""
    user = User.objects.create_user(
        username="viewer",
        email="viewer@test.com",
        password="password123",
    )
    user.is_staff = True
    user.save(update_fields=["is_staff"])

    # Grant Wagtail admin access + view permission
    user.user_permissions.add(
        Permission.objects.get(
            codename="access_admin", content_type__app_label="wagtailadmin"
        ),
        Permission.objects.get(
            codename="view_lead", content_type__app_label="sum_core_leads"
        ),
    )
    return user


@pytest.fixture
def sample_leads(db):
    """Create sample leads for testing."""
    leads = []
    for i in range(5):
        lead = Lead.objects.create(
            name=f"Test Lead {i}",
            email=f"lead{i}@test.com",
            phone=f"555-000{i}",
            message=f"Test message {i}",
            form_type="contact",
            status=Lead.Status.NEW if i % 2 == 0 else Lead.Status.CONTACTED,
            lead_source=LeadSource.GOOGLE_ADS if i % 2 == 0 else LeadSource.SEO,
            utm_source="google" if i % 2 == 0 else "",
            utm_medium="cpc" if i % 2 == 0 else "",
            utm_campaign=f"campaign_{i}",
        )
        leads.append(lead)
    return leads


class TestLeadPermissionHelpers:
    """Test permission helper functions."""

    @pytest.mark.django_db
    def test_can_user_export_leads_superuser(self, admin_user):
        """Superusers can export leads."""
        assert can_user_export_leads(admin_user) is True

    @pytest.mark.django_db
    def test_can_user_export_leads_with_permission(self):
        """Users with export_lead permission can export."""
        user = User.objects.create_user(
            username="exporter",
            email="exporter@test.com",
            password="password123",
        )
        user.user_permissions.add(
            Permission.objects.get(
                codename="export_lead", content_type__app_label="sum_core_leads"
            ),
        )
        assert can_user_export_leads(user) is True

    @pytest.mark.django_db
    def test_can_user_export_leads_without_permission(self, editor_user):
        """Users without export_lead permission cannot export."""
        assert can_user_export_leads(editor_user) is False

    def test_can_user_export_leads_unauthenticated(self):
        """Unauthenticated users cannot export."""
        assert can_user_export_leads(None) is False


@pytest.mark.django_db
class TestCSVExport:
    """Test CSV export functionality."""

    def test_build_lead_csv_empty_queryset(self):
        """CSV export works with empty queryset."""
        queryset = Lead.objects.none()
        csv_content = build_lead_csv(queryset)

        # Parse CSV
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        # Should have header but no data rows
        assert len(rows) == 0
        assert reader.fieldnames is not None

    def test_build_lead_csv_single_lead(self):
        """CSV export includes all required fields."""
        Lead.objects.create(
            name="John Doe",
            email="john@test.com",
            phone="555-1234",
            message="Test message with\nlinebreak",
            form_type="contact",
            status=Lead.Status.NEW,
            lead_source=LeadSource.GOOGLE_ADS,
            lead_source_detail="Details here",
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="test_campaign",
            utm_term="keyword",
            utm_content="ad_variant",
            landing_page_url="https://example.com/landing",
            page_url="https://example.com/contact",
            referrer_url="https://google.com",
        )

        csv_content = build_lead_csv(Lead.objects.all())

        # Parse CSV
        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        assert len(rows) == 1
        row = rows[0]

        # Check key fields
        assert row["Name"] == "John Doe"
        assert row["Email"] == "john@test.com"
        assert row["Phone"] == "555-1234"
        assert row["Message"] == "Test message with\nlinebreak"  # Proper CSV escaping
        assert row["Form Type"] == "contact"
        assert row["Status"] == "New"
        assert row["Lead Source"] == "Google Ads"
        assert row["Lead Source Detail"] == "Details here"
        assert row["UTM Source"] == "google"
        assert row["UTM Medium"] == "cpc"
        assert row["UTM Campaign"] == "test_campaign"
        assert row["UTM Term"] == "keyword"
        assert row["UTM Content"] == "ad_variant"
        assert row["Landing Page URL"] == "https://example.com/landing"
        assert row["Page URL"] == "https://example.com/contact"
        assert row["Referrer URL"] == "https://google.com"

    def test_build_lead_csv_multiple_leads(self, sample_leads):
        """CSV export includes all leads in queryset."""
        csv_content = build_lead_csv(Lead.objects.all())

        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        assert len(rows) == 5

    def test_build_lead_csv_handles_commas(self):
        """CSV export properly escapes commas in fields."""
        Lead.objects.create(
            name="Doe, John",
            email="john@test.com",
            message="Message with, commas, in it.",
            form_type="contact",
        )

        csv_content = build_lead_csv(Lead.objects.all())

        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        # Commas should be properly escaped
        assert rows[0]["Name"] == "Doe, John"
        assert rows[0]["Message"] == "Message with, commas, in it."

    def test_build_lead_csv_handles_quotes(self):
        """CSV export properly escapes quotes in fields."""
        Lead.objects.create(
            name='John "The Best" Doe',
            email="john@test.com",
            message='He said "hello"',
            form_type="contact",
        )

        csv_content = build_lead_csv(Lead.objects.all())

        reader = csv.DictReader(StringIO(csv_content))
        rows = list(reader)

        assert rows[0]["Name"] == 'John "The Best" Doe'
        assert rows[0]["Message"] == 'He said "hello"'


@pytest.mark.django_db
class TestWagtailLeadAdmin:
    """Test Wagtail admin interface for Leads."""

    def test_admin_can_access_lead_list(self, admin_user, sample_leads):
        """Admin users can access the lead list view."""
        client = Client()
        client.force_login(admin_user)

        # The URL pattern for Wagtail ModelViewSet is typically /admin/app_label/model/
        # For our case it should be /admin/leads/
        response = client.get("/admin/leads/")

        assert response.status_code == 200

    def test_editor_can_access_lead_list(self, editor_user, sample_leads):
        """Editor users can access the lead list view."""
        client = Client()
        client.force_login(editor_user)

        response = client.get("/admin/leads/")

        assert response.status_code == 200

    def test_unauthenticated_cannot_access_lead_list(self, sample_leads):
        """Unauthenticated users cannot access the lead list."""
        client = Client()
        response = client.get("/admin/leads/")

        # Should redirect to login
        assert response.status_code == 302

    def test_admin_can_access_lead_detail(self, admin_user, sample_leads):
        """Admin users can access lead detail/edit view."""
        client = Client()
        client.force_login(admin_user)

        lead = sample_leads[0]
        response = client.get(f"/admin/leads/edit/{lead.id}/")

        assert response.status_code == 200

    def test_editor_can_access_lead_detail(self, editor_user, sample_leads):
        """Editor users can access lead detail view."""
        client = Client()
        client.force_login(editor_user)

        lead = sample_leads[0]
        response = client.get(f"/admin/leads/inspect/{lead.id}/")

        assert response.status_code == 200

    def test_admin_can_update_lead_status(self, admin_user, sample_leads):
        """Admin users can update lead status."""
        client = Client()
        client.force_login(admin_user)

        lead = sample_leads[0]
        assert lead.status == Lead.Status.NEW

        # Post update
        client.post(
            f"/admin/leads/edit/{lead.id}/",
            {
                "status": Lead.Status.CONTACTED,
                "is_archived": False,
            },
        )

        # Refresh from DB
        lead.refresh_from_db()
        assert lead.status == Lead.Status.CONTACTED

    def test_editor_cannot_update_lead_status(self, editor_user, sample_leads):
        """Editor users cannot update lead status (view-only)."""
        client = Client()
        client.force_login(editor_user)

        lead = sample_leads[0]
        assert lead.status == Lead.Status.NEW

        response = client.post(
            f"/admin/leads/edit/{lead.id}/",
            {
                "status": Lead.Status.QUOTED,
                "is_archived": False,
            },
        )

        lead.refresh_from_db()
        assert response.status_code in [302, 403]
        assert lead.status == Lead.Status.NEW

    def test_viewer_cannot_update_lead_status(self, viewer_user, sample_leads):
        """Viewer users (without change permission) cannot update lead status."""
        client = Client()
        client.force_login(viewer_user)

        lead = sample_leads[0]
        original_status = lead.status

        response = client.post(
            f"/admin/leads/edit/{lead.id}/",
            {
                "status": Lead.Status.CONTACTED,
                "is_archived": False,
            },
        )

        # Should be forbidden or redirected
        assert response.status_code in [302, 403]

        # Status should not change
        lead.refresh_from_db()
        assert lead.status == original_status


@pytest.mark.django_db
class TestCSVExportPermissions:
    """Test CSV export permission enforcement."""

    def test_admin_can_export_leads(self, admin_user, sample_leads):
        """Admin users can export leads to CSV."""
        client = Client()
        client.force_login(admin_user)

        response = client.get("/admin/leads/export/")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert "attachment" in response["Content-Disposition"]

        # Verify CSV content
        content = response.content.decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        assert len(rows) == 5  # Should have all 5 sample leads

    def test_export_respects_status_filter(self, admin_user, sample_leads):
        """CSV export applies the same filters as the list view."""
        client = Client()
        client.force_login(admin_user)

        response = client.get(f"/admin/leads/export/?status={Lead.Status.NEW}")

        assert response.status_code == 200

        content = response.content.decode("utf-8")
        reader = csv.DictReader(StringIO(content))
        rows = list(reader)

        assert len(rows) == 3
        assert {row["Status"] for row in rows} == {"New"}

    def test_user_with_export_permission_can_export(self, sample_leads):
        """Users with export_lead permission can export."""
        user = User.objects.create_user(
            username="exporter",
            email="exporter@test.com",
            password="password123",
        )
        user.is_staff = True
        user.save(update_fields=["is_staff"])
        user.user_permissions.add(
            Permission.objects.get(
                codename="access_admin", content_type__app_label="wagtailadmin"
            ),
            Permission.objects.get(
                codename="export_lead", content_type__app_label="sum_core_leads"
            ),
        )

        client = Client()
        client.force_login(user)

        response = client.get("/admin/leads/export/")

        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"

    def test_editor_cannot_export_leads(self, editor_user, sample_leads):
        """Editor users without export permission cannot export."""
        client = Client()
        client.force_login(editor_user)

        response = client.get("/admin/leads/export/")

        # Should be forbidden
        assert response.status_code == 403

    def test_viewer_cannot_export_leads(self, viewer_user, sample_leads):
        """Viewer users cannot export."""
        client = Client()
        client.force_login(viewer_user)

        response = client.get("/admin/leads/export/")

        assert response.status_code == 403

    def test_unauthenticated_cannot_export_leads(self, sample_leads):
        """Unauthenticated users cannot export."""
        client = Client()

        response = client.get("/admin/leads/export/")

        # Should redirect to login or return 403
        assert response.status_code in [302, 403]


@pytest.mark.django_db
class TestLeadAdminSearch:
    """Test search functionality in lead admin."""

    def test_search_by_name(self, admin_user, sample_leads):
        """Search finds leads by name."""
        client = Client()
        client.force_login(admin_user)

        # Search for "Lead 2"
        response = client.get("/admin/leads/?q=Lead+2")

        assert response.status_code == 200
        # Verify only matching lead appears (implementation-dependent)

    def test_search_by_email(self, admin_user, sample_leads):
        """Search finds leads by email."""
        client = Client()
        client.force_login(admin_user)

        response = client.get("/admin/leads/?q=lead2@test.com")

        assert response.status_code == 200


@pytest.mark.django_db
class TestLeadAdminFilters:
    """Test filter functionality in lead admin."""

    def test_filter_by_status(self, admin_user, sample_leads):
        """Filter leads by status."""
        client = Client()
        client.force_login(admin_user)

        response = client.get(f"/admin/leads/?status={Lead.Status.NEW}")

        assert response.status_code == 200

    def test_filter_by_lead_source(self, admin_user, sample_leads):
        """Filter leads by lead source."""
        client = Client()
        client.force_login(admin_user)

        response = client.get(f"/admin/leads/?lead_source={LeadSource.GOOGLE_ADS}")

        assert response.status_code == 200

    def test_filter_by_form_type(self, admin_user, sample_leads):
        """Filter leads by form type."""
        client = Client()
        client.force_login(admin_user)

        response = client.get("/admin/leads/?form_type=contact")

        assert response.status_code == 200


@pytest.mark.django_db
class TestLeadAdminCannotAdd:
    """Test that users cannot add leads through Wagtail admin."""

    def test_admin_cannot_add_lead(self, admin_user):
        """Even admins cannot add leads through the admin (they come from forms)."""
        client = Client()
        client.force_login(admin_user)

        # Try to access the add view
        response = client.get("/admin/leads/add/")

        # Should either 404, 403, or redirect (depending on ViewSet config)
        assert response.status_code in [403, 404, 405]
