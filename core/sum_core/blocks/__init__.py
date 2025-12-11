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
)
from .services import ServiceCardsBlock, ServiceCardItemBlock
from .testimonials import TestimonialsBlock, TestimonialBlock
from .gallery import GalleryBlock, GalleryImageBlock

__all__ = [
    "PageStreamBlock",
    "HeroImageBlock",
    "HeroGradientBlock",
    "HeroCTABlock",
    "HeroBlock",
    "TrustStripBlock",
    "FeaturesListBlock",
    "ComparisonBlock",
    "PortfolioBlock",
    "ServiceCardsBlock",
    "ServiceCardItemBlock",
    "TestimonialsBlock",
    "TestimonialBlock",
    "GalleryBlock",
    "GalleryImageBlock",
]
