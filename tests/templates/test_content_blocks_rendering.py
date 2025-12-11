import pytest
from django.test import Client
from home.models import HomePage
from wagtail.models import Site, Page

@pytest.mark.django_db
def test_render_content_blocks():
    """
    Test that the new content blocks render correctly on the HomePage.
    """
    client = Client()

    # 1. Setup Site
    site = Site.objects.filter(is_default_site=True).first()
    if not site:
        root = Page.get_first_root_node()
        if not root:
             # Just in case
             return
        site = Site.objects.create(hostname='localhost', root_page=root, is_default_site=True)

    root = site.root_page

    # 2. Create Page with Blocks

    rich_text_content = """<h2>Rich Heading</h2><p>Rich Paragraph</p>"""

    home = HomePage(
        title="Content Test Page",
        slug="content-test",
        body=[
            ('content', {
                'body': rich_text_content
            }),
            ('quote', {
                'quote': 'This is a quote.',
                'author': 'Author Name',
                'role': 'Role Name'
            }),
            ('buttons', {
                'alignment': 'center',
                'buttons': [
                    {'label': 'Primary Btn', 'url': 'http://example.com/1', 'style': 'primary'},
                    {'label': 'Secondary Btn', 'url': 'http://example.com/2', 'style': 'secondary'},
                ]
            }),
            ('spacer', {'size': 'large'}),
            ('divider', {'style': 'accent'}),
        ]
    )

    root.add_child(instance=home)
    home.save_revision().publish()

    # 3. Request Page
    response = client.get(home.url)
    assert response.status_code == 200
    content = response.content.decode('utf-8')

    # 4. Verify HTML Output (Tokens & Classes)

    # Rich Text
    assert 'content-block--rich-text' in content
    assert 'rich-text' in content
    assert 'Rich Heading' in content

    # Quote
    assert 'quote-block' in content
    assert 'This is a quote.' in content
    assert 'Author Name' in content
    assert 'quote-line' in content

    # Buttons
    assert 'button-group--center' in content
    assert 'btn-primary' in content
    assert 'btn-secondary' in content
    assert 'Primary Btn' in content

    # Spacer
    assert 'content-spacer--large' in content

    # Divider
    assert 'content-divider--accent' in content
