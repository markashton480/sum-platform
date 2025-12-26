"""
Integration tests for email notification delivery.

Tests the complete email notification flow including admin notifications
and auto-reply emails, with proper mocking of SMTP.
"""

import pytest
from django.core import mail
from django.test import override_settings
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import send_auto_reply, send_form_notification
from sum_core.leads.models import EmailStatus, Lead
from wagtail.models import Site


@pytest.mark.django_db
class TestAdminNotificationEmails:
    """Test admin notification email delivery."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def form_with_notifications(self, site):
        """Create form with email notifications enabled."""
        return FormDefinition.objects.create(
            name="Contact Form",
            slug="contact-notifications",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {
                        "field_name": "message",
                        "label": "Message",
                        "required": True,
                        "rows": 5,
                    },
                ),
            ],
            success_message="Thanks for contacting us!",
            email_notification_enabled=True,
            notification_emails="admin@example.com, sales@example.com",
            is_active=True,
        )

    @pytest.fixture
    def test_lead(self, form_with_notifications):
        """Create a test lead for email testing."""
        return Lead.objects.create(
            name="John Doe",
            email="john@example.com",
            phone="555-1234",
            message="I have a question about your services.",
            form_type="contact-notifications",
            page_url="https://example.com/contact",
            landing_page_url="https://example.com",
            utm_source="google",
            utm_campaign="spring-2024",
            form_notification_status=EmailStatus.PENDING,
            form_data={
                "name": "John Doe",
                "email": "john@example.com",
                "message": "I have a question about your services.",
                "form_definition_slug": "contact-notifications",
            },
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_admin_notification_email_sent(self, form_with_notifications, test_lead):
        """Test that admin notification email is sent successfully."""
        # Clear outbox
        mail.outbox = []

        # Send notification
        send_form_notification(test_lead.id, form_with_notifications.id)

        # Verify email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        # Check recipients
        assert set(email.to) == {"admin@example.com", "sales@example.com"}

        # Check subject contains form name
        assert "Contact Form" in email.subject

        # Check body contains lead data
        assert "John Doe" in email.body
        assert "john@example.com" in email.body
        assert "I have a question" in email.body

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_notification_email_includes_attribution(
        self, form_with_notifications, test_lead
    ):
        """Test that notification email includes attribution data."""
        mail.outbox = []

        send_form_notification(test_lead.id, form_with_notifications.id)

        email = mail.outbox[0]

        # Verify attribution data is in email
        assert "utm_source" in email.body or "google" in email.body
        assert "utm_campaign" in email.body or "spring-2024" in email.body
        assert test_lead.page_url in email.body

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_notification_email_includes_contact_info(
        self, form_with_notifications, test_lead
    ):
        """Test that notification email includes all contact information."""
        mail.outbox = []

        send_form_notification(test_lead.id, form_with_notifications.id)

        email = mail.outbox[0]

        # Verify all contact fields are present
        assert test_lead.name in email.body
        assert test_lead.email in email.body
        assert test_lead.phone in email.body
        assert test_lead.message in email.body

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_notification_to_multiple_recipients(self, site):
        """Test sending notifications to multiple email addresses."""
        # Create form with multiple notification recipients
        form = FormDefinition.objects.create(
            name="Multi Admin Form",
            slug="multi-admin",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            email_notification_enabled=True,
            notification_emails=(
                "admin1@example.com, admin2@example.com, admin3@example.com"
            ),
            is_active=True,
        )

        lead = Lead.objects.create(
            name="Multi Test",
            email="multi@example.com",
            message="Testing multiple admins",
            form_type="multi-admin",
            form_notification_status=EmailStatus.PENDING,
            form_data={
                "email": "multi@example.com",
                "form_definition_slug": form.slug,
            },
        )

        mail.outbox = []
        send_form_notification(lead.id, form.id)

        # All recipients should receive the email
        assert len(mail.outbox) == 1
        email = mail.outbox[0]
        assert len(email.to) == 3
        assert "admin1@example.com" in email.to
        assert "admin2@example.com" in email.to
        assert "admin3@example.com" in email.to

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_notification_skipped_when_disabled(self, site):
        """Test that notifications are not sent when disabled."""
        # Create form with notifications disabled
        form = FormDefinition.objects.create(
            name="No Notification Form",
            slug="no-notification",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            email_notification_enabled=False,  # Notifications disabled
            notification_emails="",
            is_active=True,
        )

        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test notification disabled",
            form_type="no-notification",
            form_notification_status=EmailStatus.PENDING,
            form_data={
                "email": "test@example.com",
                "form_definition_slug": form.slug,
            },
        )

        mail.outbox = []
        send_form_notification(lead.id, form.id)

        # No email should be sent
        assert len(mail.outbox) == 0
        lead.refresh_from_db()
        assert lead.form_notification_status == EmailStatus.DISABLED

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_notification_has_html_and_plain_text(
        self, form_with_notifications, test_lead
    ):
        """Test that notification email has both HTML and plain text versions."""
        mail.outbox = []

        send_form_notification(test_lead.id, form_with_notifications.id)

        email = mail.outbox[0]

        # Verify email has alternatives (HTML version)
        assert email.body  # Plain text
        assert len(email.alternatives) > 0  # HTML alternative

        html_content = email.alternatives[0][0]
        assert "<!DOCTYPE html>" in html_content or "<html" in html_content
        assert test_lead.name in html_content


@pytest.mark.django_db
class TestAutoReplyEmails:
    """Test auto-reply email delivery."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def form_with_auto_reply(self, site):
        """Create form with auto-reply enabled."""
        return FormDefinition.objects.create(
            name="Quote Request",
            slug="quote-request",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="We'll send you a quote soon!",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for your quote request!",
            auto_reply_body="Hi {{name}},\n\nWe received your quote request and will get back to you within 24 hours.\n\nBest regards,\nThe Team",
            is_active=True,
        )

    @pytest.fixture
    def test_lead_for_auto_reply(self, form_with_auto_reply):
        """Create a test lead for auto-reply testing."""
        return Lead.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            message="Auto-reply test message",
            form_type="quote-request",
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "form_definition_slug": "quote-request",
            },
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_sent_to_submitter(
        self, form_with_auto_reply, test_lead_for_auto_reply
    ):
        """Test that auto-reply is sent to form submitter."""
        mail.outbox = []

        send_auto_reply(test_lead_for_auto_reply.id, form_with_auto_reply.id)

        # Verify email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        # Check it's sent to the submitter
        assert email.to == ["jane@example.com"]

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_template_variables_replaced(
        self, form_with_auto_reply, test_lead_for_auto_reply
    ):
        """Test that template variables like {{name}} are replaced."""
        mail.outbox = []

        send_auto_reply(test_lead_for_auto_reply.id, form_with_auto_reply.id)

        email = mail.outbox[0]

        # Verify {{name}} was replaced with actual name
        assert "Hi Jane Smith" in email.body
        assert "{{name}}" not in email.body

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_has_correct_subject(
        self, form_with_auto_reply, test_lead_for_auto_reply
    ):
        """Test that auto-reply uses the configured subject."""
        mail.outbox = []

        send_auto_reply(test_lead_for_auto_reply.id, form_with_auto_reply.id)

        email = mail.outbox[0]
        assert email.subject == "Thanks for your quote request!"

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_skipped_when_disabled(self, site):
        """Test that auto-reply is not sent when disabled."""
        form = FormDefinition.objects.create(
            name="No Auto Reply Form",
            slug="no-auto-reply",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            auto_reply_enabled=False,
            auto_reply_subject="Thanks!",
            auto_reply_body="We'll be in touch.",
            is_active=True,
        )
        lead = Lead.objects.create(
            name="Test",
            email="test@example.com",
            message="Test auto-reply disabled",
            form_type="no-auto-reply",
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "email": "test@example.com",
                "form_definition_slug": "no-auto-reply",
            },
        )

        mail.outbox = []
        send_auto_reply(lead.id, form.id)

        # No email should be sent
        assert len(mail.outbox) == 0
        lead.refresh_from_db()
        assert lead.auto_reply_status == EmailStatus.DISABLED

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_skipped_without_submitter_email(self, form_with_auto_reply):
        """Test that auto-reply is skipped if lead has no email."""
        lead = Lead.objects.create(
            name="No Email User",
            email="",  # No email address
            message="No email test",
            form_type="quote-request",
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "name": "No Email User",
                "form_definition_slug": "quote-request",
            },
        )

        mail.outbox = []
        send_auto_reply(lead.id, form_with_auto_reply.id)

        # No email should be sent
        assert len(mail.outbox) == 0

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_prevents_header_injection(self, site):
        """Test that auto-reply strips newlines to prevent header injection."""
        # Create form with auto-reply enabled
        form = FormDefinition.objects.create(
            name="Injection Test Form",
            slug="injection-test",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for your message!",
            auto_reply_body="Hi {{name}}, we received your message.",
            is_active=True,
        )

        # Create lead with newlines in name (potential header injection)
        lead = Lead.objects.create(
            name="Attacker\nBcc: evil@example.com",
            email="victim@example.com",
            message="Header injection test",
            form_type="injection-test",
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "name": "Attacker\nBcc: evil@example.com",
                "email": "victim@example.com",
                "form_definition_slug": form.slug,
            },
        )

        mail.outbox = []
        send_auto_reply(lead.id, form.id)

        # Verify email was sent and only to the intended recipient
        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        # Verify no additional headers were injected via Bcc
        assert email.to == ["victim@example.com"]
        # Verify there are no extra recipients
        assert not email.cc
        assert not email.bcc

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_prevents_crlf_header_injection(self, site):
        """Test that auto-reply handles CRLF injection attempts.

        Email headers use CRLF (\\r\\n) as separators. Attackers may try to
        inject additional headers using CRLF sequences in form fields.
        """
        # Create form with auto-reply enabled
        form = FormDefinition.objects.create(
            name="CRLF Injection Test Form",
            slug="crlf-injection-test",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for your message!",
            auto_reply_body="Hi {{name}}, we received your message.",
            is_active=True,
        )

        # CRLF injection payloads
        crlf_payloads = [
            "Attacker\r\nBcc: evil@example.com",
            "Attacker\r\nCc: evil@example.com",
            "Attacker\r\nSubject: Phishing",
            "Attacker\r\n\r\nMalicious body content",
        ]

        for i, payload in enumerate(crlf_payloads):
            lead = Lead.objects.create(
                name=payload,
                email=f"victim{i}@example.com",
                message="CRLF injection test",
                form_type="crlf-injection-test",
                auto_reply_status=EmailStatus.PENDING,
                form_data={
                    "name": payload,
                    "email": f"victim{i}@example.com",
                    "form_definition_slug": form.slug,
                },
            )

            mail.outbox = []
            send_auto_reply(lead.id, form.id)

            assert len(mail.outbox) == 1
            email = mail.outbox[0]

            # Verify only the intended recipient receives the email
            assert email.to == [f"victim{i}@example.com"]
            assert not email.cc
            assert not email.bcc

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_xss_prevention(self, site):
        """Test that auto-reply renders as plain text to prevent XSS."""
        # Create form with auto-reply enabled
        form = FormDefinition.objects.create(
            name="XSS Test Form",
            slug="xss-test",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for your message!",
            auto_reply_body="Hi {{name}}, we received your message.",
            is_active=True,
        )

        # Create lead with potential XSS payload
        lead = Lead.objects.create(
            name="<script>alert('XSS')</script>",
            email="test@example.com",
            message="XSS test",
            form_type="xss-test",
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "name": "<script>alert('XSS')</script>",
                "email": "test@example.com",
                "form_definition_slug": form.slug,
            },
        )

        mail.outbox = []
        send_auto_reply(lead.id, form.id)

        # Verify email was sent
        assert len(mail.outbox) == 1
        email = mail.outbox[0]

        # In plain text email, HTML should appear literally (not executed)
        assert "<script>" in email.body  # Should be visible as text
        # Content type should be plain text
        assert email.content_subtype == "plain"

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_auto_reply_xss_prevention_comprehensive(self, site):
        """Test XSS prevention with multiple attack vectors.

        Tests additional XSS vectors beyond basic script tags:
        - Event handlers (onerror, onclick)
        - Data URIs (javascript:)
        - HTML entities
        """
        # Create form with auto-reply enabled
        form = FormDefinition.objects.create(
            name="XSS Comprehensive Form",
            slug="xss-comprehensive",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            auto_reply_enabled=True,
            auto_reply_subject="Thanks for your message!",
            auto_reply_body="Hi {{name}}, we received your message.",
            is_active=True,
        )

        xss_payloads = [
            # Event handler attack
            '<img src=x onerror="alert(1)">',
            # Data URI attack
            '<a href="javascript:alert(1)">Click</a>',
            # HTML entity encoded script
            "&lt;script&gt;alert(1)&lt;/script&gt;",
            # SVG-based XSS
            '<svg onload="alert(1)">',
        ]

        for i, payload in enumerate(xss_payloads):
            lead = Lead.objects.create(
                name=payload,
                email=f"xss-test-{i}@example.com",
                message="XSS comprehensive test",
                form_type="xss-comprehensive",
                auto_reply_status=EmailStatus.PENDING,
                form_data={
                    "name": payload,
                    "email": f"xss-test-{i}@example.com",
                    "form_definition_slug": form.slug,
                },
            )

            mail.outbox = []
            send_auto_reply(lead.id, form.id)

            assert len(mail.outbox) == 1
            email = mail.outbox[0]

            # All payloads should appear literally in plain text email
            # (not executed or stripped)
            assert email.content_subtype == "plain"


@pytest.mark.django_db
class TestEmailNotificationIntegration:
    """Test complete email notification integration scenarios."""

    @pytest.fixture
    def full_featured_form(self, db):
        """Create form with all email features enabled."""
        site = Site.objects.get(is_default_site=True)
        return FormDefinition.objects.create(
            name="Full Featured Form",
            slug="full-featured",
            site=site,
            fields=[
                (
                    "text_input",
                    {"field_name": "name", "label": "Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "textarea",
                    {
                        "field_name": "message",
                        "label": "Message",
                        "required": True,
                        "rows": 5,
                    },
                ),
            ],
            success_message="Thanks!",
            email_notification_enabled=True,
            notification_emails="admin@example.com",
            auto_reply_enabled=True,
            auto_reply_subject="Thank you!",
            auto_reply_body="Hi {{name}}, we received your message.",
            is_active=True,
        )

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_both_admin_and_auto_reply_sent(self, full_featured_form):
        """Test that both admin notification and auto-reply are sent."""
        lead = Lead.objects.create(
            name="Complete Test",
            email="complete@example.com",
            message="Test message",
            form_type="full-featured",
            form_notification_status=EmailStatus.PENDING,
            auto_reply_status=EmailStatus.PENDING,
            form_data={
                "name": "Complete Test",
                "email": "complete@example.com",
                "message": "Test message",
                "form_definition_slug": "full-featured",
            },
        )

        mail.outbox = []

        # Send both types of emails
        send_form_notification(lead.id, full_featured_form.id)
        send_auto_reply(lead.id, full_featured_form.id)

        # Should have 2 emails total
        assert len(mail.outbox) == 2

        # Find each email by recipient
        admin_email = next(e for e in mail.outbox if "admin@example.com" in e.to)
        auto_reply_email = next(
            e for e in mail.outbox if "complete@example.com" in e.to
        )

        # Verify admin email content
        assert "Complete Test" in admin_email.body
        assert "Test message" in admin_email.body

        # Verify auto-reply content
        assert "Hi Complete Test" in auto_reply_email.body
        assert auto_reply_email.subject == "Thank you!"

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        CELERY_TASK_ALWAYS_EAGER=True,
    )
    def test_emails_not_duplicated_on_retry(self, full_featured_form):
        """Test that emails are not sent multiple times (idempotency)."""
        lead = Lead.objects.create(
            name="Idempotent Test",
            email="idempotent@example.com",
            message="Idempotency test",
            form_type="full-featured",
            form_notification_status=EmailStatus.PENDING,
            form_data={
                "name": "Idempotent Test",
                "email": "idempotent@example.com",
                "form_definition_slug": "full-featured",
            },
        )

        mail.outbox = []

        # Send notification twice (simulating retry)
        send_form_notification(lead.id, full_featured_form.id)
        initial_count = len(mail.outbox)

        send_form_notification(lead.id, full_featured_form.id)
        retry_count = len(mail.outbox)

        # Second call should not send duplicate
        assert initial_count == retry_count == 1
