"""
Name: Base Block Definitions
Path: core/sum_core/blocks/base.py
Purpose: Core block infrastructure and canonical page StreamField definition for sum_core.
Family: Imported by page models and block implementations across sum_core.
Dependencies: Wagtail blocks, rich text utilities.
"""

from wagtail import blocks
from wagtail.blocks import StreamBlock

from sum_core.blocks.content import (
    HeroBlock,
    TrustStripBlock,
    FeaturesListBlock,
    ComparisonBlock,
    PortfolioBlock,
    RichTextContentBlock,
    EditorialHeaderBlock,
    QuoteBlock,
    ImageBlock,
    ButtonGroupBlock,
    SpacerBlock,
    DividerBlock,
)
from sum_core.blocks.hero import HeroImageBlock, HeroGradientBlock
from sum_core.blocks.services import ServiceCardsBlock
from sum_core.blocks.testimonials import TestimonialsBlock
from sum_core.blocks.gallery import GalleryBlock
from sum_core.blocks.trust import (
    TrustStripBlock as TrustStripLogosBlock,
    StatsBlock,
)
from sum_core.blocks.process_faq import ProcessStepsBlock, FAQBlock


class PageStreamBlock(StreamBlock):
    """
    Canonical StreamBlock for page content fields.

    This block defines the available content blocks that can be used in page
    body fields. It serves as the foundation for building pages through the
    Wagtail admin interface.
    """

    hero_image = HeroImageBlock(group="Hero")
    hero_gradient = HeroGradientBlock(group="Hero")
    service_cards = ServiceCardsBlock(group="Services")
    testimonials = TestimonialsBlock(group="Sections")
    gallery = GalleryBlock(group="Sections")
    hero = HeroBlock(group="Legacy Sections")  # Keeping specific hero type separate
    trust_strip = TrustStripBlock(group="Sections")
    trust_strip_logos = TrustStripLogosBlock(group="Sections")
    stats = StatsBlock(group="Sections")
    process = ProcessStepsBlock(group="Sections")
    faq = FAQBlock(group="Sections")
    features = FeaturesListBlock(group="Sections")
    comparison = ComparisonBlock(group="Sections")
    portfolio = PortfolioBlock(group="Sections")

    # Content Blocks
    editorial_header = EditorialHeaderBlock(group="Content")
    content = RichTextContentBlock(group="Content")
    quote = QuoteBlock(group="Content")
    image_block = ImageBlock(group="Content")
    buttons = ButtonGroupBlock(group="Content")
    spacer = SpacerBlock(group="Content")
    divider = DividerBlock(group="Content")

    rich_text = blocks.RichTextBlock(
        label="Rich Text",
        help_text="Add formatted text content. Use H2-H4 for headings, avoid H1.",
        features=[
            "h2", "h3", "h4",  # Headings H2-H4 only, no H1
            "bold", "italic",   # Text formatting
            "link",             # Links
            "ol", "ul",         # Ordered and unordered lists
        ],
        required=False,
    )

    class Meta:
        """Meta configuration for PageStreamBlock."""
        icon = "doc-full"
        label = "Content Block"
        label_format = "Content: {label}"
        template = "sum_core/blocks/rich_text.html"  # Default template for rendering

