"""
Name: Notification Branding Tests
Path: tests/leads/test_notification_branding.py
Purpose: Verify email deliverability controls (From, Reply-To, Subject Prefix) from SiteSettings.
Family: Leads, Notification, Branding.
"""

import pytest
from django.core import mail
from django.test import override_settings
from sum_core.branding.models import SiteSettings
from sum_core.leads.models import Lead
from sum_core.leads.tasks import send_lead_notification
from wagtail.models import Site


@pytest.fixture
def lead(db):
    return Lead.objects.create(
        name="Test Lead",
        email="test@example.com",
        message="Test message",
        form_type="contact",
    )


@pytest.fixture
def site(db):
    return Site.objects.filter(is_default_site=True).first() or Site.objects.create(
        hostname="localhost", port=80, is_default_site=True, site_name="Test Site"
    )


@pytest.fixture
def site_settings(site):
    return SiteSettings.for_site(site)


@pytest.mark.django_db
class TestEmailBranding:
    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_default_sender_used_when_no_settings(self, lead, site, site_settings):
        """Test default FROM email is used when no SiteSettings provided."""
        site_settings.notification_from_email = ""
        site_settings.notification_from_name = ""
        site_settings.notification_reply_to_email = ""
        site_settings.notification_subject_prefix = ""
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        # uses DEFAULT_FROM_EMAIL from django settings (configured as noreply@example.com)
        assert email.from_email == "noreply@example.com"
        assert email.reply_to == []
        assert "New Contact Lead: Test Lead" in email.subject
        assert "[New Lead]" not in email.subject

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_custom_from_email(self, lead, site, site_settings):
        """Test custom FROM email (without name)."""
        site_settings.notification_from_email = "leads@example.com"
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "leads@example.com"

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_custom_from_name_and_email(self, lead, site, site_settings):
        """Test custom FROM name and email."""
        site_settings.notification_from_name = "My Company"
        site_settings.notification_from_email = "leads@example.com"
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "My Company <leads@example.com>"

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_reply_to_setting(self, lead, site, site_settings):
        """Test configured Reply-To header."""
        site_settings.notification_reply_to_email = "reply@example.com"
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.reply_to == ["reply@example.com"]

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_subject_prefix(self, lead, site, site_settings):
        """Test subject prefix."""
        site_settings.notification_subject_prefix = "[URGENT]"
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.subject.startswith("[URGENT] New Contact Lead: Test Lead")

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_all_settings_combined(self, lead, site, site_settings):
        """Test all branding settings combined."""
        site_settings.notification_from_name = "Mega Corp"
        site_settings.notification_from_email = "leads@megacorp.com"
        site_settings.notification_reply_to_email = "sales@megacorp.com"
        site_settings.notification_subject_prefix = "[Lead]"
        site_settings.save()

        send_lead_notification(lead.id, site_id=site.id)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "Mega Corp <leads@megacorp.com>"
        assert email.reply_to == ["sales@megacorp.com"]
        assert email.subject.startswith("[Lead] New Contact Lead: Test Lead")

    @override_settings(LEAD_NOTIFICATION_EMAIL="notify@example.com")
    def test_missing_site_id_uses_defaults(self, lead):
        """Test calling task without site_id falls back to defaults."""
        send_lead_notification(lead.id, site_id=None)

        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert email.from_email == "noreply@example.com"
        assert email.reply_to == []
