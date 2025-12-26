"""
Name: Form field blocks tests
Path: tests/forms/test_field_blocks.py
Purpose: Validate dynamic form field StreamField blocks and constraints.
Family: Forms, Dynamic Forms foundation.
Dependencies: pytest, Wagtail blocks, FormDefinition model.
"""

from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from sum_core.forms.fields import (
    FORM_FIELD_BLOCKS,
    CheckboxBlock,
    CheckboxGroupBlock,
    EmailInputBlock,
    FileUploadBlock,
    FormFieldsStreamBlock,
    HelpTextBlock,
    PhoneInputBlock,
    RadioButtonsBlock,
    SectionHeadingBlock,
    SelectBlock,
    TextareaBlock,
    TextInputBlock,
)
from sum_core.forms.models import FormDefinition


def option(value: str, label: str) -> tuple[str, dict[str, str]]:
    """Convenience helper to build choice tuples."""
    return ("option", {"value": value, "label": label})


def test_form_field_blocks_export_has_all_entries():
    """FORM_FIELD_BLOCKS should expose all block definitions in order."""
    names = [name for name, _ in FORM_FIELD_BLOCKS]
    assert names == [
        "text_input",
        "email_input",
        "phone_input",
        "textarea",
        "select",
        "checkbox",
        "checkbox_group",
        "radio_buttons",
        "file_upload",
        "section_heading",
        "help_text",
    ]


def test_form_fields_stream_block_child_blocks_match_export():
    """FormFieldsStreamBlock should contain the same block keys as the export list."""
    block = FormFieldsStreamBlock()
    assert list(block.child_blocks.keys()) == [
        "text_input",
        "email_input",
        "phone_input",
        "textarea",
        "select",
        "checkbox",
        "checkbox_group",
        "radio_buttons",
        "file_upload",
        "section_heading",
        "help_text",
    ]


def test_text_input_block_accepts_valid_config():
    """TextInputBlock should clean valid configuration data."""
    block = TextInputBlock()
    cleaned = block.clean(
        {
            "field_name": "first_name",
            "label": "First name",
            "max_length": 150,
            "placeholder": "Your name",
            "required": True,
            "css_class": "u-full-width",
        }
    )

    assert cleaned["field_name"] == "first_name"
    assert cleaned["max_length"] == 150
    assert cleaned["required"] is True


def test_text_input_block_rejects_invalid_max_length():
    """max_length must be positive when provided."""
    block = TextInputBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "name",
                "label": "Name",
                "max_length": 0,
            }
        )


def test_email_input_block_inherits_validation():
    """EmailInputBlock should share validation with TextInputBlock."""
    block = EmailInputBlock()
    cleaned = block.clean(
        {
            "field_name": "email",
            "label": "Email",
            "placeholder": "you@example.com",
        }
    )

    assert cleaned["field_name"] == "email"
    assert cleaned["required"] is True


def test_phone_input_block_supports_mask_and_placeholder():
    """PhoneInputBlock should persist optional mask and placeholder."""
    block = PhoneInputBlock()
    cleaned = block.clean(
        {
            "field_name": "phone",
            "label": "Phone",
            "format_mask": "(###) ###-####",
            "placeholder": "555-123-4567",
            "required": False,
        }
    )

    assert cleaned["format_mask"] == "(###) ###-####"
    assert cleaned["required"] is False


def test_textarea_block_validates_rows_minimum():
    """TextareaBlock rows must be at least 1."""
    block = TextareaBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "message",
                "label": "Message",
                "rows": 0,
            }
        )


def test_select_block_requires_choices():
    """SelectBlock must include at least one option."""
    block = SelectBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "service",
                "label": "Service",
                "choices": [],
            }
        )


def test_select_block_accepts_multiple_options():
    """SelectBlock should clean when options are provided."""
    block = SelectBlock()
    cleaned = block.clean(
        {
            "field_name": "service",
            "label": "Service type",
            "choices": [
                option("roofing", "Roofing"),
                option("siding", "Siding"),
            ],
            "allow_multiple": True,
        }
    )

    assert len(cleaned["choices"]) == 2
    assert cleaned["allow_multiple"] is True


def test_checkbox_block_default_checked_value():
    """CheckboxBlock should default to 'yes' checked value when not provided."""
    block = CheckboxBlock()
    cleaned = block.clean(
        {
            "field_name": "terms",
            "label": "Accept terms",
        }
    )

    assert cleaned["checked_value"] == "yes"


def test_checkbox_group_requires_options():
    """CheckboxGroupBlock enforces at least one option."""
    block = CheckboxGroupBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "services",
                "label": "Services interested in",
                "choices": [],
            }
        )


def test_radio_buttons_require_options():
    """RadioButtonsBlock enforces at least one option."""
    block = RadioButtonsBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "contact_method",
                "label": "Preferred contact method",
                "choices": [],
            }
        )


def test_file_upload_block_validates_size_and_extensions():
    """FileUploadBlock should validate required fields and limits."""
    block = FileUploadBlock()

    with pytest.raises(ValidationError):
        block.clean(
            {
                "field_name": "resume",
                "label": "Resume",
                "allowed_extensions": ".pdf,.doc",
                "max_file_size_mb": 0,
            }
        )

    cleaned = block.clean(
        {
            "field_name": "resume",
            "label": "Resume",
            "allowed_extensions": ".pdf,.doc",
        }
    )

    assert cleaned["allowed_extensions"] == ".pdf,.doc"
    assert cleaned["max_file_size_mb"] == 10


def test_section_heading_block_supports_levels():
    """SectionHeadingBlock should accept valid heading levels."""
    block = SectionHeadingBlock()
    cleaned = block.clean({"heading": "Contact details", "level": "h3"})

    assert cleaned["heading"] == "Contact details"
    assert cleaned["level"] == "h3"


def test_section_heading_block_defaults_level():
    """SectionHeadingBlock should default to h2 when level is omitted."""
    block = SectionHeadingBlock()
    cleaned = block.clean({"heading": "Contact details"})

    assert cleaned["level"] == "h2"


def test_help_text_block_accepts_rich_text():
    """HelpTextBlock should allow rich text content."""
    block = HelpTextBlock()
    cleaned = block.clean({"text": "<p>Tell us about your project.</p>"})

    text_value = cleaned["text"]
    assert hasattr(text_value, "source")
    assert "project" in text_value.source


def test_form_definition_stream_field_uses_form_fields_block():
    """FormDefinition.fields should be configured with the form fields StreamBlock."""
    stream_field = FormDefinition._meta.get_field("fields")
    assert isinstance(stream_field.stream_block, FormFieldsStreamBlock)
