"""
Name: Link Blocks Tests
Path: core/sum_core/navigation/tests/test_blocks.py
Purpose: Unit tests for UniversalLinkBlock and related link components.
Family: SUM Platform Navigation System - Tests
Dependencies: pytest, wagtail, sum_core.blocks.links
"""

from unittest.mock import MagicMock

import pytest
from sum_core.blocks.links import (
    ANCHOR_PATTERN,
    LINK_TYPE_CHOICES,
    UniversalLinkBlock,
    UniversalLinkValue,
)
from wagtail.blocks import StructBlockValidationError

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def link_block():
    """Return a fresh UniversalLinkBlock instance."""
    return UniversalLinkBlock()


@pytest.fixture
def mock_page():
    """Return a mock Wagtail Page object."""
    page = MagicMock()
    page.url = "/about-us/"
    page.title = "About Us"
    return page


def make_link_value(link_block, **kwargs):
    """
    Helper to create a UniversalLinkValue from raw data.

    This bypasses validation to create test values directly.
    """
    # Set defaults for all fields
    defaults = {
        "link_type": "page",
        "page": None,
        "url": None,
        "email": None,
        "phone": None,
        "anchor": None,
        "link_text": None,
        "open_in_new_tab": None,
    }
    defaults.update(kwargs)

    # Create the StructValue directly
    return UniversalLinkValue(link_block, defaults)


# =============================================================================
# Test: Page Link
# =============================================================================


@pytest.mark.django_db
class TestPageLink:
    """Tests for page-type links."""

    def test_page_link_returns_page_url(self, link_block, mock_page):
        """Page link href should return the page's URL."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
        )

        assert value.href == "/about-us/"

    def test_page_link_without_page_returns_hash(self, link_block):
        """Page link without page set should return '#'."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=None,
        )

        assert value.href == "#"

    def test_text_falls_back_to_page_title(self, link_block, mock_page):
        """Without custom text, should use page title."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
        )

        assert value.text == "About Us"


# =============================================================================
# Test: URL Link
# =============================================================================


@pytest.mark.django_db
class TestURLLink:
    """Tests for URL-type links."""

    def test_url_link_returns_url(self, link_block):
        """URL link href should return the URL as-is."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com/page",
        )

        assert value.href == "https://example.com/page"

    def test_url_link_without_url_returns_hash(self, link_block):
        """URL link without URL set should return '#'."""
        value = make_link_value(
            link_block,
            link_type="url",
            url=None,
        )

        assert value.href == "#"

    def test_text_falls_back_to_domain_for_url(self, link_block):
        """Without custom text, URL should use domain."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://www.example.com/long/path/here",
        )

        # Should strip www. prefix
        assert value.text == "example.com"

    def test_text_falls_back_to_domain_without_www(self, link_block):
        """Domain extraction should work without www."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://docs.python.org/3/",
        )

        assert value.text == "docs.python.org"


# =============================================================================
# Test: Email Link
# =============================================================================


@pytest.mark.django_db
class TestEmailLink:
    """Tests for email-type links."""

    def test_email_link_returns_mailto(self, link_block):
        """Email link href should return mailto: prefixed."""
        value = make_link_value(
            link_block,
            link_type="email",
            email="hello@example.com",
        )

        assert value.href == "mailto:hello@example.com"

    def test_email_link_without_email_returns_hash(self, link_block):
        """Email link without email set should return '#'."""
        value = make_link_value(
            link_block,
            link_type="email",
            email=None,
        )

        assert value.href == "#"

    def test_email_text_fallback(self, link_block):
        """Without custom text, email should show the address."""
        value = make_link_value(
            link_block,
            link_type="email",
            email="contact@company.co.uk",
        )

        assert value.text == "contact@company.co.uk"


# =============================================================================
# Test: Phone Link
# =============================================================================


@pytest.mark.django_db
class TestPhoneLink:
    """Tests for phone-type links."""

    def test_phone_link_returns_tel(self, link_block):
        """Phone link href should return tel: prefixed."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="02079460958",
        )

        assert value.href == "tel:02079460958"

    def test_phone_strips_spaces(self, link_block):
        """Phone href should strip spaces."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="020 7946 0958",
        )

        assert value.href == "tel:02079460958"

    def test_phone_strips_hyphens(self, link_block):
        """Phone href should strip hyphens."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="020-7946-0958",
        )

        assert value.href == "tel:02079460958"

    def test_phone_preserves_plus(self, link_block):
        """Phone href should preserve leading + for international format."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="+44 20 7946 0958",
        )

        assert value.href == "tel:+442079460958"

    def test_phone_strips_parentheses(self, link_block):
        """Phone href should strip parentheses."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="+1 (555) 123-4567",
        )

        assert value.href == "tel:+15551234567"

    def test_phone_link_without_phone_returns_hash(self, link_block):
        """Phone link without phone set should return '#'."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone=None,
        )

        assert value.href == "#"


# =============================================================================
# Test: Anchor Link
# =============================================================================


@pytest.mark.django_db
class TestAnchorLink:
    """Tests for anchor-type links."""

    def test_anchor_returns_hash_id(self, link_block):
        """Anchor link href should return hash-prefixed ID."""
        value = make_link_value(
            link_block,
            link_type="anchor",
            anchor="contact-section",
        )

        assert value.href == "#contact-section"

    def test_anchor_strips_leading_hash(self, link_block):
        """Anchor should strip leading # if editor includes it."""
        value = make_link_value(
            link_block,
            link_type="anchor",
            anchor="#contact-section",
        )

        assert value.href == "#contact-section"

    def test_anchor_link_without_anchor_returns_hash(self, link_block):
        """Anchor link without anchor set should return '#'."""
        value = make_link_value(
            link_block,
            link_type="anchor",
            anchor=None,
        )

        assert value.href == "#"

    def test_anchor_validation_invalid_chars(self, link_block):
        """Anchor with invalid characters should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "anchor",
                    "anchor": "invalid anchor!",  # spaces and ! not allowed
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "anchor" in exc_info.value.block_errors

    def test_anchor_validation_starts_with_number(self, link_block):
        """Anchor starting with number should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "anchor",
                    "anchor": "123-section",  # must start with letter
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "anchor" in exc_info.value.block_errors

    def test_anchor_validation_valid_complex_id(self, link_block):
        """Valid complex anchor ID should pass validation."""
        # Should not raise
        result = link_block.clean(
            {
                "link_type": "anchor",
                "anchor": "Section-123_content",
                "page": None,
                "url": None,
                "email": None,
                "phone": None,
                "link_text": None,
                "open_in_new_tab": None,
            }
        )

        assert result["anchor"] == "Section-123_content"


# =============================================================================
# Test: Validation
# =============================================================================


@pytest.mark.django_db
class TestValidation:
    """Tests for block validation logic."""

    def test_validation_page_type_requires_page(self, link_block):
        """Page type without page should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "page",
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "anchor": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "page" in exc_info.value.block_errors

    def test_validation_url_type_requires_url(self, link_block):
        """URL type without URL should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "url",
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "anchor": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "url" in exc_info.value.block_errors

    def test_validation_email_type_requires_email(self, link_block):
        """Email type without email should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "email",
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "anchor": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "email" in exc_info.value.block_errors

    def test_validation_phone_type_requires_phone(self, link_block):
        """Phone type without phone should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "phone",
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": None,
                    "anchor": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        assert "phone" in exc_info.value.block_errors

    def test_validation_phone_must_contain_digit(self, link_block):
        """Phone without any digits should fail validation."""
        with pytest.raises(StructBlockValidationError) as exc_info:
            link_block.clean(
                {
                    "link_type": "phone",
                    "page": None,
                    "url": None,
                    "email": None,
                    "phone": "not-a-number",
                    "anchor": None,
                    "link_text": None,
                    "open_in_new_tab": None,
                }
            )

        errors = exc_info.value.block_errors
        assert "phone" in errors
        assert "digit" in str(errors["phone"]).lower()


# =============================================================================
# Test: is_external
# =============================================================================


@pytest.mark.django_db
class TestIsExternal:
    """Tests for is_external property."""

    def test_is_external_only_for_url_type(self, link_block):
        """Only URL type should be considered external."""
        url_value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
        )
        assert url_value.is_external is True

    def test_page_is_not_external(self, link_block, mock_page):
        """Page type should not be external."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
        )
        assert value.is_external is False

    def test_email_is_not_external(self, link_block):
        """Email type should not be external."""
        value = make_link_value(
            link_block,
            link_type="email",
            email="test@example.com",
        )
        assert value.is_external is False

    def test_phone_is_not_external(self, link_block):
        """Phone type should not be external."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="+447123456789",
        )
        assert value.is_external is False

    def test_anchor_is_not_external(self, link_block):
        """Anchor type should not be external."""
        value = make_link_value(
            link_block,
            link_type="anchor",
            anchor="section",
        )
        assert value.is_external is False


# =============================================================================
# Test: Attributes (attrs/attrs_str)
# =============================================================================


@pytest.mark.django_db
class TestAttrs:
    """Tests for attrs and attrs_str properties."""

    def test_attrs_external_includes_rel(self, link_block):
        """External URL attrs should include rel='noopener noreferrer'."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
        )

        assert value.attrs.get("rel") == "noopener noreferrer"

    def test_attrs_new_tab_includes_target(self, link_block):
        """When opening in new tab, attrs should include target='_blank'."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
        )

        assert value.attrs.get("target") == "_blank"

    def test_attrs_phone_includes_data_contact_type(self, link_block):
        """Phone link attrs should include data-contact-type='phone'."""
        value = make_link_value(
            link_block,
            link_type="phone",
            phone="+447123456789",
        )

        assert value.attrs.get("data-contact-type") == "phone"

    def test_attrs_email_includes_data_contact_type(self, link_block):
        """Email link attrs should include data-contact-type='email'."""
        value = make_link_value(
            link_block,
            link_type="email",
            email="test@example.com",
        )

        assert value.attrs.get("data-contact-type") == "email"

    def test_attrs_str_formats_correctly(self, link_block):
        """attrs_str should format attrs as HTML attribute string."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
        )

        attrs_str = value.attrs_str
        assert 'target="_blank"' in attrs_str
        assert 'rel="noopener noreferrer"' in attrs_str

    def test_attrs_str_empty_when_no_attrs(self, link_block, mock_page):
        """attrs_str should be empty string when no attrs needed."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
        )

        assert value.attrs_str == ""


# =============================================================================
# Test: Custom Text
# =============================================================================


@pytest.mark.django_db
class TestCustomText:
    """Tests for custom link text behavior."""

    def test_text_uses_custom_when_provided(self, link_block, mock_page):
        """Custom link_text should override page title."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
            link_text="Learn More About Us",
        )

        assert value.text == "Learn More About Us"

    def test_text_uses_custom_for_url(self, link_block):
        """Custom link_text should override domain for URL."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
            link_text="Visit Our Partner",
        )

        assert value.text == "Visit Our Partner"

    def test_text_uses_custom_for_email(self, link_block):
        """Custom link_text should override email address."""
        value = make_link_value(
            link_block,
            link_type="email",
            email="contact@example.com",
            link_text="Get in Touch",
        )

        assert value.text == "Get in Touch"


# =============================================================================
# Test: New Tab Override (AC8)
# =============================================================================


@pytest.mark.django_db
class TestNewTabOverride:
    """Tests for open_in_new_tab override behavior."""

    def test_external_url_defaults_opens_new_tab(self, link_block):
        """External URL should default to opening in new tab."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
            open_in_new_tab=None,  # Unset = use default
        )

        assert value.opens_new_tab is True
        assert value.attrs.get("target") == "_blank"
        assert value.attrs.get("rel") == "noopener noreferrer"

    def test_external_url_can_disable_new_tab_when_overridden(self, link_block):
        """External URL can be forced to NOT open in new tab."""
        value = make_link_value(
            link_block,
            link_type="url",
            url="https://example.com",
            open_in_new_tab=False,  # Explicit False
        )

        assert value.opens_new_tab is False
        assert "target" not in value.attrs
        assert "rel" not in value.attrs

    def test_internal_link_can_open_in_new_tab_when_forced(self, link_block, mock_page):
        """Internal page link can be forced to open in new tab."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
            open_in_new_tab=True,  # Explicit True
        )

        assert value.opens_new_tab is True
        assert value.attrs.get("target") == "_blank"

    def test_internal_link_defaults_same_tab(self, link_block, mock_page):
        """Internal page link should default to same tab."""
        value = make_link_value(
            link_block,
            link_type="page",
            page=mock_page,
            open_in_new_tab=None,  # Unset = use default
        )

        assert value.opens_new_tab is False
        assert "target" not in value.attrs


# =============================================================================
# Test: Link Type Choices
# =============================================================================


@pytest.mark.django_db
class TestLinkTypeChoices:
    """Tests for LINK_TYPE_CHOICES configuration."""

    def test_link_type_choices_has_five_types(self):
        """LINK_TYPE_CHOICES should have exactly 5 types."""
        assert len(LINK_TYPE_CHOICES) == 5

    def test_link_type_choices_contains_expected_types(self):
        """LINK_TYPE_CHOICES should contain all expected types."""
        type_keys = [choice[0] for choice in LINK_TYPE_CHOICES]

        assert "page" in type_keys
        assert "url" in type_keys
        assert "email" in type_keys
        assert "phone" in type_keys
        assert "anchor" in type_keys


# =============================================================================
# Test: Anchor Pattern Regex
# =============================================================================


@pytest.mark.django_db
class TestAnchorPattern:
    """Tests for ANCHOR_PATTERN regex."""

    def test_valid_simple_anchor(self):
        """Simple lowercase anchor should match."""
        assert ANCHOR_PATTERN.match("contact")

    def test_valid_anchor_with_hyphen(self):
        """Anchor with hyphen should match."""
        assert ANCHOR_PATTERN.match("contact-us")

    def test_valid_anchor_with_underscore(self):
        """Anchor with underscore should match."""
        assert ANCHOR_PATTERN.match("contact_section")

    def test_valid_anchor_with_numbers(self):
        """Anchor with numbers (not first) should match."""
        assert ANCHOR_PATTERN.match("section1")
        assert ANCHOR_PATTERN.match("a123")

    def test_valid_anchor_uppercase(self):
        """Uppercase anchor should match."""
        assert ANCHOR_PATTERN.match("ContactUs")

    def test_invalid_starts_with_number(self):
        """Anchor starting with number should not match."""
        assert ANCHOR_PATTERN.match("1section") is None

    def test_invalid_contains_space(self):
        """Anchor with space should not match."""
        assert ANCHOR_PATTERN.match("contact us") is None

    def test_invalid_contains_special_chars(self):
        """Anchor with special chars should not match."""
        assert ANCHOR_PATTERN.match("contact!") is None
        assert ANCHOR_PATTERN.match("contact@us") is None
