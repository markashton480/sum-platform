import pytest
from django import forms
from sum_core.blocks.forms import ContactFormBlock, QuoteRequestFormBlock


class DummyContactForm(forms.Form):
    website = forms.CharField(required=False)  # Honeypot
    name = forms.CharField(label="Your Name")
    email = forms.EmailField(label="Email Address")


class DummyQuoteForm(forms.Form):
    company = forms.CharField(required=False)  # Honeypot
    postcode = forms.CharField(label="Postcode")
    budget = forms.ChoiceField(choices=[("10k", "10k"), ("20k", "20k")])


@pytest.mark.django_db
def test_contact_form_rendering():
    block = ContactFormBlock()
    value = block.to_python(
        {"heading": "Contact Us", "intro": "Get in touch.", "submit_label": "Send It"}
    )

    # Use plain dict for context, let Wagtail handle it
    context = {"form": DummyContactForm()}

    # Render using the block's template directly or render the block instance
    rendered = block.render(value, context=context)

    assert "Contact Us" in rendered
    assert "Get in touch" in rendered
    assert "Send It" in rendered
    assert 'data-form-type="contact"' in rendered
    assert 'class="contact-form-block' in rendered
    assert "bg-sage-black" in rendered
    assert 'name="company"' in rendered  # Honeypot
    assert "sr-only" in rendered
    assert "Your Name" in rendered
    assert "Email Address" in rendered


@pytest.mark.django_db
def test_quote_request_form_rendering():
    block = QuoteRequestFormBlock()
    value = block.to_python(
        {
            "heading": "Get a Quote",
            "submit_label": "Request Quote",
            "show_compact_meta": True,
        }
    )

    context = {"form": DummyQuoteForm()}

    rendered = block.render(value, context=context)

    assert "Get a Quote" in rendered
    assert "Request Quote" in rendered
    assert "section bg-sage-oat" in rendered
    assert 'data-form-type="quote_request"' in rendered
    assert 'name="company"' in rendered  # Honeypot
    assert "Postcode" in rendered
