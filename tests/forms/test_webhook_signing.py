"""
Name: Dynamic form webhook signing tests
Path: tests/forms/test_webhook_signing.py
Purpose: Verify dynamic form webhook signing headers.
Family: Forms, Leads, Webhooks.
"""

from __future__ import annotations

import hashlib
import hmac
from unittest.mock import Mock, patch

import pytest
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import WEBHOOK_SIGNATURE_HEADER, send_webhook
from sum_core.leads.models import Lead, WebhookStatus


@pytest.fixture
def form_definition(wagtail_default_site):
    return FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Dynamic Contact",
        slug="dynamic-contact",
        fields=[],
        webhook_enabled=True,
        webhook_url="https://example.com/webhook",
        webhook_signing_secret="supersecret",
    )


@pytest.fixture
def lead(form_definition):
    return Lead.objects.create(
        name="Jane Doe",
        email="jane@example.com",
        message="Need a quote",
        form_type=form_definition.slug,
        form_webhook_status=WebhookStatus.PENDING,
        form_data={"service": "Roofing"},
    )


@pytest.mark.django_db
def test_webhook_signature_header_matches_payload(lead, form_definition):
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200

    with patch(
        "sum_core.forms.tasks.requests.post", return_value=mock_response
    ) as mock_post:
        send_webhook(lead.id, form_definition.id)

    body = mock_post.call_args[1]["data"]
    headers = mock_post.call_args[1]["headers"]
    expected_signature = hmac.new(
        form_definition.webhook_signing_secret.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()

    assert headers[WEBHOOK_SIGNATURE_HEADER] == f"sha256={expected_signature}"


@pytest.mark.django_db
def test_webhook_signature_header_omitted_without_secret(lead, form_definition):
    form_definition.webhook_signing_secret = ""
    form_definition.save(update_fields=["webhook_signing_secret"])

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200

    with patch(
        "sum_core.forms.tasks.requests.post", return_value=mock_response
    ) as mock_post:
        send_webhook(lead.id, form_definition.id)

    headers = mock_post.call_args[1]["headers"]
    assert WEBHOOK_SIGNATURE_HEADER not in headers
