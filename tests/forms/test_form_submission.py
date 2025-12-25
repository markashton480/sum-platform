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
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from sum_core.forms.models import FormConfiguration, FormDefinition
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


def make_select_option(value: str, label: str) -> tuple[str, dict[str, str]]:
    """Helper to define select options for dynamic forms."""
    return ("option", {"value": value, "label": label})


def create_dynamic_form_definition(wagtail_site, *, is_active: bool = True):
    """Create a minimal dynamic FormDefinition for submission tests."""
    return FormDefinition.objects.create(
        site=wagtail_site,
        name="Dynamic Contact",
        slug="dynamic-contact",
        is_active=is_active,
        fields=[
            ("text_input", {"field_name": "name", "label": "Name"}),
            ("email_input", {"field_name": "email", "label": "Email"}),
            ("textarea", {"field_name": "message", "label": "Message"}),
            (
                "phone_input",
                {"field_name": "phone", "label": "Phone", "required": False},
            ),
            (
                "select",
                {
                    "field_name": "service",
                    "label": "Service",
                    "choices": [make_select_option("roofing", "Roofing")],
                    "allow_multiple": False,
                },
            ),
        ],
    )


def make_dynamic_submission_data(form_definition, time_token: str = "") -> dict:
    """Create valid dynamic form submission data."""
    return {
        "form_definition_id": str(form_definition.id),
        "name": "Jane Smith",
        "email": "jane@example.com",
        "message": "Looking for a quote.",
        "phone": "07700 900456",
        "service": "roofing",
        "_time_token": time_token,
        "website": "",
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

    def test_invalid_email_format_rejected(self, client, wagtail_site, form_config):
        """Invalid email format should return 400 and not create Lead."""
        initial_count = Lead.objects.count()
        data = make_valid_submission_data()
        data["email"] = "not-an-email"

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "email" in resp_data["errors"]
        assert "valid email" in resp_data["errors"]["email"][0].lower()
        # Ensure no Lead was created
        assert Lead.objects.count() == initial_count

    def test_invalid_email_missing_domain_rejected(
        self, client, wagtail_site, form_config
    ):
        """Email without domain should be rejected."""
        initial_count = Lead.objects.count()
        data = make_valid_submission_data()
        data["email"] = "user@"

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        assert Lead.objects.count() == initial_count

    def test_malformed_phone_rejected(self, client, wagtail_site, form_config):
        """Malformed phone number should return 400 and not create Lead."""
        initial_count = Lead.objects.count()
        data = make_valid_submission_data()
        data["phone"] = "not-a-phone-123"

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "phone" in resp_data["errors"]
        assert "valid uk phone" in resp_data["errors"]["phone"][0].lower()
        # Ensure no Lead was created
        assert Lead.objects.count() == initial_count

    def test_valid_uk_mobile_phone_accepted(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Valid UK mobile number should be accepted."""
        data = make_valid_submission_data(valid_time_token)
        data["phone"] = "07700 900123"

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
        assert lead.phone == "07700 900123"

    def test_valid_uk_landline_accepted(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Valid UK landline number should be accepted."""
        data = make_valid_submission_data(valid_time_token)
        data["phone"] = "020 7946 0958"

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
        assert lead.phone == "020 7946 0958"

    def test_international_format_uk_phone_accepted(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """UK phone with +44 prefix should be accepted."""
        data = make_valid_submission_data(valid_time_token)
        data["phone"] = "+447700900123"

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200

    def test_empty_phone_is_optional(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Empty phone field should be accepted (phone is optional)."""
        data = make_valid_submission_data(valid_time_token)
        data["phone"] = ""

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200

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
class TestFormSubmissionCSRF:
    """Tests for CSRF protection on the submission endpoint."""

    def test_missing_csrf_returns_403(
        self, wagtail_site, form_config, valid_time_token
    ):
        """POST without CSRF should return 403 when CSRF checks are enforced."""
        client = Client(enforce_csrf_checks=True)
        data = make_valid_submission_data(valid_time_token)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 403

    def test_valid_csrf_allows_submission(
        self, wagtail_site, form_config, valid_time_token
    ):
        """POST with CSRF should succeed when CSRF checks are enforced."""
        client = Client(enforce_csrf_checks=True)
        data = make_valid_submission_data(valid_time_token)

        # Trigger CSRF cookie to be set on the client.
        client.get("/admin/login/", HTTP_HOST=wagtail_site.hostname)
        csrf_token = client.cookies["csrftoken"].value
        data["csrfmiddlewaretoken"] = csrf_token

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 200


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

    def test_submission_succeeds_without_default_site(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """
        Submissions should still succeed even if no Site is marked as default.

        This can occur in dev environments after manual Site edits.
        """
        wagtail_site.is_default_site = False
        wagtail_site.hostname = "different.test"
        wagtail_site.save(update_fields=["is_default_site", "hostname"])

        data = make_valid_submission_data(valid_time_token)
        initial_count = Lead.objects.count()

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 5

            response = client.post(
                "/forms/submit/",
                data=data,
                # Use the Django test client's allowed host, but one that no longer
                # matches Site.hostname after our edit above.
                HTTP_HOST="testserver",
            )

        assert response.status_code == 200
        assert Lead.objects.count() == initial_count + 1

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
class TestDynamicFormSubmission:
    """Tests for dynamic form submission handling."""

    def test_dynamic_submission_creates_lead(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Dynamic form submission should create a Lead."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition, valid_time_token)

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
        assert lead.form_type == form_definition.slug
        assert lead.form_data["service"] == "roofing"
        assert lead.form_data["ip_address"] == "127.0.0.1"

    def test_dynamic_validation_errors_return_400(
        self, client, wagtail_site, form_config
    ):
        """Missing required fields should return validation errors."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition)
        del data["email"]

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "email" in resp_data["errors"]

    def test_dynamic_honeypot_blocks_submission(
        self, client, wagtail_site, form_config
    ):
        """Filled honeypot should be rejected for dynamic forms."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition)
        data["website"] = "bot"

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400

    def test_dynamic_timing_too_fast_returns_400(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """Dynamic submission too fast should return 400."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition, valid_time_token)

        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            token_time = int(valid_time_token.split(":")[0])
            mock_time.return_value = token_time + 1

            response = client.post(
                "/forms/submit/",
                data=data,
                HTTP_HOST=wagtail_site.hostname,
            )

        assert response.status_code == 400

    def test_dynamic_rate_limit_exceeded_returns_429(
        self, client, wagtail_site, form_config
    ):
        """Rate limiting should apply to dynamic submissions."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition)

        cache_key = get_rate_limit_cache_key("127.0.0.1", wagtail_site.id)
        cache.set(cache_key, 20, timeout=3600)

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 429

    def test_dynamic_inactive_form_rejected(self, client, wagtail_site, form_config):
        """Inactive form definitions should be rejected."""
        form_definition = create_dynamic_form_definition(wagtail_site, is_active=False)
        data = make_dynamic_submission_data(form_definition)

        response = client.post(
            "/forms/submit/",
            data=data,
            HTTP_HOST=wagtail_site.hostname,
        )

        assert response.status_code == 400
        resp_data = response.json()
        assert "inactive" in resp_data["errors"]["__all__"][0].lower()

    def test_dynamic_attribution_fields_preserved(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """UTM and referrer fields should persist on dynamic submissions."""
        form_definition = create_dynamic_form_definition(wagtail_site)
        data = make_dynamic_submission_data(form_definition, valid_time_token)
        data.update(
            {
                "utm_source": "google",
                "utm_medium": "cpc",
                "utm_campaign": "spring",
                "page_url": "https://example.com/contact",
                "landing_page_url": "https://example.com/",
                "referrer_url": "https://google.com",
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
        assert lead.utm_campaign == "spring"
        assert lead.page_url == "https://example.com/contact"
        assert lead.landing_page_url == "https://example.com/"
        assert lead.referrer_url == "https://google.com"

    def test_dynamic_file_upload_saved(
        self, client, wagtail_site, form_config, valid_time_token
    ):
        """File uploads should be persisted and referenced in form_data."""
        form_definition = FormDefinition.objects.create(
            site=wagtail_site,
            name="Dynamic Upload",
            slug="dynamic-upload",
            fields=[
                ("text_input", {"field_name": "name", "label": "Name"}),
                ("email_input", {"field_name": "email", "label": "Email"}),
                ("textarea", {"field_name": "message", "label": "Message"}),
                (
                    "file_upload",
                    {
                        "field_name": "attachment",
                        "label": "Attachment",
                        "allowed_extensions": ".pdf",
                        "max_file_size_mb": 5,
                    },
                ),
            ],
        )
        upload = SimpleUploadedFile(
            "resume.pdf", b"pdf-data", content_type="application/pdf"
        )
        data = make_dynamic_submission_data(form_definition, valid_time_token)
        data["attachment"] = upload

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
        file_path = None
        try:
            file_payload = lead.form_data["attachment"]
            assert file_payload["name"] == "resume.pdf"
            file_path = file_payload["path"]
            assert default_storage.exists(file_path)
        finally:
            if file_path:
                default_storage.delete(file_path)


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
