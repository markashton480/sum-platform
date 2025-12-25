"""
Name: Dynamic form generation
Path: core/sum_core/forms/dynamic.py
Purpose: Generate Django forms from FormDefinition StreamField blocks at runtime.
Family: Forms, Dynamic Forms foundation.
Dependencies: Django forms, FormDefinition fields.
"""

from __future__ import annotations

import os
from typing import Any

from django import forms


class DynamicFormGenerator:
    """
    Generates Django Form classes from FormDefinition at runtime.

    Usage:
        generator = DynamicFormGenerator(form_definition)
        FormClass = generator.generate_form_class()
        form = FormClass(data=request.POST, files=request.FILES)
    """

    def __init__(self, form_definition) -> None:
        self.form_definition = form_definition

    def generate_form_class(self):
        """Returns a Django Form class with fields from FormDefinition."""
        fields: dict[str, forms.Field] = {}
        file_rules: dict[str, dict[str, Any]] = {}

        for block in self.form_definition.fields:
            mapped = self._map_block_to_field(block.block_type, block.value)
            if mapped is None:
                continue
            field_name, field, file_rule = mapped
            fields[field_name] = field
            if file_rule:
                file_rules[field_name] = file_rule

        def clean(form_instance):
            cleaned = forms.Form.clean(form_instance)
            file_validation_rules = (
                getattr(form_instance, "_file_validation_rules", {}) or {}
            )
            for field_name, rule in file_validation_rules.items():
                uploaded = cleaned.get(field_name)
                if not uploaded:
                    continue

                errors = []
                extensions = rule.get("extensions") or []
                max_size_bytes = rule.get("max_size_bytes")
                max_size_mb = rule.get("max_size_mb")

                if extensions:
                    original_name = uploaded.name or ""
                    _, original_ext = os.path.splitext(original_name)
                    ext = original_ext.lower()
                    if ext not in extensions:
                        errors.append(
                            f"File type '{original_ext or 'unknown'}' "
                            "is not allowed."
                        )

                if max_size_bytes and uploaded.size > max_size_bytes:
                    max_size_mb_display = max_size_mb
                    if not max_size_mb_display and max_size_bytes:
                        max_size_mb_display = max_size_bytes / (1024 * 1024)
                    errors.append(f"File must be {max_size_mb_display:g}MB or smaller.")

                for message in errors:
                    form_instance.add_error(field_name, message)

            return cleaned

        attrs: dict[str, Any] = {"__module__": __name__}
        attrs.update(fields)
        attrs["_file_validation_rules"] = file_rules
        attrs["form_definition"] = self.form_definition
        attrs["clean"] = clean

        suffix = self.form_definition.pk or "Runtime"
        return type(f"DynamicForm{suffix}", (forms.Form,), attrs)

    def _map_block_to_field(self, block_type, block_value):
        """Maps a FormFieldBlock to a Django form field."""
        if block_type in {"section_heading", "help_text"}:
            return None

        field_name = block_value.get("field_name")
        label = block_value.get("label", "")
        help_text = block_value.get("help_text", "")
        required = bool(block_value.get("required", True))
        widget_attrs = self._build_widget_attrs(block_value)

        if block_type == "text_input":
            field = forms.CharField(
                label=label,
                required=required,
                help_text=help_text,
                max_length=block_value.get("max_length"),
                widget=forms.TextInput(
                    attrs=self._apply_placeholder(block_value, widget_attrs)
                ),
            )
            return field_name, field, None

        if block_type == "email_input":
            field = forms.EmailField(
                label=label,
                required=required,
                help_text=help_text,
                max_length=block_value.get("max_length"),
                widget=forms.EmailInput(
                    attrs=self._apply_placeholder(block_value, widget_attrs)
                ),
            )
            return field_name, field, None

        if block_type == "phone_input":
            attrs = self._apply_placeholder(block_value, widget_attrs)
            format_mask = block_value.get("format_mask")
            if format_mask:
                attrs["data-format-mask"] = format_mask
            field = forms.CharField(
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.TextInput(attrs=attrs),
            )
            return field_name, field, None

        if block_type == "textarea":
            attrs = self._apply_placeholder(block_value, widget_attrs)
            rows = block_value.get("rows")
            if rows:
                attrs["rows"] = rows
            field = forms.CharField(
                label=label,
                required=required,
                help_text=help_text,
                max_length=block_value.get("max_length"),
                widget=forms.Textarea(attrs=attrs),
            )
            return field_name, field, None

        if block_type == "select":
            choices = self._extract_choices(block_value.get("choices"))
            allow_multiple = bool(block_value.get("allow_multiple", False))
            if allow_multiple:
                field = forms.MultipleChoiceField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    choices=choices,
                    widget=forms.SelectMultiple(attrs=widget_attrs),
                )
            else:
                field = forms.ChoiceField(
                    label=label,
                    required=required,
                    help_text=help_text,
                    choices=choices,
                    widget=forms.Select(attrs=widget_attrs),
                )
            return field_name, field, None

        if block_type == "checkbox":
            attrs = dict(widget_attrs)
            checked_value = block_value.get("checked_value")
            if checked_value:
                attrs["value"] = checked_value
            field = forms.BooleanField(
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.CheckboxInput(attrs=attrs),
            )
            return field_name, field, None

        if block_type == "checkbox_group":
            field = forms.MultipleChoiceField(
                label=label,
                required=required,
                help_text=help_text,
                choices=self._extract_choices(block_value.get("choices")),
                widget=forms.CheckboxSelectMultiple(attrs=widget_attrs),
            )
            return field_name, field, None

        if block_type == "radio_buttons":
            field = forms.ChoiceField(
                label=label,
                required=required,
                help_text=help_text,
                choices=self._extract_choices(block_value.get("choices")),
                widget=forms.RadioSelect(attrs=widget_attrs),
            )
            return field_name, field, None

        if block_type == "file_upload":
            max_size_mb = block_value.get("max_file_size_mb")
            if max_size_mb is not None and max_size_mb > 0:
                max_size_bytes = max_size_mb * 1024 * 1024
            else:
                max_size_bytes = None
            file_rule = {
                "extensions": self._normalize_extensions(
                    block_value.get("allowed_extensions", "")
                ),
                "max_size_bytes": max_size_bytes,
                "max_size_mb": max_size_mb,
            }
            field = forms.FileField(
                label=label,
                required=required,
                help_text=help_text,
                widget=forms.ClearableFileInput(attrs=widget_attrs),
            )
            return field_name, field, file_rule

        return None

    def _build_widget_attrs(self, block_value) -> dict[str, str]:
        attrs: dict[str, str] = {}
        css_class = block_value.get("css_class")
        if css_class:
            attrs["class"] = css_class
        return attrs

    def _apply_placeholder(self, block_value, attrs: dict[str, str]) -> dict[str, str]:
        placeholder = block_value.get("placeholder")
        if placeholder:
            attrs = dict(attrs)
            attrs["placeholder"] = placeholder
        return attrs

    def _extract_choices(self, choices_value) -> list[tuple[str, str]]:
        if not choices_value:
            return []
        choices = []
        for choice in choices_value:
            value = getattr(choice, "value", choice)
            choices.append((value["value"], value["label"]))
        return choices

    def _normalize_extensions(self, raw_extensions: str) -> list[str]:
        if not raw_extensions:
            return []
        normalized = []
        for raw in raw_extensions.split(","):
            ext = raw.strip().lower()
            if not ext:
                continue
            if not ext.startswith("."):
                ext = f".{ext}"
            normalized.append(ext)
        return normalized
