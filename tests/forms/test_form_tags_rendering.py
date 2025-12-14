import pytest
from django.template import Context, Template
from django.test import RequestFactory


@pytest.mark.django_db
def test_form_hidden_fields_renders_token():
    factory = RequestFactory()
    request = factory.get("/")

    template = Template(
        "{% load form_tags %}" "{% form_hidden_fields form_type='contact' %}"
    )
    context = Context({"request": request})
    rendered = template.render(context)

    assert 'name="_time_token"' in rendered
    assert 'name="form_type"' in rendered
    assert 'value="contact"' in rendered
    assert 'name="page_url"' in rendered


@pytest.mark.django_db
def test_form_hidden_fields_valid_token():
    factory = RequestFactory()
    request = factory.get("/")

    template = Template("{% load form_tags %}" "{% form_hidden_fields %}")
    context = Context({"request": request})
    rendered = template.render(context)

    # Extract token value
    import re

    match = re.search(r'name="_time_token" value="([^"]+)"', rendered)
    assert match
    token = match.group(1)

    # Verify token format
    assert ":" in token
    timestamp, signature = token.split(":")
    assert timestamp.isdigit()
    assert len(signature) > 0
