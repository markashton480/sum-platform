"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from sum_core.blocks import PageStreamBlock


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
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

    template: str = "sum_core/home_page.html"

    @property
    def has_hero_block(self):
        """Check if the StreamField body contains any hero blocks."""
        if not self.body:
            return False

        # Check against the block names defined in PageStreamBlock
        hero_block_types = ["hero_image", "hero_gradient"]

        # StreamField iteration yields blocks that behave like bound blocks
        for block in self.body:
             if block.block_type in hero_block_types:
                 return True
        return False
