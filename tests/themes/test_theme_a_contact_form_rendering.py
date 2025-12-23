from __future__ import annotations

import pytest
from bs4 import BeautifulSoup
from bs4.element import Tag
from sum_core.blocks.forms import ContactFormBlock


def _get_classes(tag: Tag) -> list[str]:
    classes = tag.get("class")
    if not classes:
        return []
    if isinstance(classes, list):
        return [str(value) for value in classes]
    return str(classes).split()


@pytest.mark.django_db
def test_theme_a_contact_form_contract():
    block = ContactFormBlock()
    block_value = {
        "eyebrow": "Contact",
        "heading": "Let us help",
        "intro": "Tell us about the project.",
        "success_message": "Thanks for reaching out.",
        "submit_label": "Send enquiry",
    }

    html = block.render(block_value, context={"csrf_token": "testtoken"})
    soup = BeautifulSoup(html, "html.parser")

    section = soup.find("section")
    assert section is not None
    section_classes = _get_classes(section)
    assert "contact-form-block" in section_classes
    assert "bg-sage-black" in section_classes

    sticky_header = soup.select_one(".lg\\:sticky")
    assert sticky_header is not None

    form = soup.find("form", attrs={"id": "contact-form"})
    assert form is not None
    assert form.get("action") == "/forms/submit/"
    assert form.get("data-form-type") == "contact"
    assert form.get("data-success-message") == "Thanks for reaching out."
    assert form.get("data-error-message") == "Something went wrong. Please try again."

    csrf_input = form.find("input", attrs={"name": "csrfmiddlewaretoken"})
    assert csrf_input is not None

    time_token = form.find("input", attrs={"name": "_time_token"})
    assert time_token is not None

    form_type = form.find("input", attrs={"name": "form_type"})
    assert form_type is not None
    assert form_type.get("value") == "contact"

    honeypot = form.find("input", attrs={"name": "company"})
    assert honeypot is not None
    assert honeypot.get("tabindex") == "-1"

    submit = form.find("button", attrs={"type": "submit"})
    assert submit is not None
    submit_classes = _get_classes(submit)
    assert "btn-primary" in submit_classes
    assert "btn-submit" in submit_classes


@pytest.mark.django_db
def test_theme_a_contact_form_floating_labels():
    block = ContactFormBlock()
    block_value = {
        "heading": "Contact",
    }

    html = block.render(block_value)
    soup = BeautifulSoup(html, "html.parser")

    peer_inputs = soup.select("input.peer")
    peer_textareas = soup.select("textarea.peer")
    assert len(peer_inputs) >= 3
    assert len(peer_textareas) == 1

    name_label = soup.find("label", attrs={"for": "contact-name"})
    email_label = soup.find("label", attrs={"for": "contact-email"})
    phone_label = soup.find("label", attrs={"for": "contact-phone"})
    message_label = soup.find("label", attrs={"for": "contact-message"})
    assert name_label is not None
    assert email_label is not None
    assert phone_label is not None
    assert message_label is not None
