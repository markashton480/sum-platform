"""
Name: Blocks Package Init
Path: core/sum_core/blocks/__init__.py
Purpose: Namespace for reusable block definitions within sum_core.
Family: Imported by sum_core consumers and test_project when implementing page content.
Dependencies: PageStreamBlock from base module.
"""

from .base import PageStreamBlock
from .hero import HeroImageBlock, HeroGradientBlock, HeroCTABlock
from .content import (
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
from .services import ServiceCardsBlock, ServiceCardItemBlock
from .testimonials import TestimonialsBlock, TestimonialBlock
from .gallery import GalleryBlock, GalleryImageBlock
from .trust import (
    TrustStripItemBlock,
    TrustStripBlock as TrustStripLogosBlock,
    StatItemBlock,
    StatsBlock,
)
from .process_faq import ProcessStepsBlock, FAQBlock

from .forms import ContactFormBlock, QuoteRequestFormBlock

__all__ = [
    "PageStreamBlock",
    "HeroImageBlock",
    "HeroGradientBlock",
    "HeroCTABlock",
    "HeroBlock",
    "TrustStripBlock",
    "TrustStripLogosBlock",
    "TrustStripItemBlock",
    "FeaturesListBlock",
    "ComparisonBlock",
    "PortfolioBlock",
    "ServiceCardsBlock",
    "ServiceCardItemBlock",
    "TestimonialsBlock",
    "TestimonialBlock",
    "GalleryBlock",
    "GalleryImageBlock",
    "StatItemBlock",
    "StatsBlock",
    "ProcessStepsBlock",
    "FAQBlock",
    "RichTextContentBlock",
    "EditorialHeaderBlock",
    "QuoteBlock",
    "ImageBlock",
    "ButtonGroupBlock",
    "SpacerBlock",
    "DividerBlock",
    "ContactFormBlock",
    "QuoteRequestFormBlock",
]
