from unittest.mock import MagicMock, patch

import pytest
from django.urls import reverse
from sum_core.ops.health import check_cache, check_celery, check_db


@pytest.mark.django_db
def test_check_db_success():
    """Test that check_db returns ok when database is accessible."""
    result = check_db()
    assert result.status == "ok"
    assert result.latency_ms is not None
    assert result.latency_ms >= 0


@pytest.mark.django_db
def test_check_db_failure():
    """Test that check_db returns fail when database raises exception."""
    with patch(
        "sum_core.ops.health.connection.cursor", side_effect=Exception("DB Error")
    ):
        result = check_db()
        assert result.status == "fail"
        assert result.detail == "DB Error"
        assert result.latency_ms is None


def test_check_cache_success():
    """Test that check_cache returns ok when cache works."""
    # Use a dummy cache or mock.
    # Since we are using django.core.cache.cache, we can patch it.
    with patch("sum_core.ops.health.cache") as mock_cache:
        mock_cache.get.return_value = 1
        result = check_cache()
        assert result.status == "ok"
        mock_cache.set.assert_called()
        mock_cache.get.assert_called()
        mock_cache.delete.assert_called()


def test_check_cache_failure():
    """Test that check_cache returns fail when cache mismatches."""
    with patch("sum_core.ops.health.cache") as mock_cache:
        mock_cache.get.return_value = 2  # Mismatch
        result = check_cache()
        assert result.status == "fail"
        assert "mismatch" in str(result.detail)


@patch("sum_core.ops.health.app_or_default")
@patch("sum_core.ops.health.settings")
def test_check_celery_success(mock_settings, mock_app_or_default):
    """Test celery check returns ok when connected."""
    mock_settings.CELERY_BROKER_URL = "redis://localhost:6379/0"
    mock_app = MagicMock()
    mock_connection = MagicMock()

    # Context manager mock
    mock_app.connection_for_read.return_value.__enter__.return_value = mock_connection
    mock_app_or_default.return_value = mock_app

    result = check_celery()
    assert result.status == "ok"
    mock_connection.ensure_connection.assert_called()


@patch("sum_core.ops.health.settings")
def test_check_celery_skipped(mock_settings):
    """Test celery check disabled if no broker URL."""
    mock_settings.CELERY_BROKER_URL = None
    result = check_celery()
    assert result.status == "ok"
    assert "Not configured" in result.detail


@pytest.mark.django_db
def test_health_endpoint_200(client):
    """Integration test for successful health check."""
    # Mock checks to ensure stability
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

        response = client.get(reverse("health_check"))
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "checks" in data
        assert "version" in data


@pytest.mark.django_db
def test_health_endpoint_200_when_degraded(client):
    """Integration test for degraded health check (non-critical issues)."""
    with patch("sum_core.ops.views.get_health_status") as mock_get_status:
        mock_get_status.return_value = {
            "status": "degraded",
            "version": {"git_sha": "abc", "build": "123"},
            "checks": {"celery": {"status": "fail"}},
            "timestamp": "now",
        }

        response = client.get(reverse("health_check"))
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"


@pytest.mark.django_db
def test_health_endpoint_503_when_unhealthy(client):
    """Integration test for unhealthy health check (critical failures)."""
    with patch("sum_core.ops.views.get_health_status") as mock_get_status:
        mock_get_status.return_value = {
            "status": "unhealthy",
            "version": {"git_sha": "abc", "build": "123"},
            "checks": {"db": {"status": "fail"}},
            "timestamp": "now",
        }

        response = client.get(reverse("health_check"))
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
