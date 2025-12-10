"""
Name: Content Blocks
Path: core/sum_core/blocks/content.py
Purpose: Define StructBlocks for rich content sections (Hero, Features, Portfolio, etc.).
Family: Used by StreamFields in pages.
"""
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ButtonBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True)
    link = blocks.URLBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    style = blocks.ChoiceBlock(choices=[
        ('btn-primary', 'Primary'),
        ('btn-outline', 'Outline'),
    ], default='btn-primary')

    class Meta:
        template = "sum_core/blocks/button.html"
        icon = "placeholder"


class HeroBlock(blocks.StructBlock):
    status_text = blocks.CharBlock(required=False, help_text="e.g. Available for Q1 2025")
    title = blocks.TextBlock(required=True, help_text="Main heading. Use html tags like <span class='italic-accent'> for styling.")
    description = blocks.TextBlock(required=True)
    primary_cta = ButtonBlock(required=False)
    secondary_cta = ButtonBlock(required=False)
    image = ImageChooserBlock(required=True)
    float_card_label = blocks.CharBlock(required=False, help_text="e.g. Est. Annual Savings")
    float_card_value = blocks.CharBlock(required=False, help_text="e.g. £2,450")

    class Meta:
        template = "sum_core/blocks/hero.html"
        icon = "image"
        label = "Hero Section"


class TrustItemBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True)

    class Meta:
        icon = "tick"


class TrustStripBlock(blocks.StructBlock):
    items = blocks.ListBlock(TrustItemBlock())

    class Meta:
        template = "sum_core/blocks/trust_strip.html"
        icon = "list-ul"
        label = "Trust Strip"


class FeatureBlock(blocks.StructBlock):
    icon = blocks.CharBlock(required=True, help_text="Emoji or text icon")
    title = blocks.CharBlock(required=True)
    description = blocks.TextBlock(required=True)

    class Meta:
        icon = "tick-inverse"


class FeaturesListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    intro = blocks.TextBlock(required=False)
    features = blocks.ListBlock(FeatureBlock())

    class Meta:
        template = "sum_core/blocks/features_list.html"
        icon = "list-ul"
        label = "Features List"


class ComparisonBlock(blocks.StructBlock):
    accent_text = blocks.CharBlock(required=False, help_text="Small italic text above title")
    title = blocks.CharBlock(required=True)
    description = blocks.TextBlock(required=True)
    image_before = ImageChooserBlock(required=True, help_text="Background/Before image")
    image_after = ImageChooserBlock(required=True, help_text="Foreground/After image")

    class Meta:
        template = "sum_core/blocks/comparison.html"
        icon = "image"
        label = "Comparison Slider"


class ProjectBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    meta = blocks.CharBlock(required=True, help_text="e.g. Kensington • 12kW System")
    title = blocks.CharBlock(required=True)

    class Meta:
        icon = "image"


class PortfolioBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True)
    projects = blocks.ListBlock(ProjectBlock())

    class Meta:
        template = "sum_core/blocks/portfolio.html"
        icon = "grip"
        label = "Portfolio Grid"

