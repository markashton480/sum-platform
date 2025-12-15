"""
Name: Smoke Consumer Home Models
Path: clients/_smoke_consumer/smoke_consumer/home/models.py
Purpose: Minimal HomePage model for smoke testing Wagtail integration.
Family: Validation/proof project for sum_core consumability.
Dependencies: Wagtail, sum_core.pages.mixins
"""

from __future__ import annotations

from sum_core.pages.mixins import BreadcrumbMixin, OpenGraphMixin, SeoFieldsMixin
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Minimal home page for the smoke consumer project.

    Demonstrates that client projects can use sum_core mixins
    without any test_project dependencies.
    """

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    promote_panels = (
        SeoFieldsMixin.seo_panels
        + OpenGraphMixin.open_graph_panels
        + Page.promote_panels
    )

    # Only allow one HomePage at root
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["sum_core_pages.StandardPage", "sum_core_pages.ServiceIndexPage"]

    class Meta:
        verbose_name = "Home Page"
