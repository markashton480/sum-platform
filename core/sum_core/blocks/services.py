"""
Name: Service Blocks
Path: core/sum_core/blocks/services.py
Purpose: StreamField blocks for service card grids
Family: Used by PageStreamBlock and core page models (HomePage, ServicePage, etc.)
Dependencies: Wagtail blocks, wagtailimages, sum_core.blocks.base, design system CSS
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

class ServiceCardItemBlock(blocks.StructBlock):
    """
    A single service card within the ServiceCardsBlock grid.
    """
    icon = blocks.CharBlock(
        required=False, 
        max_length=4, 
        help_text="Emoji or short icon text (optional)"
    )
    image = ImageChooserBlock(
        required=False,
        help_text="Allows proper image/icon; render as the primary visual if present."
    )
    title = blocks.CharBlock(
        required=True, 
        max_length=120
    )
    description = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic', 'link', 'ul', 'ol', 'document-link'],
        help_text="Limited to paragraphs + basic inline formatting."
    )
    link_url = blocks.URLBlock(
        required=False
    )
    link_label = blocks.CharBlock(
        required=False, 
        max_length=50, 
        help_text="Defaults to “Learn more” if left blank."
    )

    class Meta:
        icon = "doc-full"
        label = "Service Card"


class ServiceCardsBlock(blocks.StructBlock):
    """
    A section containing a grid of ServiceCardItemBlocks.
    """
    eyebrow = blocks.CharBlock(
        required=False, 
        max_length=120, 
        help_text="Short label above the heading (optional)."
    )
    heading = blocks.RichTextBlock(
        required=True, 
        features=['italic', 'bold'],
        help_text="Section heading. Use Italic for accent color."
    )
    intro = blocks.TextBlock(
        required=False, 
        help_text="Short supporting paragraph."
    )
    cards = blocks.ListBlock(
        ServiceCardItemBlock(), 
        min_num=1, 
        max_num=12
    )
    layout_style = blocks.ChoiceBlock(
        choices=[
            ("default", "Default"), 
            ("tight", "Tight spacing")
        ], 
        default="default", 
        required=False
    )

    class Meta:
        template = "sum_core/blocks/service_cards.html"
        icon = "list-ul"
        label = "Service cards"
        help_text = "Showcase services in a responsive card grid (1–12 cards)."
