"""
Name: Lead Model Tests
Path: tests/leads/test_lead_model.py
Purpose: Validate Lead model defaults and basic field persistence.
Family: Lead management test coverage.
Dependencies: Django ORM, sum_core.leads.models.Lead.
"""

from __future__ import annotations

import pytest
from sum_core.leads.models import Lead

pytestmark = pytest.mark.django_db


def test_lead_defaults() -> None:
    lead = Lead.objects.create(
        name="Jane Doe",
        email="jane@example.com",
        phone="",
        message="Hello",
        form_type="contact",
        form_data={"topic": "General enquiry"},
    )

    assert lead.status == Lead.Status.NEW
    assert lead.is_archived is False
    assert lead.submitted_at is not None


def test_lead_form_data_persists_exactly() -> None:
    payload = {"postcode": "SW1A 1AA", "budget": "20-40k", "details": "Kitchen + bath"}
    lead = Lead.objects.create(
        name="Sam Smith",
        email="sam@example.com",
        message="Please quote",
        phone="07123456789",
        form_type="quote",
        form_data=payload,
    )

    lead.refresh_from_db()
    assert lead.form_data == payload
