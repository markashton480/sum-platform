"""
Name: Lead Attribution Tests
Path: tests/leads/test_attribution.py
Purpose: Validate lead source derivation logic for SSOT defaults and custom rules.
Family: Lead management test coverage.
Dependencies: sum_core.leads.attribution, sum_core.leads.models.LeadSourceRule.
"""

from __future__ import annotations

import pytest
from sum_core.leads.attribution import derive_lead_source
from sum_core.leads.models import LeadSourceRule

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def clear_lead_source_rules() -> None:
    """Clear all LeadSourceRule objects before each test to ensure isolation."""
    LeadSourceRule.objects.all().delete()


class TestSSOTDefaultRules:
    """Tests for SSOT 8.2 default attribution rules."""

    def test_google_cpc_derives_google_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="google",
            utm_medium="cpc",
        )
        assert source == "google_ads"
        assert detail == ""

    def test_google_cpc_with_campaign_includes_detail(self) -> None:
        source, detail = derive_lead_source(
            utm_source="google",
            utm_medium="cpc",
            utm_campaign="winter-sale-2025",
        )
        assert source == "google_ads"
        assert detail == "campaign=winter-sale-2025"

    def test_facebook_cpc_derives_meta_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="facebook",
            utm_medium="cpc",
        )
        assert source == "meta_ads"

    def test_instagram_cpc_derives_meta_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="instagram",
            utm_medium="cpc",
        )
        assert source == "meta_ads"

    def test_fb_shorthand_cpc_derives_meta_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="fb",
            utm_medium="cpc",
        )
        assert source == "meta_ads"

    def test_ig_shorthand_cpc_derives_meta_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="ig",
            utm_medium="cpc",
        )
        assert source == "meta_ads"

    def test_bing_cpc_derives_bing_ads(self) -> None:
        source, detail = derive_lead_source(
            utm_source="bing",
            utm_medium="cpc",
        )
        assert source == "bing_ads"

    def test_google_referrer_no_utm_derives_seo(self) -> None:
        source, detail = derive_lead_source(
            referrer_url="https://www.google.com/search?q=kitchen+renovation",
        )
        assert source == "seo"
        assert "referrer=" in detail

    def test_no_referrer_no_utm_derives_direct(self) -> None:
        source, detail = derive_lead_source()
        assert source == "direct"
        assert detail == ""

    def test_has_referrer_no_utm_derives_referral(self) -> None:
        source, detail = derive_lead_source(
            referrer_url="https://www.checkatrade.com/trades/example",
        )
        assert source == "referral"
        assert "referrer=" in detail

    def test_offline_prefix_derives_offline(self) -> None:
        source, detail = derive_lead_source(
            utm_source="offline-flyer",
            utm_medium="print",
        )
        assert source == "offline"

    def test_unknown_utm_combination_derives_unknown(self) -> None:
        source, detail = derive_lead_source(
            utm_source="linkedin",
            utm_medium="social",
        )
        assert source == "unknown"
        assert "utm_source=linkedin" in detail

    def test_case_insensitive_matching(self) -> None:
        source, _ = derive_lead_source(
            utm_source="GOOGLE",
            utm_medium="CPC",
        )
        assert source == "google_ads"


class TestLeadSourceRuleMatching:
    """Tests for LeadSourceRule model's matches() method."""

    def test_empty_rule_matches_everything(self) -> None:
        rule = LeadSourceRule(
            derived_source="google_ads",
            is_active=True,
        )
        assert rule.matches(utm_source="any", utm_medium="anything", referrer_url="")

    def test_inactive_rule_never_matches(self) -> None:
        rule = LeadSourceRule(
            utm_source="google",
            derived_source="google_ads",
            is_active=False,
        )
        assert not rule.matches(utm_source="google", utm_medium="cpc", referrer_url="")

    def test_utm_source_match(self) -> None:
        rule = LeadSourceRule(
            utm_source="partner",
            derived_source="referral",
            is_active=True,
        )
        assert rule.matches(utm_source="partner", utm_medium="", referrer_url="")
        assert not rule.matches(utm_source="google", utm_medium="", referrer_url="")

    def test_utm_medium_match(self) -> None:
        rule = LeadSourceRule(
            utm_medium="email",
            derived_source="referral",
            is_active=True,
        )
        assert rule.matches(utm_source="", utm_medium="email", referrer_url="")
        assert not rule.matches(utm_source="", utm_medium="cpc", referrer_url="")

    def test_referrer_contains_match(self) -> None:
        rule = LeadSourceRule(
            referrer_contains="trustpilot.com",
            derived_source="referral",
            is_active=True,
        )
        assert rule.matches(
            utm_source="",
            utm_medium="",
            referrer_url="https://www.trustpilot.com/review/example",
        )
        assert not rule.matches(
            utm_source="",
            utm_medium="",
            referrer_url="https://google.com",
        )

    def test_multiple_conditions_require_all_match(self) -> None:
        rule = LeadSourceRule(
            utm_source="google",
            utm_medium="cpc",
            derived_source="google_ads",
            is_active=True,
        )
        # Both match
        assert rule.matches(utm_source="google", utm_medium="cpc", referrer_url="")
        # Only source matches
        assert not rule.matches(
            utm_source="google", utm_medium="email", referrer_url=""
        )
        # Only medium matches
        assert not rule.matches(utm_source="bing", utm_medium="cpc", referrer_url="")

    def test_case_insensitive_matching(self) -> None:
        rule = LeadSourceRule(
            utm_source="Google",
            utm_medium="CPC",
            derived_source="google_ads",
            is_active=True,
        )
        assert rule.matches(utm_source="GOOGLE", utm_medium="cpc", referrer_url="")


class TestLeadSourceRuleOverride:
    """Tests for rule overrides via database queries."""

    def test_rule_overrides_ssot_default(self) -> None:
        # Create a custom rule that overrides Google CPC to a different source
        LeadSourceRule.objects.create(
            name="Test Override",
            utm_source="google",
            utm_medium="cpc",
            derived_source="referral",
            derived_source_detail="custom-tracking",
            priority=10,
            is_active=True,
        )

        source, detail = derive_lead_source(
            utm_source="google",
            utm_medium="cpc",
        )

        # Should use rule, not SSOT default
        assert source == "referral"
        assert "custom-tracking" in detail

    def test_priority_ordering_first_match_wins(self) -> None:
        # Create two overlapping rules with different priorities
        LeadSourceRule.objects.create(
            name="Low Priority",
            utm_source="partner",
            derived_source="unknown",
            priority=100,
            is_active=True,
        )
        LeadSourceRule.objects.create(
            name="High Priority",
            utm_source="partner",
            derived_source="referral",
            priority=10,
            is_active=True,
        )

        source, _ = derive_lead_source(utm_source="partner")

        # Higher priority (lower number) wins
        assert source == "referral"

    def test_inactive_rule_skipped(self) -> None:
        # Create an inactive rule
        LeadSourceRule.objects.create(
            name="Inactive Rule",
            utm_source="partner",
            derived_source="offline",
            priority=1,
            is_active=False,
        )

        source, _ = derive_lead_source(utm_source="partner")

        # Should fall through to SSOT default (unknown for unrecognised source)
        assert source == "unknown"

    def test_no_matching_rules_uses_ssot_defaults(self) -> None:
        # Create a rule that won't match
        LeadSourceRule.objects.create(
            name="Unrelated Rule",
            utm_source="some-other-source",
            derived_source="offline",
            priority=1,
            is_active=True,
        )

        source, _ = derive_lead_source(
            utm_source="google",
            utm_medium="cpc",
        )

        # Should use SSOT default
        assert source == "google_ads"

    def test_rule_derived_source_detail_appends_campaign(self) -> None:
        LeadSourceRule.objects.create(
            name="With Detail",
            utm_source="partner",
            derived_source="referral",
            derived_source_detail="partner-network",
            priority=10,
            is_active=True,
        )

        source, detail = derive_lead_source(
            utm_source="partner",
            utm_campaign="spring-2025",
        )

        assert source == "referral"
        assert "partner-network" in detail
        assert "campaign=spring-2025" in detail


class TestLeadSourceRuleModel:
    """Tests for LeadSourceRule model behavior."""

    def test_str_representation_with_all_fields(self) -> None:
        rule = LeadSourceRule(
            name="My Rule",
            utm_source="google",
            utm_medium="cpc",
            referrer_contains="example.com",
            derived_source="google_ads",
        )
        str_repr = str(rule)
        assert "My Rule:" in str_repr
        assert "utm_source=google" in str_repr
        assert "utm_medium=cpc" in str_repr
        assert "referrer~example.com" in str_repr
        assert "google_ads" in str_repr

    def test_str_representation_catch_all(self) -> None:
        rule = LeadSourceRule(
            derived_source="unknown",
        )
        str_repr = str(rule)
        assert "(catch-all)" in str_repr

    def test_ordering_by_priority_and_id(self) -> None:
        rule1 = LeadSourceRule.objects.create(
            utm_source="a",
            derived_source="unknown",
            priority=10,
        )
        rule2 = LeadSourceRule.objects.create(
            utm_source="b",
            derived_source="unknown",
            priority=10,
        )
        rule3 = LeadSourceRule.objects.create(
            utm_source="c",
            derived_source="unknown",
            priority=50,
        )

        rules = list(LeadSourceRule.objects.all())
        # First two have same priority, ordered by id (creation order)
        assert rules[0] == rule1
        assert rules[1] == rule2
        assert rules[2] == rule3
