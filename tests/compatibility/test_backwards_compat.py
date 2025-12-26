"""
Name: Backwards Compatibility Tests
Path: tests/compatibility/test_backwards_compat.py
Purpose: Verify static forms, dynamic forms, leads admin, and page rendering remain compatible.
Family: Compatibility, Forms, Leads, Pages.
Dependencies: pytest, Django test client, Wagtail models, sum_core forms/leads/pages.
"""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client
from sum_core.blocks import PageStreamBlock
from sum_core.forms.models import FormConfiguration, FormDefinition
from sum_core.leads.models import Lead
from sum_core.pages import StandardPage
from sum_core.pages.services import ServiceIndexPage, ServicePage
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def wagtail_site(wagtail_default_site: Site) -> Site:
    return wagtail_default_site


@pytest.fixture
def admin_user(db):
    user_model = get_user_model()
    return user_model.objects.create_superuser(
        username="admin",
        email="admin@test.com",
        password="password123",
    )


def _select_option(value: str, label: str) -> tuple[str, dict[str, str]]:
    return ("option", {"value": value, "label": label})


def _create_dynamic_form_definition(site: Site) -> FormDefinition:
    return FormDefinition.objects.create(
        site=site,
        name="Dynamic Contact",
        slug="dynamic-contact",
        fields=[
            ("text_input", {"field_name": "name", "label": "Name"}),
            ("email_input", {"field_name": "email", "label": "Email"}),
            ("textarea", {"field_name": "message", "label": "Message"}),
            (
                "select",
                {
                    "field_name": "service",
                    "label": "Service",
                    "choices": [_select_option("roofing", "Roofing")],
                    "allow_multiple": False,
                },
            ),
        ],
    )


def _contact_form_stream_data():
    stream_block = PageStreamBlock()
    return stream_block.to_python(
        [
            {
                "type": "contact_form",
                "value": {
                    "heading": "<h2>Contact Us</h2>",
                    "intro": "<p>Tell us about your project.</p>",
                    "submit_label": "Send",
                },
            }
        ]
    )


def _quote_form_stream_data():
    stream_block = PageStreamBlock()
    return stream_block.to_python(
        [
            {
                "type": "quote_request_form",
                "value": {
                    "heading": "<h2>Request a Quote</h2>",
                    "intro": "<p>Share project details.</p>",
                    "submit_label": "Request Quote",
                    "show_compact_meta": True,
                },
            }
        ]
    )


def test_static_contact_form_submission_creates_lead(wagtail_site: Site) -> None:
    FormConfiguration.get_for_site(wagtail_site)
    client = Client()

    data = {
        "name": "Alice Legacy",
        "email": "alice@example.com",
        "message": "Hello from a static form.",
        "form_type": "contact",
        "company": "",
        "project_type": "roofing",
    }

    response = client.post(
        "/forms/submit/",
        data=data,
        HTTP_HOST=wagtail_site.hostname,
    )

    assert response.status_code == 200
    lead = Lead.objects.latest("submitted_at")
    assert lead.form_type == "contact"
    assert lead.form_data["project_type"] == "roofing"


def test_static_quote_request_submission_creates_lead(wagtail_site: Site) -> None:
    FormConfiguration.get_for_site(wagtail_site)
    client = Client()

    data = {
        "name": "Bob Legacy",
        "email": "bob@example.com",
        "message": "Requesting a quote.",
        "form_type": "quote_request",
        "company": "",
        "budget": "20k",
    }

    response = client.post(
        "/forms/submit/",
        data=data,
        HTTP_HOST=wagtail_site.hostname,
    )

    assert response.status_code == 200
    lead = Lead.objects.latest("submitted_at")
    assert lead.form_type == "quote_request"
    assert lead.form_data["budget"] == "20k"


def test_dynamic_form_submission_sets_form_type_slug(wagtail_site: Site) -> None:
    form_definition = _create_dynamic_form_definition(wagtail_site)
    client = Client()

    data = {
        "form_definition_id": str(form_definition.id),
        "name": "Dana Dynamic",
        "email": "dana@example.com",
        "message": "Dynamic form submission.",
        "service": "roofing",
        "website": "",
    }

    response = client.post(
        "/forms/submit/",
        data=data,
        HTTP_HOST=wagtail_site.hostname,
    )

    assert response.status_code == 200
    lead = Lead.objects.latest("submitted_at")
    assert lead.form_type == form_definition.slug
    assert lead.form_data["service"] == "roofing"


def test_admin_list_and_filters_handle_mixed_leads(admin_user) -> None:
    legacy_lead = Lead.objects.create(
        name="Legacy Lead",
        email="legacy@example.com",
        message="Legacy static lead.",
        form_type="contact",
    )
    dynamic_lead = Lead.objects.create(
        name="Dynamic Lead",
        email="dynamic@example.com",
        message="Dynamic lead.",
        form_type="dynamic-contact",
    )

    client = Client()
    client.force_login(admin_user)

    response = client.get("/admin/leads/")
    assert response.status_code == 200
    html = response.content.decode()
    assert legacy_lead.name in html
    assert dynamic_lead.name in html

    response = client.get("/admin/leads/?form_type=contact")
    assert response.status_code == 200
    html = response.content.decode()
    assert legacy_lead.name in html
    assert dynamic_lead.name not in html

    response = client.get("/admin/leads/?form_type=dynamic-contact")
    assert response.status_code == 200
    html = response.content.decode()
    assert dynamic_lead.name in html
    assert legacy_lead.name not in html


def test_admin_detail_renders_for_legacy_and_dynamic_leads(admin_user) -> None:
    legacy_lead = Lead.objects.create(
        name="Legacy Detail",
        email="legacy-detail@example.com",
        message="Legacy detail view.",
        form_type="contact",
    )
    dynamic_lead = Lead.objects.create(
        name="Dynamic Detail",
        email="dynamic-detail@example.com",
        message="Dynamic detail view.",
        form_type="dynamic-contact",
    )

    client = Client()
    client.force_login(admin_user)

    for lead in (legacy_lead, dynamic_lead):
        response = client.get(f"/admin/leads/inspect/{lead.id}/")
        assert response.status_code == 200
        assert lead.form_type in response.content.decode()


def test_standard_page_with_contact_form_renders_and_has_seo_tags(
    wagtail_site: Site,
) -> None:
    root = Page.get_first_root_node()
    page = StandardPage(
        title="Contact Page",
        slug="contact-page",
        body=_contact_form_stream_data(),
        meta_description="Contact page description.",
    )
    root.add_child(instance=page)
    page.save_revision().publish()

    client = Client()
    response = client.get(page.url)
    html = response.content.decode()

    assert response.status_code == 200
    assert 'data-form-type="contact"' in html
    assert '<meta name="description" content="Contact page description.">' in html
    assert (
        '<meta property="og:description" content="Contact page description.">' in html
    )


def test_service_page_with_quote_form_renders_and_has_seo_tags(
    wagtail_site: Site,
) -> None:
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services")
    root.add_child(instance=service_index)
    service_index.save_revision().publish()

    service_page = ServicePage(
        title="Roofing Service",
        slug="roofing-service",
        body=_quote_form_stream_data(),
        meta_description="Roofing service description.",
    )
    service_index.add_child(instance=service_page)
    service_page.save_revision().publish()

    client = Client()
    response = client.get(service_page.url)
    html = response.content.decode()

    assert response.status_code == 200
    assert 'data-form-type="quote_request"' in html
    assert '<meta name="description" content="Roofing service description.">' in html
    assert (
        '<meta property="og:description" content="Roofing service description.">'
        in html
    )
