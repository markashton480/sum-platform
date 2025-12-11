"""
Name: Standard Page Model
Path: core/sum_core/pages/standard.py
Purpose: A reusable general-purpose content page using StreamField with PageStreamBlock.
Family: SUM Platform – Page Types
Dependencies: Wagtail Page model, sum_core.blocks.base.PageStreamBlock
"""
from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page

from sum_core.blocks.base import PageStreamBlock


class StandardPage(Page):
    """
    General-purpose content page for About, FAQ, Terms, Service Overview, etc.

    Uses the same PageStreamBlock as HomePage, allowing editors to compose pages
    from the full set of available blocks (hero, trust strip, testimonials,
    services, content blocks, etc.) without developer involvement.
    """

    body: StreamField = StreamField(
        PageStreamBlock(),
        blank=True,
        null=True,
        use_json_field=True,
        help_text="Add content blocks to build your page layout.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    # Allow StandardPage to be created under any Page type for flexibility
    # In real client sites, this can be overridden to limit to specific parents
    parent_page_types: list[str] = ["wagtailcore.Page", "home.HomePage"]

    # StandardPage is a leaf content page - no child pages allowed
    subpage_types: list[str] = []

    template: str = "sum_core/standard_page.html"

    class Meta:
        verbose_name = "Standard Page"
        verbose_name_plural = "Standard Pages"

    @property
    def has_hero_block(self) -> bool:
        """Check if the StreamField body contains any hero blocks."""
        if not self.body:
            return False

        hero_block_types = ["hero_image", "hero_gradient", "hero"]

        for block in self.body:
            if block.block_type in hero_block_types:
                return True
        return False

