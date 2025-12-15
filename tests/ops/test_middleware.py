"""
Name: Correlation ID Middleware Tests
Path: tests/ops/test_middleware.py
Purpose: Unit tests for CorrelationIdMiddleware.
Family: Ops/Observability Tests (Milestone 4)
Dependencies: pytest, Django
"""

from __future__ import annotations

import uuid

import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from sum_core.ops.middleware import (
    REQUEST_ID_HEADER,
    CorrelationIdMiddleware,
    get_request_id,
)


@pytest.fixture
def request_factory():
    """Provide Django RequestFactory."""
    return RequestFactory()


@pytest.fixture
def mock_get_response():
    """Create a mock get_response callable."""

    def _get_response(request):
        return HttpResponse("OK")

    return _get_response


class TestCorrelationIdMiddleware:
    """Tests for CorrelationIdMiddleware."""

    def test_generates_request_id_when_absent(self, request_factory, mock_get_response):
        """Test middleware generates a UUID request_id when header is absent."""
        middleware = CorrelationIdMiddleware(mock_get_response)
        request = request_factory.get("/")

        response = middleware(request)

        # Should have set request.request_id
        assert hasattr(request, "request_id")
        assert request.request_id is not None

        # Should be a valid UUID
        uuid.UUID(request.request_id)  # Raises if invalid

        # Response should have X-Request-ID header
        assert REQUEST_ID_HEADER in response
        assert response[REQUEST_ID_HEADER] == request.request_id

    def test_preserves_inbound_request_id(self, request_factory, mock_get_response):
        """Test middleware preserves X-Request-ID when provided in request."""
        middleware = CorrelationIdMiddleware(mock_get_response)
        existing_id = "test-request-id-12345"

        request = request_factory.get("/", HTTP_X_REQUEST_ID=existing_id)

        response = middleware(request)

        # Should preserve the existing request_id
        assert request.request_id == existing_id
        assert response[REQUEST_ID_HEADER] == existing_id

    def test_response_header_always_set(self, request_factory, mock_get_response):
        """Test X-Request-ID header is always set on response."""
        middleware = CorrelationIdMiddleware(mock_get_response)
        request = request_factory.get("/")

        response = middleware(request)

        assert REQUEST_ID_HEADER in response

    def test_request_id_available_on_request_object(
        self, request_factory, mock_get_response
    ):
        """Test request.request_id attribute is available."""
        middleware = CorrelationIdMiddleware(mock_get_response)
        request = request_factory.get("/")

        middleware(request)

        assert hasattr(request, "request_id")
        assert isinstance(request.request_id, str)
        assert len(request.request_id) > 0

    def test_context_variable_set_during_request(self, request_factory):
        """Test request_id is available via get_request_id() during request."""
        captured_id = None

        def capturing_get_response(request):
            nonlocal captured_id
            captured_id = get_request_id()
            return HttpResponse("OK")

        middleware = CorrelationIdMiddleware(capturing_get_response)
        request = request_factory.get("/")

        middleware(request)

        assert captured_id is not None
        assert captured_id == request.request_id

    def test_context_variable_reset_after_request(self, request_factory):
        """Test context variable is reset after request completes."""
        middleware = CorrelationIdMiddleware(lambda r: HttpResponse("OK"))
        request = request_factory.get("/")

        middleware(request)

        # After request completes, get_request_id() should return None
        assert get_request_id() is None


@pytest.mark.django_db
class TestMiddlewareIntegration:
    """Integration tests for middleware with Django client."""

    def test_health_endpoint_has_request_id_header(self, client):
        """Test that /health/ endpoint returns X-Request-ID header."""
        from unittest.mock import patch

        with patch("sum_core.ops.views.get_health_status") as mock_get_status:
            mock_get_status.return_value = {
                "status": "ok",
                "version": {"git_sha": "abc", "build": "123"},
                "checks": {
                    "db": {"status": "ok"},
                    "cache": {"status": "ok"},
                    "celery": {"status": "ok"},
                },
                "timestamp": "now",
            }

            response = client.get("/health/")

            assert response.status_code == 200
            assert REQUEST_ID_HEADER in response
            # Should be a valid UUID
            uuid.UUID(response[REQUEST_ID_HEADER])
