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
from django.utils import timezone
from sum_core.forms.dynamic import DynamicFormGenerator
from sum_core.forms.models import FormDefinition

# Check if libmagic is available for MIME validation tests
try:
    import magic

    magic.from_buffer(b"test", mime=True)
    LIBMAGIC_AVAILABLE = True
except (ImportError, AttributeError):
    LIBMAGIC_AVAILABLE = False
except Exception:
    # Catch MagicException and other errors during detection test
    LIBMAGIC_AVAILABLE = False

requires_libmagic = pytest.mark.skipif(
    not LIBMAGIC_AVAILABLE, reason="libmagic not available"
)


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
    assert "u-input" in form.fields["first_name"].widget.attrs["class"]
    assert "border-b-2" in form.fields["first_name"].widget.attrs["class"]
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

    # Valid PDF file with proper PDF header
    good_file = SimpleUploadedFile("resume.pdf", b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    form = form_class(data={}, files={"resume": good_file})
    assert form.is_valid()

    bad_extension = SimpleUploadedFile("resume.exe", b"x")
    form = form_class(data={}, files={"resume": bad_extension})
    assert not form.is_valid()
    assert "resume" in form.errors

    # Oversized file with proper PDF header
    oversized_file = SimpleUploadedFile(
        "resume.pdf", b"%PDF-1.4\n" + b"x" * (1024 * 1024 + 1)
    )
    form = form_class(data={}, files={"resume": oversized_file})
    assert not form.is_valid()
    assert "resume" in form.errors


@pytest.mark.django_db
def test_form_class_cache_reuses_definition_version(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Cached Form",
        slug="cached-form",
        fields=[
            (
                "text_input",
                {
                    "field_name": "name",
                    "label": "Name",
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()
    cached_class = DynamicFormGenerator(form_def).generate_form_class()

    assert form_class is cached_class

    FormDefinition.objects.filter(pk=form_def.pk).update(
        updated_at=timezone.now() + timezone.timedelta(seconds=1)
    )
    form_def.refresh_from_db()
    new_class = DynamicFormGenerator(form_def).generate_form_class()

    assert new_class is not form_class


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_rejects_spoofed_extensions(wagtail_default_site):
    """Test that MIME type validation catches files with spoofed extensions."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Secure Upload",
        slug="secure-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "document",
                    "label": "Document",
                    "allowed_extensions": ".pdf",
                    "max_file_size_mb": 5,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Valid PDF file with proper PDF header
    valid_pdf = SimpleUploadedFile("document.pdf", b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    form = form_class(data={}, files={"document": valid_pdf})
    assert form.is_valid(), f"Valid PDF should pass: {form.errors}"

    # Spoofed PDF: EXE file renamed to .pdf (MZ header for Windows executable)
    spoofed_pdf = SimpleUploadedFile("malicious.pdf", b"MZ\x90\x00" + b"x" * 100)
    form = form_class(data={}, files={"document": spoofed_pdf})
    assert not form.is_valid(), "Spoofed EXE as PDF should fail"
    assert "document" in form.errors
    assert any(
        "appears to be" in str(e).lower() and "expected" in str(e).lower()
        for e in form.errors["document"]
    ), f"Expected MIME mismatch error, got: {form.errors['document']}"


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_allows_valid_image_types(wagtail_default_site):
    """Test that MIME validation accepts valid image files."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Image Upload",
        slug="image-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "photo",
                    "label": "Photo",
                    "allowed_extensions": ".jpg,.png",
                    "max_file_size_mb": 5,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Valid PNG (complete PNG header with IHDR chunk)
    valid_png = SimpleUploadedFile(
        "photo.png",
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89",
    )
    form = form_class(data={}, files={"photo": valid_png})
    assert form.is_valid(), f"Valid PNG should pass: {form.errors}"

    # Valid JPEG (JPEG header with SOI and APP0 markers)
    valid_jpg = SimpleUploadedFile(
        "photo.jpg",
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00",
    )
    form = form_class(data={}, files={"photo": valid_jpg})
    assert form.is_valid(), f"Valid JPEG should pass: {form.errors}"


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_rejects_spoofed_images(wagtail_default_site):
    """Test that MIME validation rejects spoofed image files."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Photo Upload",
        slug="photo-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "image",
                    "label": "Image",
                    "allowed_extensions": ".png",
                    "max_file_size_mb": 5,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Text file renamed to .png
    spoofed_png = SimpleUploadedFile("fake.png", b"This is just text content")
    form = form_class(data={}, files={"image": spoofed_png})
    assert not form.is_valid(), "Text file masquerading as PNG should fail"
    assert "image" in form.errors


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_allows_office_documents(wagtail_default_site):
    """Test that MIME validation accepts valid Office documents."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Document Upload",
        slug="doc-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "file",
                    "label": "File",
                    "allowed_extensions": ".docx,.xlsx",
                    "max_file_size_mb": 10,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Valid DOCX (ZIP header - Office files are ZIP archives)
    valid_docx = SimpleUploadedFile("document.docx", b"PK\x03\x04" + b"\x00" * 100)
    form = form_class(data={}, files={"file": valid_docx})
    assert form.is_valid(), f"Valid DOCX should pass: {form.errors}"

    # Valid XLSX (ZIP header - Office files are ZIP archives)
    valid_xlsx = SimpleUploadedFile("spreadsheet.xlsx", b"PK\x03\x04" + b"\x00" * 100)
    form = form_class(data={}, files={"file": valid_xlsx})
    assert form.is_valid(), f"Valid XLSX should pass: {form.errors}"


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_with_unknown_extension(wagtail_default_site):
    """Test that unknown extensions pass through without MIME blocking."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Custom Upload",
        slug="custom-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "data",
                    "label": "Data File",
                    "allowed_extensions": ".xyz",  # Not in MIME mapping
                    "max_file_size_mb": 5,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Unknown extension should pass through (no MIME check)
    unknown_file = SimpleUploadedFile("data.xyz", b"custom data format")
    form = form_class(data={}, files={"data": unknown_file})
    assert form.is_valid(), f"Unknown extension should pass: {form.errors}"


@pytest.mark.django_db
@requires_libmagic
def test_mime_type_validation_empty_file(wagtail_default_site):
    """Test that empty files are caught by MIME validation."""
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="PDF Upload",
        slug="pdf-upload",
        fields=[
            (
                "file_upload",
                {
                    "field_name": "doc",
                    "label": "Document",
                    "allowed_extensions": ".pdf",
                    "max_file_size_mb": 5,
                },
            )
        ],
    )

    form_class = DynamicFormGenerator(form_def).generate_form_class()

    # Empty file
    empty_file = SimpleUploadedFile("empty.pdf", b"")
    form = form_class(data={}, files={"doc": empty_file})
    assert not form.is_valid(), "Empty file should fail"
    assert "doc" in form.errors
    assert any(
        "empty" in str(e).lower() for e in form.errors["doc"]
    ), f"Expected 'empty' in error message, got: {form.errors['doc']}"
