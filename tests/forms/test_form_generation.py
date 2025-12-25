"""
Name: Dynamic form generation tests
Path: tests/forms/test_form_generation.py
Purpose: Validate dynamic Django form creation from FormDefinition blocks.
Family: Forms, Dynamic Forms foundation.
Dependencies: pytest, Django forms, FormDefinition.
"""

from __future__ import annotations

import pytest
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from sum_core.forms.dynamic import DynamicFormGenerator
from sum_core.forms.models import FormDefinition


def option(value: str, label: str) -> tuple[str, dict[str, str]]:
    """Convenience helper to build choice tuples."""
    return ("option", {"value": value, "label": label})


@pytest.mark.django_db
def test_generate_form_class_maps_fields_and_order(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Contact",
        slug="contact",
        fields=[
            (
                "text_input",
                {
                    "field_name": "first_name",
                    "label": "First name",
                    "help_text": "Tell us who you are.",
                    "max_length": 120,
                    "placeholder": "Jane",
                    "css_class": "u-input",
                },
            ),
            ("section_heading", {"heading": "Contact details", "level": "h2"}),
            (
                "email_input",
                {
                    "field_name": "email",
                    "label": "Email",
                    "placeholder": "you@example.com",
                    "css_class": "u-input",
                },
            ),
            ("help_text", {"text": "<p>We will reply quickly.</p>"}),
            (
                "select",
                {
                    "field_name": "service",
                    "label": "Service",
                    "choices": [
                        option("roofing", "Roofing"),
                        option("siding", "Siding"),
                    ],
                    "allow_multiple": False,
                    "css_class": "u-select",
                },
            ),
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()
    form = form_class()

    assert list(form.fields.keys()) == ["first_name", "email", "service"]
    assert form.fields["first_name"].label == "First name"
    assert form.fields["first_name"].help_text == "Tell us who you are."
    assert form.fields["first_name"].widget.attrs["class"] == "u-input"
    assert form.fields["first_name"].widget.attrs["placeholder"] == "Jane"


@pytest.mark.django_db
def test_field_mapping_types_and_widgets(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="All Fields",
        slug="all-fields",
        fields=[
            (
                "text_input",
                {
                    "field_name": "first_name",
                    "label": "First name",
                    "max_length": 100,
                },
            ),
            (
                "email_input",
                {
                    "field_name": "email",
                    "label": "Email",
                },
            ),
            (
                "phone_input",
                {
                    "field_name": "phone",
                    "label": "Phone",
                    "format_mask": "(###) ###-####",
                    "placeholder": "555-123-4567",
                    "required": False,
                },
            ),
            (
                "textarea",
                {
                    "field_name": "message",
                    "label": "Message",
                    "rows": 6,
                    "max_length": 500,
                    "placeholder": "Tell us more",
                },
            ),
            (
                "select",
                {
                    "field_name": "service",
                    "label": "Service",
                    "choices": [option("roofing", "Roofing")],
                    "allow_multiple": False,
                },
            ),
            (
                "select",
                {
                    "field_name": "materials",
                    "label": "Materials",
                    "choices": [
                        option("shingles", "Shingles"),
                        option("metal", "Metal"),
                    ],
                    "allow_multiple": True,
                },
            ),
            (
                "checkbox",
                {
                    "field_name": "terms",
                    "label": "Accept terms",
                    "checked_value": "agree",
                },
            ),
            (
                "checkbox_group",
                {
                    "field_name": "channels",
                    "label": "Channels",
                    "choices": [
                        option("email", "Email"),
                        option("sms", "SMS"),
                    ],
                    "required": False,
                },
            ),
            (
                "radio_buttons",
                {
                    "field_name": "contact_method",
                    "label": "Preferred contact",
                    "choices": [
                        option("phone", "Phone"),
                        option("email", "Email"),
                    ],
                },
            ),
            (
                "file_upload",
                {
                    "field_name": "resume",
                    "label": "Resume",
                    "allowed_extensions": ".pdf,.doc",
                    "max_file_size_mb": 5,
                },
            ),
        ],
    )

    form = DynamicFormGenerator(form_def).generate_form_class()()

    assert isinstance(form.fields["first_name"], forms.CharField)
    assert isinstance(form.fields["email"], forms.EmailField)
    assert isinstance(form.fields["phone"], forms.CharField)
    assert isinstance(form.fields["message"], forms.CharField)
    assert isinstance(form.fields["service"], forms.ChoiceField)
    assert isinstance(form.fields["materials"], forms.MultipleChoiceField)
    assert isinstance(form.fields["terms"], forms.BooleanField)
    assert isinstance(form.fields["channels"], forms.MultipleChoiceField)
    assert isinstance(form.fields["contact_method"], forms.ChoiceField)
    assert isinstance(form.fields["resume"], forms.FileField)

    assert isinstance(form.fields["first_name"].widget, forms.TextInput)
    assert isinstance(form.fields["email"].widget, forms.EmailInput)
    assert isinstance(form.fields["message"].widget, forms.Textarea)
    assert isinstance(form.fields["service"].widget, forms.Select)
    assert isinstance(form.fields["materials"].widget, forms.SelectMultiple)
    assert isinstance(form.fields["terms"].widget, forms.CheckboxInput)
    assert isinstance(form.fields["channels"].widget, forms.CheckboxSelectMultiple)
    assert isinstance(form.fields["contact_method"].widget, forms.RadioSelect)
    assert isinstance(form.fields["resume"].widget, forms.ClearableFileInput)

    assert form.fields["phone"].required is False
    assert form.fields["channels"].required is False
    assert form.fields["phone"].widget.attrs["data-format-mask"] == "(###) ###-####"
    assert form.fields["phone"].widget.attrs["placeholder"] == "555-123-4567"
    assert form.fields["message"].widget.attrs["rows"] == 6

    assert list(form.fields["service"].choices) == [("roofing", "Roofing")]
    assert list(form.fields["materials"].choices) == [
        ("shingles", "Shingles"),
        ("metal", "Metal"),
    ]


@pytest.mark.django_db
def test_file_upload_validation(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Files",
        slug="files",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "resume",
                    "label": "Resume",
                    "allowed_extensions": ".pdf",
                    "max_file_size_mb": 1,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    good_file = SimpleUploadedFile("resume.pdf", b"pdf")
    form = form_class(data={}, files={"resume": good_file})
    assert form.is_valid()

    bad_extension = SimpleUploadedFile("resume.exe", b"x")
    form = form_class(data={}, files={"resume": bad_extension})
    assert not form.is_valid()
    assert "resume" in form.errors

    oversized_file = SimpleUploadedFile("resume.pdf", b"x" * (1024 * 1024 + 1))
    form = form_class(data={}, files={"resume": oversized_file})
    assert not form.is_valid()
    assert "resume" in form.errors
