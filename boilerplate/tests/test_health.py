"""
Integration tests for the /health/ endpoint.

This test verifies that sum_core endpoints are correctly wired into this client project.
It should continue to pass after copying the boilerplate and renaming the project.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_health_endpoint_returns_200(client) -> None:
    """
    Integration test: /health/ returns HTTP 200 with JSON.

    This test proves that the client project correctly wires the sum_core ops endpoint.
    """
    # Mock the health checks to ensure stable test results
    with patch("sum_core.ops.views.get_health_status") as mock_get_status:
        mock_get_status.return_value = {
            "status": "ok",
            "version": {"git_sha": "test", "build": "test"},
            "checks": {
                "db": {"status": "ok"},
                "cache": {"status": "ok"},
                "celery": {"status": "ok"},
            },
            "timestamp": "2025-01-01T00:00:00Z",
        }

        response = client.get(reverse("health_check"))

        assert response.status_code == 200


@pytest.mark.django_db
def test_health_endpoint_returns_json_with_status_and_checks(client) -> None:
    """
    Integration test: /health/ JSON response has required keys.

    Verifies the health endpoint returns the expected structure.
    """
    with patch("sum_core.ops.views.get_health_status") as mock_get_status:
        mock_get_status.return_value = {
            "status": "ok",
            "version": {"git_sha": "test", "build": "test"},
            "checks": {
                "db": {"status": "ok"},
                "cache": {"status": "ok"},
                "celery": {"status": "ok"},
            },
            "timestamp": "2025-01-01T00:00:00Z",
        }

        response = client.get(reverse("health_check"))
        data = response.json()

        assert "status" in data, "Response JSON must have 'status' key"
        assert "checks" in data, "Response JSON must have 'checks' key"
