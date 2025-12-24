from __future__ import annotations

import pytest
from django.template import RequestContext, Template
from django.test import RequestFactory
from sum_core.branding.models import SiteSettings
from wagtail.models import Site

pytestmark = pytest.mark.django_db


def test_branding_css_output_hsl() -> None:
    """
    Verify branding_css emits HSL variables for all configured colors.
    """
    site = Site.objects.get(is_default_site=True)
    settings = SiteSettings.for_site(site)

    # Configure colors that map to known HSL values
    settings.secondary_color = "#556f61"  # Sage Moss (148 13% 38%)
    settings.accent_color = "#a0563b"  # Sage Terra (16 46% 43%)
    settings.background_color = "#f7f5f1"  # Sage Linen (40 27% 96%)
    settings.surface_color = "#e3ded4"  # Sage Oat (40 22% 86%)
    settings.text_color = "#1a2f23"  # Sage Black (146 29% 14%)

    settings.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template("{% load branding_tags %}{% branding_css %}")
    rendered = template.render(RequestContext(request, {}))

    # Clean up whitespace for checking
    rendered_clean = rendered.replace("\n", "").replace(" ", "")

    # Check Secondary HSL
    assert "--secondary-h:148;" in rendered_clean
    assert "--secondary-s:13%;" in rendered_clean
    assert "--secondary-l:38%;" in rendered_clean

    # Check Accent HSL
    assert "--accent-h:16;" in rendered_clean
    assert "--accent-s:46%;" in rendered_clean
    assert "--accent-l:43%;" in rendered_clean

    # Check Background HSL
    assert "--background-h:40;" in rendered_clean
    assert "--background-s:27%;" in rendered_clean
    assert "--background-l:96%;" in rendered_clean

    # Check Surface HSL
    assert "--surface-h:40;" in rendered_clean
    assert "--surface-s:21%;" in rendered_clean
    assert "--surface-l:86%;" in rendered_clean

    # Check Text HSL
    assert "--text-h:146;" in rendered_clean
    assert "--text-s:29%;" in rendered_clean
    assert "--text-l:14%;" in rendered_clean
