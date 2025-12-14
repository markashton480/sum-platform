"""
Name: Lead Submission Handler Tests
Path: tests/leads/test_lead_submission_handler.py
Purpose: Validate “submission → Lead persisted” and “no lost leads” invariant on downstream failures.
Family: Lead management test coverage.
Dependencies: sum_core.leads.services.create_lead_from_submission.
"""

from __future__ import annotations

import pytest
from sum_core.leads.models import Lead
from sum_core.leads.services import create_lead_from_submission

pytestmark = pytest.mark.django_db


def test_create_lead_from_submission_creates_lead() -> None:
    payload = {"preferred_time": "morning", "notes": "Call first"}
    lead = create_lead_from_submission(
        name="Alex Example",
        email="alex@example.com",
        phone="07000000000",
        message="Hi",
        form_type="contact",
        form_data=payload,
    )

    assert Lead.objects.filter(pk=lead.pk).exists()
    assert lead.status == Lead.Status.NEW
    assert lead.form_type == "contact"
    assert lead.form_data == payload


def test_downstream_failure_does_not_delete_persisted_lead() -> None:
    def _raise_after_create(_: Lead) -> None:
        raise RuntimeError("simulated downstream failure")

    with pytest.raises(RuntimeError):
        create_lead_from_submission(
            name="Failure Case",
            email="failure@example.com",
            message="Test",
            form_type="contact",
            form_data={"a": 1},
            post_create_hook=_raise_after_create,
        )

    assert Lead.objects.filter(
        email="failure@example.com", form_type="contact"
    ).exists()
