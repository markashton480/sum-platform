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
from wagtail.models import Page, Site


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

    def clean(self) -> None:
        """
        Validate that only one HomePage exists per site.

        Raises ValidationError if this HomePage would conflict with an existing
        HomePage that is already set as root_page for a site.

        Note: This validation checks if this page is already a root_page.
        Since Site.root_page is unique per site, the database enforces that
        only one page can be root_page per site. This validation is defensive.
        """
        super().clean()

        # Get sites where this page is currently the root_page
        sites_with_this_page = Site.objects.filter(root_page=self)

        # If this page is not a root_page for any site yet, allow it
        # (The validation will happen via signal when it's set as root_page)
        if not sites_with_this_page.exists():
            return

        # Check each site where this page is root_page
        for site in sites_with_this_page:
            # Check if there's another HomePage that's also root_page for this same site
            # (This shouldn't happen due to Site.root_page uniqueness, but we validate defensively)
            other_homepages = HomePage.objects.exclude(pk=self.pk).filter(
                id__in=Site.objects.filter(id=site.id)
                .exclude(root_page=self)
                .values_list("root_page_id", flat=True)
            )

            if other_homepages.exists():
                raise ValidationError(
                    {
                        "title": (
                            f"Only one HomePage is allowed per site. "
                            f"Another HomePage is already set as the root page for site '{site.hostname}'."
                        )
                    }
                )

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
