"""
Name: Dynamic form webhook field controls tests
Path: tests/forms/test_webhook_field_controls.py
Purpose: Verify allowlist and denylist filtering for webhook payloads.
Family: Forms, Leads, Webhooks.
"""

from __future__ import annotations

import pytest
from sum_core.forms.models import FormDefinition
from sum_core.forms.tasks import _build_webhook_payload
from sum_core.leads.models import Lead


@pytest.fixture
def form_definition(wagtail_default_site):
    return FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Dynamic Contact",
        slug="dynamic-contact",
        fields=[],
        webhook_enabled=True,
        webhook_url="https://example.com/webhook",
    )


@pytest.fixture
def lead(form_definition):
    return Lead.objects.create(
        name="Jane Doe",
        email="jane@example.com",
        message="Need a quote",
        form_type=form_definition.slug,
        form_data={
            "service": "Roofing",
            "budget": "5000",
            "ssn": "123-45-6789",
        },
    )


@pytest.mark.django_db
def test_webhook_denylist_removes_fields(lead, form_definition):
    form_definition.webhook_field_denylist = "ssn"
    form_definition.save(update_fields=["webhook_field_denylist"])

    payload = _build_webhook_payload(lead, form_definition)
    data = payload["submission"]["data"]

    assert "ssn" not in data
    assert data["service"] == "Roofing"
    assert data["budget"] == "5000"


@pytest.mark.django_db
def test_webhook_allowlist_includes_only_fields(lead, form_definition):
    form_definition.webhook_field_allowlist = "service, budget"
    form_definition.save(update_fields=["webhook_field_allowlist"])

    payload = _build_webhook_payload(lead, form_definition)
    data = payload["submission"]["data"]

    assert set(data.keys()) == {"service", "budget"}


@pytest.mark.django_db
def test_webhook_allowlist_then_denylist(lead, form_definition):
    form_definition.webhook_field_allowlist = "service, ssn"
    form_definition.webhook_field_denylist = "ssn"
    form_definition.save(
        update_fields=["webhook_field_allowlist", "webhook_field_denylist"]
    )

    payload = _build_webhook_payload(lead, form_definition)
    data = payload["submission"]["data"]

    assert set(data.keys()) == {"service"}
