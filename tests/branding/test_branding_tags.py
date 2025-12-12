"""
Name: Branding Template Tag Tests
Path: tests/branding/test_branding_tags.py
Purpose: Verify get_site_settings tag renders values and caches per request.
Family: Branding test suite.
Dependencies: Django templates, wagtail Site model, branding template tags.
"""

from __future__ import annotations

import pytest
from django.db import connection
from django.template import RequestContext, Template
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from sum_core.branding.models import SiteSettings  # type: ignore[import-not-found]
from sum_core.branding.templatetags.branding_tags import (  # type: ignore[import-not-found]
    get_site_settings,
)
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_get_site_settings_renders_in_template() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Template Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")

    template = Template(
        "{% load branding_tags %}"
        "{% get_site_settings as ss %}"
        "{{ ss.company_name }}"
    )
    rendered = template.render(RequestContext(request, {}))

    assert rendered.strip() == "Template Co"


def test_get_site_settings_caches_per_request() -> None:
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)
    settings.company_name = "Cache Co"
    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    context = {"request": request}

    # First call should hit the DB and cache result on the request
    with CaptureQueriesContext(connection) as first_pass:
        first_settings = get_site_settings(context)

    assert len(first_pass) >= 1

    with CaptureQueriesContext(connection) as second_pass:
        second_settings = get_site_settings(context)

    assert second_settings is first_settings
    assert len(second_pass) == 0
