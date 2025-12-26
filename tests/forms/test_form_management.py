"""
Name: Form management tests
Path: tests/forms/test_form_management.py
Purpose: Validate FormDefinition cloning and DynamicFormBlock behavior.
Family: Forms, Dynamic Forms management.
Dependencies: pytest, Django ORM, Wagtail blocks, Django templates.
"""

from __future__ import annotations

import re
from types import SimpleNamespace

import pytest
from django.template.loader import render_to_string
from django.test import RequestFactory
from sum_core.blocks.forms import DynamicFormBlock
from sum_core.forms.models import FormDefinition


@pytest.mark.django_db
def test_clone_form_definition_creates_unique_inactive_copy(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Contact Form",
        slug="contact",
    )

    cloned = form_def.clone()

    assert cloned.pk is not None
    assert cloned.pk != form_def.pk
    assert cloned.is_active is False
    assert cloned.slug.startswith("contact-copy")
    assert cloned.name == "Contact Form (Copy)"


@pytest.mark.django_db
def test_clone_form_definition_increments_slug(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Support Form",
        slug="support",
    )

    first_clone = form_def.clone()
    second_clone = form_def.clone()

    assert first_clone.slug != second_clone.slug
    assert first_clone.slug.startswith("support-copy")
    assert second_clone.slug.startswith("support-copy")


@pytest.mark.django_db
def test_dynamic_form_block_flags_inactive_form(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Inactive Form",
        slug="inactive-form",
        is_active=False,
    )

    block = DynamicFormBlock()
    value = block.to_python({"form_definition": form_def.pk})
    context = block.get_context(value)

    assert context["form_inactive_warning"] is True


@pytest.mark.django_db
def test_dynamic_form_template_has_unique_id_and_multi_form_js(wagtail_default_site):
    form_def = FormDefinition.objects.create(
        site=wagtail_default_site,
        name="Inline Form",
        slug="inline-form",
    )

    request = RequestFactory().get("/")
    block_context = SimpleNamespace(id="block-1")
    value = SimpleNamespace(
        form_definition=form_def,
        presentation_style="inline",
        cta_button_text="Submit",
    )

    rendered = render_to_string(
        "sum_core/blocks/dynamic_form_block.html",
        context={"self": value, "block": block_context},
        request=request,
    )

    assert re.search(r'id="[^"]*block-1"', rendered)
    assert "data-dynamic-form" in rendered or "js-async-form" in rendered
