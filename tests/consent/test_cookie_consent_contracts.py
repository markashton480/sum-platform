from __future__ import annotations

import re
from pathlib import Path

from django.template.loader import get_template

from tests.utils import REPO_ROOT


def _read_template_source(template_name: str) -> str:
    template = get_template(template_name)
    origin = getattr(template, "origin", None)
    assert origin and origin.name, f"Template origin missing for {template_name}"
    return Path(origin.name).read_text(encoding="utf-8")


def _read_static_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def test_cookie_banner_template_contract(theme_active_copy) -> None:
    content = _read_template_source("sum_core/includes/cookie_banner.html")

    assert re.search(r'class="[^"]*cookie-banner', content)
    assert 'data-cookie-consent="accept"' in content
    assert 'data-cookie-consent="reject"' in content


def test_footer_manage_cookie_link_contract(theme_active_copy) -> None:
    content = _read_template_source("sum_core/includes/footer.html")

    assert 'data-cookie-consent="manage"' in content


def test_cookie_consent_js_validates_accept_reject_and_version() -> None:
    content = _read_static_text("core/sum_core/static/sum_core/js/cookie_consent.js")

    assert "CONSENT_ACCEPTED" in content
    assert "CONSENT_REJECTED" in content
    assert re.search(
        r"consent\s*===\s*CONSENT_ACCEPTED\s*\|\|\s*consent\s*===\s*CONSENT_REJECTED",
        content,
    )
    assert "version === currentVersion" in content
    assert "if (!isConsentValid())" in content


def test_analytics_loader_requires_accepted_consent_and_matching_version() -> None:
    content = _read_static_text("core/sum_core/static/sum_core/js/analytics_loader.js")

    assert "CONSENT_ACCEPTED" in content
    assert "version === getConsentVersion()" in content
    assert "cookie_banner_enabled" in content
