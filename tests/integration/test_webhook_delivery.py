"""
Integration tests for webhook delivery.

Tests the complete webhook firing flow including payload structure,
retry logic, and security measures, with proper mocking of HTTP requests.
"""

import json

import pytest
import responses
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import fire_webhook
from sum_core.leads.models import Lead
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
                ("text_input", {"label": "Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
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
            form_data={
                "Name": "Webhook User",
                "Email": "webhook@example.com",
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
        fire_webhook(test_lead.id)

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

        fire_webhook(test_lead.id)

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
        assert payload["submission"]["name"] == "Webhook User"
        assert payload["submission"]["email"] == "webhook@example.com"
        assert payload["submission"]["phone"] == "555-9999"
        assert payload["submission"]["message"] == "Test webhook delivery"

        assert "attribution" in payload
        assert payload["attribution"]["utm_source"] == "facebook"
        assert payload["attribution"]["utm_medium"] == "social"
        assert payload["attribution"]["utm_campaign"] == "summer-2024"
        assert payload["attribution"]["utm_content"] == "ad-1"
        assert payload["attribution"]["utm_term"] == "services"
        assert payload["attribution"]["referrer"] == "https://facebook.com"
        assert payload["attribution"]["page_url"] == "https://example.com/contact"
        assert payload["attribution"]["landing_page_url"] == "https://example.com"

    @responses.activate
    def test_webhook_includes_request_id(self, form_with_webhook, test_lead):
        """Test that webhook payload includes request ID for tracking."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        fire_webhook(test_lead.id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify request ID is present
        assert "request_id" in payload
        assert isinstance(payload["request_id"], str)
        assert len(payload["request_id"]) > 0

    @responses.activate
    def test_webhook_includes_timestamp(self, form_with_webhook, test_lead):
        """Test that webhook payload includes timestamp."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        fire_webhook(test_lead.id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify timestamp is present
        assert "timestamp" in payload
        # Timestamp should be ISO format
        from datetime import datetime

        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))

    @responses.activate
    def test_webhook_skipped_when_disabled(self, site):
        """Test that webhook is not fired when disabled."""
        # Note: This test requires form_definition ForeignKey on Lead model (not yet implemented)
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test webhook message",
            form_type="no-webhook",
            form_data={"Email": "test@example.com"},
        )

        # Fire webhook (should be skipped)
        fire_webhook(lead.id)

        # No HTTP request should have been made
        assert len(responses.calls) == 0

    @responses.activate
    def test_webhook_skipped_without_url(self, site):
        """Test that webhook is skipped if no URL is configured."""
        # Note: This test requires form_definition ForeignKey on Lead model (not yet implemented)
        lead = Lead.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test webhook message",
            form_type="no-url",
            form_data={"Email": "test@example.com"},
        )

        fire_webhook(lead.id)

        # No HTTP request should have been made
        assert len(responses.calls) == 0

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
            fire_webhook(test_lead.id)

        # Verify request was made despite failure
        assert len(responses.calls) == 1

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
            fire_webhook(test_lead.id)

        assert len(responses.calls) == 1

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

        for url in private_urls:
            # Note: This test requires form_definition ForeignKey on Lead model (not yet implemented)
            lead = Lead.objects.create(
                name="Test User",
                email="test@example.com",
                message="Test SSRF protection",
                form_type=f"private-{url.replace('/', '-').replace(':', '-')}",
                form_data={"Email": "test@example.com"},
            )

            # Webhook should be blocked
            with pytest.raises(ValueError, match="private|localhost|local"):
                fire_webhook(lead.id)

    @responses.activate
    def test_webhook_includes_form_data(self, form_with_webhook, test_lead):
        """Test that webhook includes complete form_data field."""
        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        fire_webhook(test_lead.id)

        payload = json.loads(responses.calls[0].request.body)

        # Verify form_data is included
        assert "form_data" in payload["submission"]
        assert payload["submission"]["form_data"]["Name"] == "Webhook User"
        assert payload["submission"]["form_data"]["Email"] == "webhook@example.com"

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
            form_data={
                "Name": "Minimal User",
                "Email": "minimal@example.com",
                "form_definition_slug": "webhook-form",
            },
        )

        responses.add(
            responses.POST,
            "https://hooks.example.com/lead",
            json={"success": True},
            status=200,
        )

        fire_webhook(lead.id)

        payload = json.loads(responses.calls[0].request.body)

        # Payload should still be valid
        assert payload["submission"]["name"] == "Minimal User"
        assert payload["submission"]["email"] == "minimal@example.com"
        assert payload["submission"]["message"] == "Minimal message"
        # Optional attribution fields should be null or empty
        assert payload["submission"]["phone"] in [None, ""]
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
                ("text_input", {"label": "Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
                ("phone_input", {"label": "Phone", "required": False}),
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
            form_data={
                "Name": "Zapier User",
                "Email": "zapier@example.com",
                "Phone": "555-0000",
                "form_definition_slug": "zapier",
            },
        )

        fire_webhook(lead.id)

        # Verify Zapier was called
        assert len(responses.calls) == 1
        payload = json.loads(responses.calls[0].request.body)

        # Zapier expects specific structure
        assert payload["event"] == "form.submitted"
        assert payload["form"]["name"] == "Zapier Integration"
        assert payload["submission"]["email"] == "zapier@example.com"

    @pytest.fixture
    def hubspot_form(self, db):
        """Create form configured for HubSpot integration."""
        site = Site.objects.get(is_default_site=True)
        return FormDefinition.objects.create(
            name="HubSpot Integration",
            slug="hubspot",
            site=site,
            fields=[
                ("text_input", {"label": "First Name", "required": True}),
                ("text_input", {"label": "Last Name", "required": True}),
                ("email_input", {"label": "Email", "required": True}),
                ("text_input", {"label": "Company", "required": False}),
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
            form_data={
                "First Name": "John",
                "Last Name": "Doe",
                "Email": "john@company.com",
                "Company": "Acme Corp",
                "form_definition_slug": "hubspot",
            },
        )

        fire_webhook(lead.id)

        # Verify HubSpot was called
        assert len(responses.calls) == 1
        payload = json.loads(responses.calls[0].request.body)

        # HubSpot receives form data
        assert payload["submission"]["form_data"]["First Name"] == "John"
        assert payload["submission"]["form_data"]["Last Name"] == "Doe"
        assert payload["submission"]["form_data"]["Company"] == "Acme Corp"

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
            form_data={
                "Name": "Idempotent Test",
                "Email": "idempotent@example.com",
                "form_definition_slug": "zapier",
            },
        )

        # Fire webhook twice (simulating retry)
        fire_webhook(lead.id)
        initial_count = len(responses.calls)

        fire_webhook(lead.id)
        retry_count = len(responses.calls)

        # Second call should not fire duplicate webhook
        assert initial_count == retry_count == 1

    @responses.activate
    def test_webhook_with_different_status_codes(self, zapier_form):
        """Test webhook behavior with various HTTP status codes."""
        lead = Lead.objects.create(
            name="Status Test",
            email="status@example.com",
            message="Testing status codes",
            form_type="zapier",
            form_data={
                "Email": "status@example.com",
                "form_definition_slug": "zapier",
            },
        )

        # Test 2xx success codes
        for status in [200, 201, 202, 204]:
            responses.reset()
            responses.add(
                responses.POST,
                "https://hooks.zapier.com/hooks/catch/123456/abcdef/",
                status=status,
            )

            # Should succeed without exception
            fire_webhook(lead.id)
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
                fire_webhook(lead.id)


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

        for url in metadata_urls:
            # Note: This test requires form_definition ForeignKey on Lead model (not yet implemented)
            lead = Lead.objects.create(
                name="Test User",
                email="test@example.com",
                message="Testing SSRF to metadata endpoint",
                form_type=f"ssrf-{url.replace('/', '-')}",
                form_data={"Email": "test@example.com"},
            )

            # Should block metadata endpoint access
            with pytest.raises(ValueError):
                fire_webhook(lead.id)
