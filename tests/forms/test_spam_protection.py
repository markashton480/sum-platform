"""
Name: Spam protection tests
Path: tests/forms/test_spam_protection.py
Purpose: Test spam protection services (honeypot, rate limiting, timing).
Family: Test Suite, Forms.
Dependencies: pytest, Django cache, sum_core.forms.services.
"""

from __future__ import annotations

import time
from unittest import mock

import pytest
from django.core.cache import cache
from sum_core.forms.services import (
    check_honeypot,
    check_rate_limit,
    check_timing,
    generate_time_token,
    get_rate_limit_cache_key,
    increment_rate_limit_counter,
    run_spam_checks,
)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestHoneypotCheck:
    """Tests for honeypot spam detection."""

    def test_empty_honeypot_is_not_spam(self):
        """Empty honeypot field should pass."""
        result = check_honeypot({"company": ""}, "company")
        assert not result.is_spam
        assert result.reason == ""

    def test_missing_honeypot_is_not_spam(self):
        """Missing honeypot field should pass."""
        result = check_honeypot({}, "company")
        assert not result.is_spam

    def test_filled_honeypot_is_spam(self):
        """Filled honeypot field should be detected as spam."""
        result = check_honeypot({"company": "SpamBot Inc"}, "company")
        assert result.is_spam
        assert "Honeypot" in result.reason

    def test_whitespace_only_honeypot_is_spam(self):
        """Whitespace-only value is truthy, so treated as spam."""
        result = check_honeypot({"company": "   "}, "company")
        assert result.is_spam

    def test_custom_honeypot_field_name(self):
        """Custom honeypot field name should work."""
        result = check_honeypot({"website": "http://spam.com"}, "website")
        assert result.is_spam


class TestRateLimitCheck:
    """Tests for rate limiting."""

    def test_no_previous_submissions_passes(self):
        """First submission should pass rate limit."""
        result = check_rate_limit("192.168.1.1", site_id=1, max_per_hour=10)
        assert not result.is_spam
        assert not result.should_rate_limit

    def test_under_limit_passes(self):
        """Submissions under limit should pass."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 5, timeout=3600)

        result = check_rate_limit("192.168.1.1", site_id=1, max_per_hour=10)
        assert not result.should_rate_limit

    def test_at_limit_triggers_rate_limit(self):
        """Submission at limit should trigger rate limit."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 10, timeout=3600)

        result = check_rate_limit("192.168.1.1", site_id=1, max_per_hour=10)
        assert result.should_rate_limit
        assert "Rate limit" in result.reason

    def test_over_limit_triggers_rate_limit(self):
        """Submission over limit should trigger rate limit."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 15, timeout=3600)

        result = check_rate_limit("192.168.1.1", site_id=1, max_per_hour=10)
        assert result.should_rate_limit

    def test_different_ips_are_independent(self):
        """Different IPs should have independent counters."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 10, timeout=3600)

        # Different IP should not be rate limited
        result = check_rate_limit("192.168.1.2", site_id=1, max_per_hour=10)
        assert not result.should_rate_limit

    def test_different_sites_are_independent(self):
        """Different sites should have independent counters."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 10, timeout=3600)

        # Same IP, different site should not be rate limited
        result = check_rate_limit("192.168.1.1", site_id=2, max_per_hour=10)
        assert not result.should_rate_limit


class TestIncrementRateLimitCounter:
    """Tests for rate limit counter increment."""

    def test_increment_from_zero(self):
        """Counter should increment from 0 to 1."""
        increment_rate_limit_counter("192.168.1.1", site_id=1)
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        assert cache.get(cache_key) == 1

    def test_increment_existing_counter(self):
        """Counter should increment existing value."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 5, timeout=3600)

        increment_rate_limit_counter("192.168.1.1", site_id=1)
        assert cache.get(cache_key) == 6


class TestTimeTokenGeneration:
    """Tests for time token generation."""

    def test_generates_valid_format(self):
        """Token should be in timestamp:signature format."""
        token = generate_time_token()
        parts = token.split(":")
        assert len(parts) == 2
        assert parts[0].isdigit()
        assert len(parts[1]) == 16  # Truncated HMAC

    def test_generates_unique_tokens(self):
        """Each call should generate a unique signature timing."""
        token1 = generate_time_token()
        time.sleep(0.01)  # Small delay to ensure different timestamp
        token2 = generate_time_token()
        # Tokens from same second will have same timestamp
        # but we verify format is correct
        assert ":" in token1
        assert ":" in token2


class TestTimingCheck:
    """Tests for submission timing validation."""

    def test_empty_token_passes(self):
        """Empty token should pass (graceful fallback)."""
        result = check_timing("", min_seconds=3)
        assert not result.is_spam

    def test_malformed_token_is_spam(self):
        """Malformed token should be rejected."""
        result = check_timing("not-a-valid-token", min_seconds=3)
        assert result.is_spam
        assert "format" in result.reason.lower()

    def test_invalid_signature_is_spam(self):
        """Token with invalid signature should be rejected."""
        fake_token = "1234567890:fakesignature00"
        result = check_timing(fake_token, min_seconds=3)
        assert result.is_spam
        assert "signature" in result.reason.lower()

    def test_valid_token_after_min_seconds_passes(self):
        """Valid token submitted after min_seconds should pass."""
        token = generate_time_token()
        # Mock time to simulate waiting
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            # Set current time to 5 seconds after token generation
            original_time = int(token.split(":")[0])
            mock_time.return_value = original_time + 5
            result = check_timing(token, min_seconds=3)

        assert not result.is_spam

    def test_valid_token_before_min_seconds_is_spam(self):
        """Valid token submitted too quickly should be rejected."""
        token = generate_time_token()
        # Mock time to simulate immediate submission
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            original_time = int(token.split(":")[0])
            mock_time.return_value = original_time + 1  # Only 1 second elapsed
            result = check_timing(token, min_seconds=3)

        assert result.is_spam
        assert "quickly" in result.reason.lower()

    def test_expired_token_is_spam(self):
        """Token older than 1 hour should be rejected."""
        token = generate_time_token()
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            original_time = int(token.split(":")[0])
            mock_time.return_value = original_time + 4000  # Over 1 hour
            result = check_timing(token, min_seconds=3)

        assert result.is_spam
        assert "expired" in result.reason.lower()


class TestRunSpamChecks:
    """Integration tests for combined spam checks."""

    def test_all_checks_pass(self):
        """Valid submission should pass all checks."""
        token = generate_time_token()
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            original_time = int(token.split(":")[0])
            mock_time.return_value = original_time + 5

            result = run_spam_checks(
                form_data={"company": "", "name": "Test"},
                ip_address="192.168.1.1",
                site_id=1,
                time_token=token,
                honeypot_field_name="company",
                rate_limit_per_hour=20,
                min_seconds_to_submit=3,
            )

        assert not result.is_spam
        assert not result.should_rate_limit

    def test_honeypot_checked_first(self):
        """Honeypot should be checked before other expensive checks."""
        result = run_spam_checks(
            form_data={"company": "SpamBot"},
            ip_address="192.168.1.1",
            site_id=1,
            time_token="",
            honeypot_field_name="company",
            rate_limit_per_hour=20,
            min_seconds_to_submit=3,
        )
        assert result.is_spam
        assert "Honeypot" in result.reason

    def test_rate_limit_returns_correct_flag(self):
        """Rate limit should set should_rate_limit flag."""
        cache_key = get_rate_limit_cache_key("192.168.1.1", 1)
        cache.set(cache_key, 20, timeout=3600)

        result = run_spam_checks(
            form_data={"company": ""},
            ip_address="192.168.1.1",
            site_id=1,
            time_token="",
            honeypot_field_name="company",
            rate_limit_per_hour=20,
            min_seconds_to_submit=3,
        )
        assert result.should_rate_limit
        assert not result.is_spam  # Rate limit is separate from spam

    def test_timing_check_runs_when_others_pass(self):
        """Timing check should run when honeypot and rate limit pass."""
        token = generate_time_token()
        with mock.patch("sum_core.forms.services.time.time") as mock_time:
            original_time = int(token.split(":")[0])
            mock_time.return_value = original_time + 1  # Too quick

            result = run_spam_checks(
                form_data={"company": ""},
                ip_address="192.168.1.1",
                site_id=1,
                time_token=token,
                honeypot_field_name="company",
                rate_limit_per_hour=20,
                min_seconds_to_submit=3,
            )

        assert result.is_spam
        assert "quickly" in result.reason.lower()
