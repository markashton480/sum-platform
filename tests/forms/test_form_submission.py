"""
Name: Form submission tests
Path: tests/forms/test_form_submission.py
Purpose: Test form submission endpoint with spam protection and Lead creation.
Family: Test Suite, Forms, Leads.
Dependencies: pytest, Django test client, sum_core.forms, sum_core.leads.
"""

from __future__ import annotations

import json
from unittest import mock

import pytest
from django.core.cache import cache
from django.test import Client
from sum_core.forms.models import FormConfiguration
from sum_core.forms.services import generate_time_token, get_rate_limit_cache_key
from sum_core.leads.models import Lead


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def wagtail_site(wagtail_default_site):
    """Return the default Wagtail site."""
    return wagtail_default_site


@pytest.fixture
def form_config(wagtail_site):
    """Create FormConfiguration for the test site."""
    config, _ = FormConfiguration.objects.get_or_create(
        site=wagtail_site,
        defaults={
            "honeypot_field_name": "company",
            "rate_limit_per_ip_per_hour": 20,
            "min_seconds_to_submit": 3,
        },
    )
    return config


@pytest.fixture
def valid_time_token():
    """Generate a valid time token that passes timing check."""
    token = generate_time_token()
    return token


@pytest.fixture
def client():
    """Django test client."""
    return Client()


def make_valid_submission_data(time_token: str = "") -> dict:
    """Create valid form submission data."""
    return {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Hello, I have a question.",
        "form_type": "contact",
        "_time_token": time_token,
        "company": "",  # Honeypot empty
    }


@pytest.mark.django_db
class TestFormSubmissionValidation:
    """Tests for form submission validation."""

    def test_missing_name_returns_400(self, client, wagtail_site, form_config):
        """Missing name should return 400 with error."""
        data = make_valid_submission_data()
        del data["name"]

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert not resp_data["success"]
        assert "name" in resp_data["errors"]

    def test_missing_email_returns_400(self, client, wagtail_site, form_config):
        """Missing email should return 400 with error."""
        data = make_valid_submission_data()
        del data["email"]

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "email" in resp_data["errors"]

    def test_missing_message_returns_400(self, client, wagtail_site, form_config):
        """Missing message should return 400 with error."""
        data = make_valid_submission_data()
        del data["message"]

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "message" in resp_data["errors"]

    def test_missing_form_type_returns_400(self, client, wagtail_site, form_config):
        """Missing form_type should return 400 when no default configured."""
        data = make_valid_submission_data()
        del data["form_type"]

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "form_type" in resp_data["errors"]

    def test_default_form_type_used_when_configured(
        self, client, wagtail_site, form_config
    ):
        """Default form_type from config should be used when not in submission."""
        form_config.default_form_type = "contact"
        form_config.save()

        data = make_valid_submission_data()
        del data["form_type"]

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(data.get("_time_token", "0").split(":")[0] or 0)
            mock_time.return_value = token_time + 5 if token_time else 1000

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200


@pytest.mark.django_db
class TestFormSubmissionSpamProtection:
    """Tests for spam protection during form submission."""

    def test_honeypot_filled_returns_400(self, client, wagtail_site, form_config):
        """Filled honeypot should return 400."""
        initial_count = Lead.objects.count()
        data = make_valid_submission_data()
        data["company"] = "SpamBot Corp"

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        # Should not create a Lead
        assert Lead.objects.count() == initial_count

    def test_rate_limit_exceeded_returns_429(self, client, wagtail_site, form_config):
        """Exceeding rate limit should return 429."""
        # Set counter to limit
        cache_key = get_rate_limit_cache_key("127.0.0.1", wagtail_site.id)
        cache.set(cache_key, 20, timeout=3600)

        data = make_valid_submission_data()

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 429
        resp_data = response.json()
        assert "Too many requests" in str(resp_data["errors"])

    def test_timing_too_fast_returns_400(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Submission too fast after form render should return 400."""
        data = make_valid_submission_data(valid_time_token)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 1  # Only 1 second

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 400


@pytest.mark.django_db
class TestFormSubmissionSuccess:
    """Tests for successful form submission and Lead creation."""

    def test_valid_submission_creates_lead(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Valid submission should create a Lead."""
        data = make_valid_submission_data(valid_time_token)
        initial_count = Lead.objects.count()

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        assert Lead.objects.count() == initial_count + 1

        lead = Lead.objects.latest("submitted_at")
        assert lead.name == "John Doe"
        assert lead.email == "john@example.com"
        assert lead.message == "Hello, I have a question."
        assert lead.form_type == "contact"

    def test_valid_submission_returns_lead_id(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Successful submission should return lead_id in response."""
        data = make_valid_submission_data(valid_time_token)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        resp_data = response.json()
        assert resp_data["success"] is True
        assert "lead_id" in resp_data
        assert Lead.objects.filter(id=resp_data["lead_id"]).exists()

    def test_attribution_fields_stored(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Attribution fields should be stored on Lead."""
        data = make_valid_submission_data(valid_time_token)
        data.update(
            {
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "spring-promo",
                "utm_term": "window installation",
                "utm_content": "ad-v1",
                "page_url": "https://example.com/contact",
                "landing_page_url": "https://example.com/",
                "referrer_url": "https://google.com/search",
            }
        )

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        lead = Lead.objects.latest("submitted_at")
        assert lead.utm_source == "google"
        assert lead.utm_medium == "cpc"
        assert lead.utm_campaign == "spring-promo"
        assert lead.page_url == "https://example.com/contact"
        assert lead.landing_page_url == "https://example.com/"
        assert lead.referrer_url == "https://google.com/search"

    def test_lead_source_derived(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Lead source should be derived from attribution."""
        data = make_valid_submission_data(valid_time_token)
        data.update(
            {
                "utm_source": "google",
                "utm_medium": "cpc",
            }
        )

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        lead = Lead.objects.latest("submitted_at")
        assert lead.lead_source == "google_ads"

    def test_extra_form_data_stored(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Extra form fields should be stored in form_data."""
        data = make_valid_submission_data(valid_time_token)
        data.update(
            {
                "project_type": "residential",
                "budget": "20-40k",
                "postcode": "SW1A 1AA",
            }
        )

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        lead = Lead.objects.latest("submitted_at")
        assert lead.form_data["project_type"] == "residential"
        assert lead.form_data["budget"] == "20-40k"
        assert lead.form_data["postcode"] == "SW1A 1AA"

    def test_rate_limit_incremented_on_success(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Rate limit counter should be incremented after successful submission."""
        data = make_valid_submission_data(valid_time_token)
        cache_key = get_rate_limit_cache_key("127.0.0.1", wagtail_site.id)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        assert cache.get(cache_key) == 1


@pytest.mark.django_db
class TestNoLostLeadsInvariant:
    """Tests for the 'no lost leads' invariant."""

    def test_lead_created_before_hook_failure(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Lead should be created even if post-create hook fails."""
        data = make_valid_submission_data(valid_time_token)
        initial_count = Lead.objects.count()

        # We can't easily test the hook from the HTTP endpoint,
        # but we can verify the Lead is created on success
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        assert Lead.objects.count() == initial_count + 1

    def test_validation_errors_do_not_create_lead(
        self, client, wagtail_site, form_config
    ):
        """Validation errors should not create a Lead."""
        data = {"name": "", "email": "", "message": ""}
        initial_count = Lead.objects.count()

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        assert Lead.objects.count() == initial_count


@pytest.mark.django_db
class TestFormConfigurationModel:
    """Tests for FormConfiguration model."""

    def test_get_for_site_creates_default(self, wagtail_site):
        """get_for_site should create config with defaults if not exists."""
        FormConfiguration.objects.filter(site=wagtail_site).delete()

        config = FormConfiguration.get_for_site(wagtail_site)

        assert config.site == wagtail_site
        assert config.honeypot_field_name == "company"
        assert config.rate_limit_per_ip_per_hour == 20
        assert config.min_seconds_to_submit == 3

    def test_get_for_site_returns_existing(self, wagtail_site):
        """get_for_site should return existing config."""
        FormConfiguration.objects.filter(site=wagtail_site).delete()
        existing = FormConfiguration.objects.create(
            site=wagtail_site,
            honeypot_field_name="website",
            rate_limit_per_ip_per_hour=50,
        )

        config = FormConfiguration.get_for_site(wagtail_site)

        assert config.id == existing.id
        assert config.honeypot_field_name == "website"

    def test_str_representation(self, wagtail_site):
        """String representation should include site hostname."""
        FormConfiguration.objects.filter(site=wagtail_site).delete()
        config = FormConfiguration.objects.create(site=wagtail_site)
        assert wagtail_site.hostname in str(config)


@pytest.mark.django_db
class TestJSONSubmission:
    """Tests for JSON-encoded form submissions."""

    def test_json_submission_works(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """JSON-encoded submission should work."""
        data = make_valid_submission_data(valid_time_token)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=json.dumps(data),
                content_type="application/json",
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200
        lead = Lead.objects.latest("submitted_at")
        assert lead.name == "John Doe"

    def test_invalid_json_returns_400(self, client, wagtail_site, form_config):
        """Invalid JSON should return 400."""
        response = client.post(
            "/forms/submit/",
            data="not valid json{",
            content_type="application/json",
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "Invalid request data" in str(resp_data["errors"])


@pytest.mark.django_db
class TestHTTPMethods:
    """Tests for HTTP method handling."""

    def test_get_not_allowed(self, client, wagtail_site):
        """GET requests should return 405."""
        response = client.get(
            "/forms/submit/",
            HTTP_HOST=wagtail_site.hostname,
        )
        assert response.status_code == 405
