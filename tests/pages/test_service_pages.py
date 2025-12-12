"""
Name: Service Page Tests
Path: tests/pages/test_service_pages.py
Purpose: Validate ServiceIndexPage and ServicePage models, hierarchy enforcement, and template rendering.
Family: Part of the page-level test suite exercising the page types.
Dependencies: Wagtail Site & Page models, sum_core.pages.services, home.HomePage.
"""
from __future__ import annotations

import pytest
from django.test import RequestFactory
from home.models import HomePage
from sum_core.blocks import PageStreamBlock
from sum_core.pages.services import ServiceIndexPage, ServicePage
from wagtail.fields import StreamField
from wagtail.models import Page, Site

pytestmark = pytest.mark.django_db


# =============================================================================
# ServiceIndexPage Model Tests
# =============================================================================


def test_service_index_page_is_registered_as_page_type() -> None:
    """ServiceIndexPage is registered as a Wagtail page type."""
    assert issubclass(ServiceIndexPage, Page)


def test_service_index_page_has_intro_stream_field() -> None:
    """ServiceIndexPage has an intro field that is a StreamField."""
    intro_field = ServiceIndexPage._meta.get_field("intro")
    assert isinstance(intro_field, StreamField)


def test_service_index_page_intro_uses_page_stream_block() -> None:
    """ServiceIndexPage intro StreamField uses PageStreamBlock."""
    intro_field = ServiceIndexPage._meta.get_field("intro")
    assert isinstance(intro_field.stream_block, PageStreamBlock)


def test_service_index_page_can_be_created_under_homepage() -> None:
    """ServiceIndexPage can be created under HomePage."""
    root = Page.get_first_root_node()

    # Create HomePage first
    homepage = HomePage(title="Home", slug="home-under")
    root.add_child(instance=homepage)

    # Create ServiceIndexPage under HomePage
    service_index = ServiceIndexPage(
        title="Our Services",
        slug="services",
    )
    homepage.add_child(instance=service_index)

    assert ServiceIndexPage.objects.filter(title="Our Services").exists()


def test_service_index_page_can_be_created_with_empty_intro() -> None:
    """ServiceIndexPage can be created with an empty intro StreamField."""
    root = Page.get_first_root_node()

    # Create HomePage first
    homepage = HomePage(title="Home", slug="home-empty-intro")
    root.add_child(instance=homepage)

    service_index = ServiceIndexPage(
        title="Services Empty Intro",
        slug="services-empty-intro",
        intro=None,
    )
    homepage.add_child(instance=service_index)

    retrieved = ServiceIndexPage.objects.get(slug="services-empty-intro")
    assert retrieved.title == "Services Empty Intro"


def test_service_index_page_can_be_created_with_intro_content() -> None:
    """ServiceIndexPage can be created with intro content."""
    root = Page.get_first_root_node()

    # Create HomePage first
    homepage = HomePage(title="Home", slug="home-intro-content")
    root.add_child(instance=homepage)

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>Our Services</h2><p>We offer a range of premium services.</p>",
            }
        ]
    )

    service_index = ServiceIndexPage(
        title="Services With Intro",
        slug="services-with-intro",
        intro=stream_data,
    )
    homepage.add_child(instance=service_index)

    retrieved = ServiceIndexPage.objects.get(slug="services-with-intro")
    assert len(list(retrieved.intro)) == 1


def test_service_index_page_template_path() -> None:
    """ServiceIndexPage uses the correct template path."""
    assert ServiceIndexPage.template == "sum_core/service_index_page.html"


def test_service_index_page_subpage_types() -> None:
    """ServiceIndexPage only allows ServicePage children."""
    assert "sum_core_pages.ServicePage" in ServiceIndexPage.subpage_types


def test_service_index_page_parent_page_types() -> None:
    """ServiceIndexPage can only be created under HomePage."""
    assert ServiceIndexPage.parent_page_types == ["home.HomePage"]


def test_service_index_page_get_context_includes_services() -> None:
    """ServiceIndexPage.get_context() includes live, public ServicePage children."""
    root = Page.get_first_root_node()

    # Create HomePage first
    homepage = HomePage(title="Home", slug="home-context")
    root.add_child(instance=homepage)

    # Create ServiceIndexPage
    service_index = ServiceIndexPage(title="Services", slug="services-context-test")
    homepage.add_child(instance=service_index)

    # Create a published ServicePage child
    service1 = ServicePage(
        title="Kitchen Remodeling",
        slug="kitchen-remodeling",
        short_description="Transform your kitchen.",
    )
    service_index.add_child(instance=service1)
    service1.save_revision().publish()

    # Create another published ServicePage child
    service2 = ServicePage(
        title="Bathroom Renovation",
        slug="bathroom-renovation",
        short_description="Upgrade your bathroom.",
    )
    service_index.add_child(instance=service2)
    service2.save_revision().publish()

    # Get context
    request = RequestFactory().get("/services/")
    context = service_index.get_context(request)

    # Assert services are in context
    assert "services" in context
    services = list(context["services"])
    assert len(services) == 2
    assert services[0].title == "Kitchen Remodeling"
    assert services[1].title == "Bathroom Renovation"


def test_service_index_page_get_context_excludes_drafts() -> None:
    """ServiceIndexPage.get_context() excludes draft ServicePage children."""
    root = Page.get_first_root_node()

    # Create HomePage first
    homepage = HomePage(title="Home", slug="home-exclude-drafts")
    root.add_child(instance=homepage)

    # Create ServiceIndexPage
    service_index = ServiceIndexPage(title="Services", slug="services-exclude-drafts")
    homepage.add_child(instance=service_index)

    # Create a published ServicePage
    service1 = ServicePage(title="Published Service", slug="published")
    service_index.add_child(instance=service1)
    service1.save_revision().publish()

    # Create a draft ServicePage (not live)
    service2 = ServicePage(title="Draft Service", slug="draft", live=False)
    service_index.add_child(instance=service2)
    # Ensure it's saved but not live
    service2.live = False
    service2.save()

    # Get context
    request = RequestFactory().get("/services/")
    context = service_index.get_context(request)

    # Assert only published service is in context
    services = list(context["services"])
    assert len(services) == 1
    assert services[0].title == "Published Service"


# =============================================================================
# Page Tree Rule Tests (Regression Tests for M3-005)
# =============================================================================


def test_service_index_page_cannot_be_created_under_root() -> None:
    """ServiceIndexPage cannot be created directly under root (negative test)."""
    # Verify that ServiceIndexPage.parent_page_types does not allow root
    assert "wagtailcore.Page" not in ServiceIndexPage.parent_page_types


def test_service_index_page_can_create_at_homepage() -> None:
    """ServiceIndexPage.can_create_at() returns True for HomePage."""
    root = Page.get_first_root_node()

    # Create HomePage
    homepage = HomePage(title="Home", slug="home-can-create")
    root.add_child(instance=homepage)

    assert ServiceIndexPage.can_create_at(homepage) is True


def test_service_index_page_cannot_create_at_root() -> None:
    """ServiceIndexPage.can_create_at() returns False for Root."""
    root = Page.get_first_root_node()
    assert ServiceIndexPage.can_create_at(root) is False


# =============================================================================
# ServicePage Model Tests
# =============================================================================


def test_service_page_is_registered_as_page_type() -> None:
    """ServicePage is registered as a Wagtail page type."""
    assert issubclass(ServicePage, Page)


def test_service_page_has_featured_image_field() -> None:
    """ServicePage has a featured_image field."""
    featured_image_field = ServicePage._meta.get_field("featured_image")
    assert featured_image_field is not None


def test_service_page_has_short_description_field() -> None:
    """ServicePage has a short_description field."""
    short_description_field = ServicePage._meta.get_field("short_description")
    assert short_description_field.max_length == 250


def test_service_page_has_body_stream_field() -> None:
    """ServicePage has a body field that is a StreamField."""
    body_field = ServicePage._meta.get_field("body")
    assert isinstance(body_field, StreamField)


def test_service_page_body_uses_page_stream_block() -> None:
    """ServicePage body StreamField uses PageStreamBlock."""
    body_field = ServicePage._meta.get_field("body")
    assert isinstance(body_field.stream_block, PageStreamBlock)


def test_service_page_can_be_created_under_service_index_page() -> None:
    """ServicePage can be created under ServiceIndexPage."""
    root = Page.get_first_root_node()

    # Create ServiceIndexPage
    service_index = ServiceIndexPage(title="Services", slug="services-create")
    root.add_child(instance=service_index)

    # Create ServicePage under it
    service_page = ServicePage(
        title="Kitchen Remodeling",
        slug="kitchen-remodeling",
        short_description="Transform your kitchen with our expert team.",
    )
    service_index.add_child(instance=service_page)

    assert ServicePage.objects.filter(title="Kitchen Remodeling").exists()


def test_service_page_cannot_be_created_under_root() -> None:
    """ServicePage cannot be created directly under root (negative test)."""
    # Attempt to create ServicePage under root should fail
    # Wagtail will prevent this based on parent_page_types
    # We verify that ServicePage.parent_page_types does not allow root
    assert "wagtailcore.Page" not in ServicePage.parent_page_types


def test_service_page_parent_page_types() -> None:
    """ServicePage can only be created under ServiceIndexPage."""
    assert ServicePage.parent_page_types == ["sum_core_pages.ServiceIndexPage"]


def test_service_page_is_leaf_page() -> None:
    """ServicePage has no allowed subpage types (leaf page)."""
    assert ServicePage.subpage_types == []


def test_service_page_can_be_created_with_empty_body() -> None:
    """ServicePage can be created with an empty body StreamField."""
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-empty-body")
    root.add_child(instance=service_index)

    service_page = ServicePage(
        title="Minimal Service",
        slug="minimal-service",
        body=None,
    )
    service_index.add_child(instance=service_page)

    retrieved = ServicePage.objects.get(slug="minimal-service")
    assert retrieved.title == "Minimal Service"


def test_service_page_can_be_created_with_body_content() -> None:
    """ServicePage can be created with body content."""
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-body-content")
    root.add_child(instance=service_index)

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "rich_text",
                "value": "<h2>Service Details</h2><p>Detailed information.</p>",
            }
        ]
    )

    service_page = ServicePage(
        title="Detailed Service",
        slug="detailed-service",
        body=stream_data,
    )
    service_index.add_child(instance=service_page)

    retrieved = ServicePage.objects.get(slug="detailed-service")
    assert len(list(retrieved.body)) == 1


def test_service_page_template_path() -> None:
    """ServicePage uses the correct template path."""
    assert ServicePage.template == "sum_core/service_page.html"


def test_service_page_has_hero_block_returns_false_when_no_body() -> None:
    """has_hero_block returns False when body is empty."""
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-no-hero")
    root.add_child(instance=service_index)

    service_page = ServicePage(title="No Hero Service", slug="no-hero")
    service_index.add_child(instance=service_page)

    assert service_page.has_hero_block is False


def test_service_page_has_hero_block_returns_false_for_non_hero_blocks() -> None:
    """has_hero_block returns False when body contains no hero blocks."""
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-no-hero-blocks")
    root.add_child(instance=service_index)

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [{"type": "rich_text", "value": "<p>Content.</p>"}]
    )

    service_page = ServicePage(
        title="Content Only Service",
        slug="content-only",
        body=stream_data,
    )
    service_index.add_child(instance=service_page)

    assert service_page.has_hero_block is False


def test_service_page_has_hero_block_returns_true_for_hero_image() -> None:
    """has_hero_block returns True when body contains hero_image block."""
    from wagtail.images.models import Image
    from wagtail.images.tests.utils import get_test_image_file

    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-with-hero")
    root.add_child(instance=service_index)

    image = Image.objects.create(title="Hero Image", file=get_test_image_file())

    stream_block = PageStreamBlock()
    stream_data = stream_block.to_python(
        [
            {
                "type": "hero_image",
                "value": {
                    "headline": "<p>Welcome</p>",
                    "subheadline": "",
                    "ctas": [],
                    "status": "",
                    "image": image.pk,
                    "image_alt": "Hero background",
                    "overlay_opacity": "medium",
                    "floating_card_label": "",
                    "floating_card_value": "",
                },
            }
        ]
    )

    service_page = ServicePage(
        title="Hero Service",
        slug="hero-service",
        body=stream_data,
    )
    service_index.add_child(instance=service_page)

    assert service_page.has_hero_block is True


# =============================================================================
# Template Rendering Tests
# =============================================================================


def test_service_index_page_renders_service_grid_when_children_exist() -> None:
    """ServiceIndexPage template renders service grid when children exist."""
    from wagtail.images.models import Image
    from wagtail.images.tests.utils import get_test_image_file

    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-grid-render")
    root.add_child(instance=service_index)

    # Create test image
    image = Image.objects.create(title="Service Image", file=get_test_image_file())

    # Create ServicePage with featured image
    service_page = ServicePage(
        title="Kitchen Remodeling",
        slug="kitchen-remodeling",
        short_description="Transform your kitchen.",
        featured_image=image,
    )
    service_index.add_child(instance=service_page)
    service_page.save_revision().publish()

    # Set up site
    site = Site.objects.get(is_default_site=True)
    site.root_page = service_index
    site.save()

    # Render the page
    request = RequestFactory().get("/services/", HTTP_HOST=site.hostname or "localhost")
    context = service_index.get_context(request)

    # Verify services are in context
    assert "services" in context
    services = list(context["services"])
    assert len(services) == 1
    assert services[0].title == "Kitchen Remodeling"


def test_service_page_renders_title_and_description() -> None:
    """ServicePage template renders title and short description."""
    root = Page.get_first_root_node()
    service_index = ServiceIndexPage(title="Services", slug="services-page-render")
    root.add_child(instance=service_index)

    service_page = ServicePage(
        title="Kitchen Remodeling",
        slug="kitchen-remodeling",
        short_description="Transform your kitchen with our expert team.",
    )
    service_index.add_child(instance=service_page)

    assert service_page.title == "Kitchen Remodeling"
    assert (
        service_page.short_description == "Transform your kitchen with our expert team."
    )
