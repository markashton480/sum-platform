"""
Name: Sentry Integration Tests
Path: tests/ops/test_sentry.py
Purpose: Unit tests for Sentry initialization.
Family: Ops/Observability Tests (Milestone 4)
Dependencies: pytest, sentry-sdk (optional)
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch


class TestSentryInit:
    """Tests for Sentry initialization."""

    def test_init_skipped_when_dsn_not_set(self):
        """Test Sentry init returns False when SENTRY_DSN is not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove SENTRY_DSN if present
            os.environ.pop("SENTRY_DSN", None)

            from sum_core.ops.sentry import init_sentry

            result = init_sentry()
            assert result is False

    def test_init_returns_true_when_dsn_set(self):
        """Test Sentry init returns True when SENTRY_DSN is set."""
        with patch.dict(
            os.environ,
            {"SENTRY_DSN": "https://test@sentry.io/123"},
            clear=False,
        ):
            with patch("sentry_sdk.init") as mock_init:
                from sum_core.ops.sentry import init_sentry

                result = init_sentry()

                assert result is True
                mock_init.assert_called_once()

    def test_init_uses_environment_variable(self):
        """Test Sentry init uses SENTRY_ENVIRONMENT."""
        with patch.dict(
            os.environ,
            {
                "SENTRY_DSN": "https://test@sentry.io/123",
                "SENTRY_ENVIRONMENT": "staging",
            },
            clear=False,
        ):
            with patch("sentry_sdk.init") as mock_init:
                from sum_core.ops.sentry import init_sentry

                init_sentry()

                call_kwargs = mock_init.call_args[1]
                assert call_kwargs["environment"] == "staging"

    def test_init_uses_git_sha_for_release(self):
        """Test Sentry init uses GIT_SHA for release."""
        with patch.dict(
            os.environ,
            {
                "SENTRY_DSN": "https://test@sentry.io/123",
                "GIT_SHA": "abc123def",
            },
            clear=False,
        ):
            with patch("sentry_sdk.init") as mock_init:
                from sum_core.ops.sentry import init_sentry

                init_sentry()

                call_kwargs = mock_init.call_args[1]
                assert call_kwargs["release"] == "abc123def"

    def test_send_default_pii_is_false(self):
        """Test Sentry init has send_default_pii=False."""
        with patch.dict(
            os.environ,
            {"SENTRY_DSN": "https://test@sentry.io/123"},
            clear=False,
        ):
            with patch("sentry_sdk.init") as mock_init:
                from sum_core.ops.sentry import init_sentry

                init_sentry()

                call_kwargs = mock_init.call_args[1]
                assert call_kwargs["send_default_pii"] is False


class TestSetSentryContext:
    """Tests for set_sentry_context helper."""

    def test_set_context_with_request_id(self):
        """Test set_sentry_context sets request_id tag."""
        with patch("sentry_sdk.configure_scope") as mock_configure:
            mock_scope = MagicMock()
            mock_configure.return_value.__enter__ = MagicMock(return_value=mock_scope)
            mock_configure.return_value.__exit__ = MagicMock(return_value=None)

            from sum_core.ops.sentry import set_sentry_context

            set_sentry_context(request_id="test-id-123", lead_id=42)

            mock_scope.set_tag.assert_any_call("request_id", "test-id-123")
            mock_scope.set_tag.assert_any_call("lead_id", "42")

    def test_set_context_handles_import_error(self):
        """Test set_sentry_context handles missing sentry_sdk gracefully."""
        with patch.dict("sys.modules", {"sentry_sdk": None}):
            # Should not raise
            from sum_core.ops.sentry import set_sentry_context

            set_sentry_context(request_id="test")
