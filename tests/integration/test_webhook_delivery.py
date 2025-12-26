"""
Integration tests for webhook delivery.

Tests the complete webhook firing flow including payload structure,
retry logic, and security measures, with proper mocking of HTTP requests.
"""

import json

import pytest
import responses
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import send_webhook
from sum_core.leads.models import Lead, WebhookStatus
from wagtail.models import Site


@pytest.mark.django_db
class TestWebhookDelivery:
    """Test webhook delivery to external endpoints."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    @pytest.fixture
    def form_with_webhook(self, site):
        """Create form with webhook enabled."""
        return FormDefinition.objects.create(
            name="Webhook Form",
            slug="webhook-form",
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
            webhook_enabled=True,
            webhook_url="https://hooks.example.com/lead",
            is_active=True,
        )

    @pytest.fixture
    def test_lead(self, form_with_webhook):
        """Create a test lead for webhook testing."""
        return Lead.objects.create(
            name="Webhook User",
            email="webhook@example.com",
            phone="555-9999",
            message="Test webhook delivery",
            form_type="webhook-form",
            page_url="https://example.com/contact",
            landing_page_url="https://example.com",
            utm_source="facebook",
            utm_medium="social",
            utm_campaign="summer-2024",
            utm_content="ad-1",
            utm_term="services",
            referrer_url="https://facebook.com",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "name": "Webhook User",
                "email": "webhook@example.com",
                "form_definition_slug": "webhook-form",
            },
        )

    @responses.activate
    def test_webhook_fires_successfully(self, form_with_webhook, test_lead):
        """Test that webhook is fired to the configured URL."""
        # Mock the webhook endpoint
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        # Fire webhook
        send_webhook(test_lead.id, form_with_webhook.id)

        # Verify webhook was called
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://hooks.example.com/lead"

    @responses.activate
    def test_webhook_payload_structure(self, form_with_webhook, test_lead):
        """Test that webhook payload has correct structure."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        send_webhook(test_lead.id, form_with_webhook.id)

        # Parse the sent payload
        request_body = responses.calls[0].request.body
        payload = json.loads(request_body)

        # Verify payload structure
        assert "event" in payload
        assert payload["event"] == "form.submitted"

        assert "form" in payload
        assert payload["form"]["name"] == "Webhook Form"
        assert payload["form"]["slug"] == "webhook-form"

        assert "submission" in payload
        assert payload["submission"]["id"] == test_lead.id
        assert payload["submission"]["contact"]["name"] == "Webhook User"
        assert payload["submission"]["contact"]["email"] == "webhook@example.com"
        assert payload["submission"]["contact"]["phone"] == "555-9999"
        assert payload["submission"]["contact"]["message"] == "Test webhook delivery"
        assert payload["submission"]["data"]["name"] == "Webhook User"

        assert "attribution" in payload
        assert payload["attribution"]["utm_source"] == "facebook"
        assert payload["attribution"]["utm_medium"] == "social"
        assert payload["attribution"]["utm_campaign"] == "summer-2024"
        assert payload["attribution"]["utm_content"] == "ad-1"
        assert payload["attribution"]["utm_term"] == "services"
        assert payload["attribution"]["source_url"] == "https://example.com/contact"
        assert payload["attribution"]["landing_page"] == "https://example.com"

    @responses.activate
    def test_webhook_includes_request_id(self, form_with_webhook, test_lead):
        """Test that webhook payload includes request ID for tracking."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        request_id = "req-123"
        send_webhook(test_lead.id, form_with_webhook.id, request_id=request_id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify request ID is present
        assert payload["request_id"] == request_id

    @responses.activate
    def test_webhook_includes_timestamp(self, form_with_webhook, test_lead):
        """Test that webhook payload includes timestamp."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        send_webhook(test_lead.id, form_with_webhook.id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify timestamp is present
        assert "timestamp" in payload
        # Timestamp should be ISO format
        from datetime import datetime

        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))

    @responses.activate
    def test_webhook_skipped_when_disabled(self, site):
        """Test that webhook is not fired when disabled."""
        # Create form with webhook disabled
        form = FormDefinition.objects.create(
            name="No Webhook Form",
            slug="no-webhook",
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
            webhook_enabled=False,  # Webhook disabled
            webhook_url="",
            is_active=True,
        )

        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test webhook message",
            form_type="no-webhook",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "email": "test@example.com",
                "form_definition_slug": form.slug,
            },
        )

        # Fire webhook (should be skipped)
        send_webhook(lead.id, form.id)

        # No HTTP request should have been made
        assert len(responses.calls) == 0
        lead.refresh_from_db()
        assert lead.form_webhook_status == WebhookStatus.DISABLED

    @responses.activate
    def test_webhook_skipped_without_url(self, site):
        """Test that webhook is skipped if no URL is configured."""
        # Create form with webhook enabled but no URL
        form = FormDefinition.objects.create(
            name="No URL Form",
            slug="no-url",
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
            webhook_enabled=True,  # Enabled but no URL
            webhook_url="",
            is_active=True,
        )

        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test webhook message",
            form_type="no-url",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "email": "test@example.com",
                "form_definition_slug": form.slug,
            },
        )

        send_webhook(lead.id, form.id)

        # No HTTP request should have been made
        assert len(responses.calls) == 0
        lead.refresh_from_db()
        assert lead.form_webhook_status == WebhookStatus.FAILED

    @responses.activate
    def test_webhook_retry_on_failure(self, form_with_webhook, test_lead):
        """Test that webhook is retried on failure."""
        # Mock endpoint to fail first, then succeed
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"error": "Server error"},
            status=500,
        )

        with pytest.raises(Exception):
            # Should raise exception to trigger Celery retry
            send_webhook(test_lead.id, form_with_webhook.id)

        # Verify request was made despite failure
        assert len(responses.calls) == 1
        test_lead.refresh_from_db()
        assert test_lead.form_webhook_status == WebhookStatus.IN_PROGRESS
        assert test_lead.form_webhook_last_status_code == 500

    @responses.activate
    def test_webhook_timeout_handling(self, form_with_webhook, test_lead):
        """Test that webhook handles timeout gracefully."""
        import requests

        # Mock timeout exception
        def request_callback(request):
            raise requests.exceptions.Timeout("Connection timeout")

        responses.add_callback(
            responses.POST,
            "https://hooks.example.com/lead",
            callback=request_callback,
        )

        with pytest.raises(requests.exceptions.Timeout):
            send_webhook(test_lead.id, form_with_webhook.id)

        assert len(responses.calls) == 1
        test_lead.refresh_from_db()
        assert test_lead.form_webhook_status == WebhookStatus.IN_PROGRESS

    @responses.activate
    def test_webhook_blocks_private_urls(self, site):
        """Test that webhooks to private IP addresses are blocked (SSRF protection)."""
        private_urls = [
            "http://localhost:8000/webhook",
            "http://127.0.0.1/webhook",
            "http://10.0.0.1/webhook",
            "http://192.168.1.1/webhook",
            "http://172.16.0.1/webhook",
        ]

        for i, url in enumerate(private_urls):
            # Create form with private URL
            slug = f"private-test-{i}"
            form = FormDefinition.objects.create(
                name=f"Private URL Test {i}",
                slug=slug,
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
                webhook_enabled=True,
                webhook_url=url,  # Private URL that should be blocked
                is_active=True,
            )

            lead = Lead.objects.create(
                name="Test User",
                email=f"test{i}@example.com",
                message="Test SSRF protection",
                form_type=slug,
                form_webhook_status=WebhookStatus.PENDING,
                form_data={
                    "email": f"test{i}@example.com",
                    "form_definition_slug": slug,
                },
            )

            # Webhook should be blocked
            send_webhook(lead.id, form.id)
            lead.refresh_from_db()
            assert lead.form_webhook_status == WebhookStatus.FAILED
            assert lead.form_webhook_last_error

    @responses.activate
    def test_webhook_includes_form_data(self, form_with_webhook, test_lead):
        """Test that webhook includes complete form_data field."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        send_webhook(test_lead.id, form_with_webhook.id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify form_data is included
        assert "data" in payload["submission"]
        assert payload["submission"]["data"]["name"] == "Webhook User"
        assert payload["submission"]["data"]["email"] == "webhook@example.com"

    @responses.activate
    def test_webhook_handles_missing_optional_fields(self, form_with_webhook):
        """Test webhook payload when optional fields are missing."""
        # Create lead with minimal data
        lead = Lead.objects.create(
            name="Minimal User",
            email="minimal@example.com",
            message="Minimal message",
            form_type="webhook-form",
            # No phone or attribution data
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "name": "Minimal User",
                "email": "minimal@example.com",
                "form_definition_slug": "webhook-form",
            },
        )

        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        send_webhook(lead.id, form_with_webhook.id)

        payload = json.loads(responses.calls[0].request.body)

        # Payload should still be valid
        assert payload["submission"]["contact"]["name"] == "Minimal User"
        assert payload["submission"]["contact"]["email"] == "minimal@example.com"
        assert payload["submission"]["contact"]["message"] == "Minimal message"
        # Optional attribution fields should be null or empty
        assert payload["submission"]["contact"]["phone"] in [None, ""]
        assert payload["attribution"]["utm_source"] in [None, ""]


@pytest.mark.django_db
class TestWebhookIntegrationScenarios:
    """Test complete webhook integration scenarios."""

    @pytest.fixture
    def zapier_form(self, db):
        """Create form configured for Zapier integration."""
        site = Site.objects.get(is_default_site=True)
        return FormDefinition.objects.create(
            name="Zapier Integration",
            slug="zapier",
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
                    "phone_input",
                    {"field_name": "phone", "label": "Phone", "required": False},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="Thanks!",
            webhook_enabled=True,
            webhook_url="https://hooks.zapier.com/hooks/catch/123456/abcdef/",
            is_active=True,
        )

    @responses.activate
    def test_zapier_webhook_integration(self, zapier_form):
        """Test webhook integration with Zapier."""
        responses.add(
            responses.POST,
            "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
            json={"status": "success"},
            status=200,
        )

        lead = Lead.objects.create(
            name="Zapier User",
            email="zapier@example.com",
            phone="555-0000",
            message="Zapier integration test",
            form_type="zapier",
            utm_source="google",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "name": "Zapier User",
                "email": "zapier@example.com",
                "phone": "555-0000",
                "form_definition_slug": "zapier",
            },
        )

        send_webhook(lead.id, zapier_form.id)

        # Verify Zapier was called
        assert len(responses.calls) == 1
        payload = json.loads(responses.calls[0].request.body)

        # Zapier expects specific structure
        assert payload["event"] == "form.submitted"
        assert payload["form"]["name"] == "Zapier Integration"
        assert payload["submission"]["contact"]["email"] == "zapier@example.com"

    @pytest.fixture
    def hubspot_form(self, db):
        """Create form configured for HubSpot integration."""
        site = Site.objects.get(is_default_site=True)
        return FormDefinition.objects.create(
            name="HubSpot Integration",
            slug="hubspot",
            site=site,
            fields=[
                (
                    "text_input",
                    {
                        "field_name": "first_name",
                        "label": "First Name",
                        "required": True,
                    },
                ),
                (
                    "text_input",
                    {"field_name": "last_name", "label": "Last Name", "required": True},
                ),
                (
                    "email_input",
                    {"field_name": "email", "label": "Email", "required": True},
                ),
                (
                    "text_input",
                    {"field_name": "company", "label": "Company", "required": False},
                ),
                (
                    "textarea",
                    {"field_name": "message", "label": "Message", "required": True},
                ),
            ],
            success_message="We'll be in touch!",
            webhook_enabled=True,
            webhook_url="https://api.hubspot.com/webhooks/v1/integration",
            is_active=True,
        )

    @responses.activate
    def test_hubspot_webhook_integration(self, hubspot_form):
        """Test webhook integration with HubSpot."""
        responses.add(
            responses.POST,
            "https://api.hubspot.com/webhooks/v1/integration",
            json={"success": True},
            status=200,
        )

        lead = Lead.objects.create(
            name="John Doe",
            email="john@company.com",
            message="HubSpot integration test",
            form_type="hubspot",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@company.com",
                "company": "Acme Corp",
                "form_definition_slug": "hubspot",
            },
        )

        send_webhook(lead.id, hubspot_form.id)

        # Verify HubSpot was called
        assert len(responses.calls) == 1
        payload = json.loads(responses.calls[0].request.body)

        # HubSpot receives form data
        assert payload["submission"]["data"]["first_name"] == "John"
        assert payload["submission"]["data"]["last_name"] == "Doe"
        assert payload["submission"]["data"]["company"] == "Acme Corp"

    @responses.activate
    def test_webhook_idempotency(self, zapier_form):
        """Test that webhooks are not fired multiple times (idempotency)."""
        responses.add(
            responses.POST,
            "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
            json={"status": "success"},
            status=200,
        )

        lead = Lead.objects.create(
            name="Idempotent Test",
            email="idempotent@example.com",
            message="Testing idempotency",
            form_type="zapier",
            form_webhook_status=WebhookStatus.PENDING,
            form_data={
                "name": "Idempotent Test",
                "email": "idempotent@example.com",
                "form_definition_slug": "zapier",
            },
        )

        # Verify webhook_sent_at is initially not set
        assert lead.form_webhook_sent_at is None

        # Fire webhook first time
        send_webhook(lead.id, zapier_form.id)
        initial_count = len(responses.calls)

        # Refresh from database and verify webhook_sent_at was set
        lead.refresh_from_db()
        assert lead.form_webhook_sent_at is not None
        first_sent_at = lead.form_webhook_sent_at

        # Fire webhook second time (simulating retry)
        send_webhook(lead.id, zapier_form.id)
        retry_count = len(responses.calls)

        # Refresh and verify webhook_sent_at didn't change
        lead.refresh_from_db()
        assert lead.form_webhook_sent_at == first_sent_at

        # Second call should not fire duplicate webhook
        assert initial_count == retry_count == 1

    @responses.activate
    def test_webhook_with_different_status_codes(self, zapier_form):
        """Test webhook behavior with various HTTP status codes."""
        # Test 2xx success codes
        for status in [200, 201, 202, 204]:
            responses.reset()
            responses.add(
                responses.POST,
                "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
                status=status,
            )

            # Should succeed without exception
            lead = Lead.objects.create(
                name="Status Test",
                email="status@example.com",
                message="Testing status codes",
                form_type="zapier",
                form_webhook_status=WebhookStatus.PENDING,
                form_data={
                    "email": "status@example.com",
                    "form_definition_slug": "zapier",
                },
            )
            send_webhook(lead.id, zapier_form.id)
            assert len(responses.calls) == 1

        # Test error codes that should raise exceptions
        for status in [400, 401, 403, 404, 500, 502, 503]:
            responses.reset()
            responses.add(
                responses.POST,
                "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
                status=status,
            )

            with pytest.raises(Exception):
                lead = Lead.objects.create(
                    name="Status Test",
                    email="status@example.com",
                    message="Testing status codes",
                    form_type="zapier",
                    form_webhook_status=WebhookStatus.PENDING,
                    form_data={
                        "email": "status@example.com",
                        "form_definition_slug": "zapier",
                    },
                )
                send_webhook(lead.id, zapier_form.id)


@pytest.mark.django_db
class TestWebhookSecurityEdgeCases:
    """Test security measures for webhook delivery."""

    @pytest.fixture
    def site(self):
        """Get the default test site."""
        return Site.objects.get(is_default_site=True)

    def test_webhook_prevents_ssrf_to_metadata_endpoints(self, site):
        """Test that webhooks cannot target cloud metadata endpoints."""
        metadata_urls = [
            "http://169.254.169.254/latest/meta-data/",  # AWS
            "http://metadata.google.internal/",  # GCP
        ]

        for i, url in enumerate(metadata_urls):
            # Create form with metadata URL
            slug = f"metadata-test-{i}"
            form = FormDefinition.objects.create(
                name=f"Metadata URL Test {i}",
                slug=slug,
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
                webhook_enabled=True,
                webhook_url=url,  # Metadata URL that should be blocked
                is_active=True,
            )

            lead = Lead.objects.create(
                name="Test User",
                email=f"metadata{i}@example.com",
                message="Testing SSRF to metadata endpoint",
                form_type=slug,
                form_webhook_status=WebhookStatus.PENDING,
                form_data={
                    "email": f"metadata{i}@example.com",
                    "form_definition_slug": slug,
                },
            )

            # Should block metadata endpoint access
            send_webhook(lead.id, form.id)
            lead.refresh_from_db()
            assert lead.form_webhook_status == WebhookStatus.FAILED
