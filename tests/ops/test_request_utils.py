"""
Name: Request utilities tests
Path: tests/ops/test_request_utils.py
Purpose: Validate trusted proxy client IP extraction.
Family: Ops tests.
Dependencies: pytest, Django
"""

from __future__ import annotations

from django.test import RequestFactory, override_settings
from sum_core.ops.request_utils import get_client_ip


def test_untrusted_proxy_ignores_x_forwarded_for():
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.5",
        REMOTE_ADDR="198.51.100.10",
    )

    assert get_client_ip(request) == "198.51.100.10"


@override_settings(SUM_TRUSTED_PROXY_IPS=["10.0.0.1"])
def test_trusted_proxy_uses_x_forwarded_for():
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.5",
        REMOTE_ADDR="10.0.0.1",
    )

    assert get_client_ip(request) == "203.0.113.5"


@override_settings(SUM_TRUSTED_PROXY_IPS=["10.0.0.1"])
def test_untrusted_proxy_in_chain_stops_resolution():
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.5, 192.0.2.10",
        REMOTE_ADDR="10.0.0.1",
    )

    assert get_client_ip(request) == "192.0.2.10"


@override_settings(SUM_TRUSTED_PROXY_IPS=["10.0.0.0/8"])
def test_trusted_proxy_cidr_uses_x_forwarded_for():
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="203.0.113.5",
        REMOTE_ADDR="10.2.3.4",
    )

    assert get_client_ip(request) == "203.0.113.5"


@override_settings(SUM_TRUSTED_PROXY_IPS=["10.0.0.1"])
def test_invalid_forwarded_for_falls_back_to_remote_addr():
    request = RequestFactory().get(
        "/",
        HTTP_X_FORWARDED_FOR="unknown",
        REMOTE_ADDR="10.0.0.1",
    )

    assert get_client_ip(request) == "10.0.0.1"
