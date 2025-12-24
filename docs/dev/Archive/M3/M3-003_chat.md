# M3-003 requirements and implementation
_Exported on 12/12/2025 at 13:38:37 GMT from Cursor (2.1.50)_

---

**User**

Please review the requirements in @docs/dev/M3/M3-003.md and carefully implement.

---

**Cursor**

Got it. I’ll (1) inspect the current `HomePage` model + existing tests, (2) implement **root-only creation** via `can_create_at` (or Wagtail equivalent already used here) and **true single-homepage enforcement** in `clean()`, then (3) add the two negative tests and run the test suite to confirm everything passes.

Nice — `HomePage` already has a `clean()` override, but it’s currently relying on `Site.root_page` logic (which doesn’t truly enforce “only one HomePage exists”). Next I’ll inspect the existing homepage tests and then swap `clean()` to the explicit queryset check + add the root-only `can_create_at` enforcement.

Aha: tests already cover a “clean() doesn’t raise” case, but nothing yet asserts the **two new negative guarantees** (non-root creation denied, second HomePage forbidden). Next I’ll find any existing `can_create_at` patterns in this repo, then implement the model change + update/extend tests accordingly.

I’ve found there aren’t any existing `can_create_at` implementations elsewhere in this repo, so we’ll define it directly on `HomePage` using Wagtail’s standard hook: **allow creation only when `parent.is_root()`**. Next I’ll update `HomePage.clean()` to the explicit “any other HomePage exists” constraint, then extend `tests/pages/test_home_page.py` with the two negative tests from the spec.

```python
"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a HomePage type with StreamField body, SEO fields, and one-per-site enforcement.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core.pages.mixins, sum_core.blocks.base.PageStreamBlock, sum_core base template.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError
from sum_core.blocks import PageStreamBlock
from sum_core.pages.mixins import BreadcrumbMixin, OpenGraphMixin, SeoFieldsMixin
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


class HomePage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Homepage for the test project with StreamField body, SEO fields, and one-per-site enforcement.

    Satisfies US-P01 Homepage acceptance criteria:
    - StreamField body accepting all homepage blocks (PageStreamBlock)
    - SEO fields (meta title, meta description) via SeoFieldsMixin
    - Open Graph image via OpenGraphMixin
    - Only one HomePage allowed per site (enforced via clean method)
    """

    intro: RichTextField = RichTextField(blank=True)
    body: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add content blocks to build your homepage layout.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    promote_panels = (
        SeoFieldsMixin.seo_panels
        + OpenGraphMixin.open_graph_panels
        + Page.promote_panels
    )

    # HomePage can only be created under the root page
    parent_page_types: list[str] = ["wagtailcore.Page"]

    # HomePage can have child pages (e.g., StandardPage)
    subpage_types: list[str] = ["wagtailcore.Page"]

    template: str = "sum_core/home_page.html"

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"

    @classmethod
    def can_create_at(cls, parent: Page) -> bool:
        """
        Enforce root-only creation for HomePage.

        This is used by Wagtail admin UI, but also helps prevent programmatic
        misuse when callers respect the standard Wagtail create APIs.
        """
        return parent.is_root() and super().can_create_at(parent)

    def clean(self) -> None:
        """
        Validate that only one HomePage exists.

        This rule is enforced at the model layer so programmatic creation can't
        bypass it.
        """
        super().clean()

        if HomePage.objects.exclude(pk=self.pk).exists():
            raise ValidationError({"title": "Only one HomePage is allowed per site."})

    @property
    def has_hero_block(self) -> bool:
        """Check if the StreamField body contains any hero blocks."""
        if not self.body:
            return False

        # Check against the block names defined in PageStreamBlock
        hero_block_types = ["hero_image", "hero_gradient", "hero"]

        # StreamField iteration yields blocks that behave like bound blocks
        for block in self.body:
            if block.block_type in hero_block_types:
                return True
        return False

```

```python
"""
Name: Home Page Tests
Path: tests/pages/test_home_page.py
Purpose: Validate the test project's HomePage type and its integration with the SUM base template.
Family: Part of the page-level test suite exercising the design system.
Dependencies: Wagtail Site & Page models, home.HomePage, sum_core templates.
"""
from __future__ import annotations

import pytest
from django.core.exceptions import ValidationError
from django.template import RequestContext, Template
from django.test import RequestFactory
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


def test_home_page_can_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    assert HomePage.objects.filter(title="Test Home").exists()


def test_home_page_can_only_be_created_under_root() -> None:
    root = Page.get_first_root_node()
    non_root_parent = Page(title="Non-root Parent", slug="non-root-parent")
    root.add_child(instance=non_root_parent)

    assert HomePage.can_create_at(root) is True
    assert HomePage.can_create_at(non_root_parent) is False


def test_home_page_cannot_create_second_homepage() -> None:
    root = Page.get_first_root_node()

    first = HomePage(title="Home 1", slug="home-1")
    root.add_child(instance=first)

    second = HomePage(title="Home 2", slug="home-2")
    with pytest.raises(ValidationError) as excinfo:
        root.add_child(instance=second)

    assert "Only one HomePage is allowed" in str(excinfo.value)


def test_home_page_template_uses_sum_core_base() -> None:
    root = Page.get_first_root_node()
    homepage = HomePage(title="Test Home", slug="test-home-template")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template(
        "{% extends 'sum_core/home_page.html' %}"
        "{% block content %}<p>Content</p>{% endblock %}"
    )
    rendered = template.render(RequestContext(request, {"page": homepage}))

    assert "sum_core/css/main.css" in rendered
    assert "<header" in rendered
    assert "<footer" in rendered


def test_home_page_renders_streamfield_content() -> None:
    """Test that HomePage renders StreamField content below the hero section."""
    root = Page.get_first_root_node()

    # Create a PageStreamBlock with rich text content
    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>Test Heading</h2><p>This is test content with <strong>bold</strong> text.</p>",
            }
        ]
    )

    homepage = HomePage(
        title="Test Home with Content", slug="test-home-content", body=stream_data
    )
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template("{% extends 'sum_core/home_page.html' %}")
    rendered = template.render(RequestContext(request, {"page": homepage}))

    # Check that the page renders without errors
    assert rendered is not None

    # Check that StreamField content appears in the rendered output
    assert "Test Heading" in rendered
    assert "This is test content" in rendered
    assert "<strong>bold</strong>" in rendered

    # Check that the content is wrapped in the expected block structure
    # assert "section" in rendered  # RichText block might not have wrapper currently
    # assert "container" in rendered
    # assert "text-body" in rendered


def test_home_page_renders_service_cards() -> None:
    """Test that HomePage renders ServiceCardsBlock content."""
    root = Page.get_first_root_node()

    # Create a PageStreamBlock with service cards
    stream_block = PageStreamBlock()

    # Minimal valid data for service_cards
    service_card_data = {
        "eyebrow": "Our Services",
        "heading": "Comprehensive Solutions",
        "intro": "We do everything.",
        "cards": [
            {
                "title": "Service 1",
                "description": "Description 1",
                "link_url": "https://example.com/1",
                "link_label": "Go to 1",
            },
            {
                "title": "Service 2",
                "description": "Description 2",
            },
            {
                "title": "Service 3",
                "description": "Description 3",
            },
        ],
        "layout_style": "default",
    }

    stream_data = stream_block.to_python(
        [
            {
                "type": "service_cards",
                "value": service_card_data,
            }
        ]
    )

    homepage = HomePage(
        title="Test Home with Services", slug="test-home-services", body=stream_data
    )
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    request = RequestFactory().get("/", HTTP_HOST=site.hostname or "localhost")
    template = Template("{% extends 'sum_core/home_page.html' %}")
    rendered = template.render(RequestContext(request, {"page": homepage}))

    # Check content
    assert "Comprehensive Solutions" in rendered
    assert "Our Services" in rendered
    assert "Service 1" in rendered
    assert "services__grid" in rendered
    assert "services__card" in rendered
    assert "btn--link" in rendered


def test_home_page_clean_validates_when_root_page() -> None:
    """Test that HomePage.clean() validates correctly when it's a root_page."""
    root = Page.get_first_root_node()

    # Create HomePage and set it as root_page
    homepage = HomePage(title="Root Home", slug="root-home")
    root.add_child(instance=homepage)

    site = Site.objects.get(is_default_site=True)
    site.root_page = homepage
    site.save()

    # Refresh and validate - should not raise
    homepage.refresh_from_db()
    homepage.clean()  # Should not raise ValidationError

    # Verify it's the root_page
    assert Site.objects.get(is_default_site=True).root_page == homepage


def test_home_page_has_seo_fields() -> None:
    """Test that HomePage has SEO fields from mixins."""
    root = Page.get_first_root_node()
    homepage = HomePage(
        title="SEO Test Home",
        slug="seo-test-home",
        meta_title="Custom Meta Title",
        meta_description="Custom meta description for testing.",
    )
    root.add_child(instance=homepage)

    assert homepage.meta_title == "Custom Meta Title"
    assert homepage.meta_description == "Custom meta description for testing."


def test_home_page_has_promote_panels() -> None:
    """Test that HomePage has promote_panels with SEO/OG fields."""
    # Verify promote_panels attribute exists and includes SEO/OG panels
    assert hasattr(HomePage, "promote_panels"), "HomePage should have promote_panels"
    assert len(HomePage.promote_panels) > 0, "promote_panels should not be empty"

    # Check that SEO fields are accessible
    root = Page.get_first_root_node()
    homepage = HomePage(
        title="Promote Test",
        slug="promote-test",
        meta_title="Test Meta Title",
        meta_description="Test description",
    )
    root.add_child(instance=homepage)

    assert homepage.meta_title == "Test Meta Title"
    assert homepage.meta_description == "Test description"

```

Good — model enforcement is now in place, and tests now explicitly cover the two new guarantees: **root-only creation** and **rejecting a second HomePage**. Next I’ll run lints for the touched files and execute the test suite to confirm everything passes end-to-end.
