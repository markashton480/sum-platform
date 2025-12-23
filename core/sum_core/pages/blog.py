"""
Name: Blog Page Models
Path: core/sum_core/pages/blog.py
Purpose: BlogIndexPage and BlogPostPage models for blog content organization.
Family: SUM Platform – Page Types
Dependencies: Wagtail Page model, sum_core.blocks.base.PageStreamBlock
"""

from __future__ import annotations

from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from sum_core.blocks.base import PageStreamBlock
from sum_core.pages.mixins import BreadcrumbMixin, OpenGraphMixin, SeoFieldsMixin
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page


class BlogIndexPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Landing page for blog posts that lists child BlogPostPage items.

    Provides an intro StreamField for content above the listing and
    paginates published BlogPostPage instances beneath it.
    """

    intro: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Optional intro content displayed above the blog post listing.",
    )

    paginate_by = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=6,
        help_text="Number of posts to show per page (leave blank for default).",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("paginate_by"),
    ]

    promote_panels = (
        SeoFieldsMixin.seo_panels
        + OpenGraphMixin.open_graph_panels
        + Page.promote_panels
    )

    # NOTE: parent_page_types is intentionally NOT set here.
    # Wagtail's default (inherited from Page) allows ANY parent page type.
    # Client projects should restrict via their HomePage's subpage_types.

    # Only allow BlogPostPage children
    subpage_types: list[str] = ["sum_core_pages.BlogPostPage"]

    # v0.6 rendering contract: themes own page templates under theme/
    template: str = "theme/blog_index_page.html"

    class Meta:
        verbose_name = "Blog Index Page"
        verbose_name_plural = "Blog Index Pages"

    def get_context(self, request, *args, **kwargs):
        """Add paginated, live BlogPostPage children to context."""
        context = super().get_context(request, *args, **kwargs)

        posts = (
            BlogPostPage.objects.child_of(self)
            .live()
            .public()
            .order_by("-date", "-first_published_at")
        )

        paginate_by = self.paginate_by or 6
        paginator = Paginator(posts, paginate_by)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["posts"] = page_obj
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["is_paginated"] = page_obj.has_other_pages()
        return context


class BlogPostPage(SeoFieldsMixin, OpenGraphMixin, BreadcrumbMixin, Page):
    """
    Individual blog article page.

    Contains featured image, excerpt, date, and body content.
    Must be created under BlogIndexPage.
    """

    date = models.DateField(
        default=timezone.now,
        help_text="Publish date shown in blog listings.",
    )

    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Featured image displayed in blog listings and post headers.",
    )

    excerpt = models.TextField(
        blank=True,
        help_text="Short summary shown in blog listings.",
    )

    body: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Main content for the blog post.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("featured_image"),
        FieldPanel("excerpt"),
        FieldPanel("body"),
    ]

    promote_panels = (
        SeoFieldsMixin.seo_panels
        + OpenGraphMixin.open_graph_panels
        + Page.promote_panels
    )

    # BlogPostPage must be created under BlogIndexPage
    parent_page_types: list[str] = ["sum_core_pages.BlogIndexPage"]

    # BlogPostPage is a leaf page - no children allowed
    subpage_types: list[str] = []

    # v0.6 rendering contract: themes own page templates under theme/
    template: str = "theme/blog_post_page.html"

    class Meta:
        verbose_name = "Blog Post Page"
        verbose_name_plural = "Blog Post Pages"
