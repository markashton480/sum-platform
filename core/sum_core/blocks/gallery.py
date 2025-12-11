"""
Name: Gallery Blocks
Path: core/sum_core/blocks/gallery.py
Purpose: StreamField blocks for gallery/image grid sections.
Family: Used via PageStreamBlock on core pages (e.g., HomePage) and other templates.
Dependencies: Wagtail blocks, wagtail.images ImageChooserBlock, sum_core design tokens.
"""

from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class GalleryImageBlock(blocks.StructBlock):
    """Individual gallery item with image, alt text, and caption."""

    image = ImageChooserBlock(required=True, help_text="Project photo.")
    alt_text = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="For screen readers. If blank, the image title will be used."
    )
    caption = blocks.CharBlock(
        required=False,
        max_length=255,
        help_text="Short caption, e.g. location or project type."
    )

    class Meta:
        icon = "image"
        label = "Gallery Image"


class GalleryBlock(blocks.StructBlock):
    """
    Gallery section block with heading, intro text, and a grid of images.

    Provides a flexible image gallery for showcasing project photos,
    portfolio pieces, or any visual content in a responsive grid layout.
    """

    eyebrow = blocks.CharBlock(
        required=False,
        max_length=80,
        help_text="Small text above heading, e.g. 'Selected Works'."
    )
    heading = blocks.RichTextBlock(
        required=False,
        features=['bold', 'italic'],
        help_text="Main section heading. Use italics for accent styling."
    )
    intro = blocks.TextBlock(
        required=False,
        help_text="Optional supporting text."
    )
    images = blocks.ListBlock(
        GalleryImageBlock(),
        min_num=1,
        max_num=24,
        help_text="Add 1–24 images to the gallery."
    )

    class Meta:
        icon = "image"
        label = "Gallery"
        help_text = "Grid of project images with optional captions."
        template = "sum_core/blocks/gallery.html"
