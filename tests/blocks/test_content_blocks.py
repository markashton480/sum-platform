import pytest
from sum_core.blocks.content import (
    ButtonGroupBlock,
    DividerBlock,
    ImageBlock,
    ManifestoBlock,
    PortfolioItemBlock,
    QuoteBlock,
    RichTextContentBlock,
    SpacerBlock,
)
from sum_core.blocks.gallery import FeaturedCaseStudyBlock
from wagtail import blocks


@pytest.mark.django_db
def test_rich_text_content_block_definition():
    block = RichTextContentBlock()
    assert isinstance(block, blocks.StructBlock)
    assert "body" in block.child_blocks
    assert "align" in block.child_blocks
    assert isinstance(block.child_blocks["body"], blocks.RichTextBlock)


@pytest.mark.django_db
def test_quote_block_definition():
    block = QuoteBlock()
    assert "quote" in block.child_blocks
    assert "author" in block.child_blocks
    assert "role" in block.child_blocks


@pytest.mark.django_db
def test_image_block_definition():
    block = ImageBlock()
    assert "image" in block.child_blocks
    assert "alt_text" in block.child_blocks
    assert "caption" in block.child_blocks
    assert "full_width" in block.child_blocks


@pytest.mark.django_db
def test_button_group_block_definition():
    block = ButtonGroupBlock()
    assert "alignment" in block.child_blocks
    assert "buttons" in block.child_blocks
    # Test valid alignment choices
    choices = [c[0] for c in block.child_blocks["alignment"].field.choices]
    assert "left" in choices
    assert "center" in choices
    assert "right" in choices


@pytest.mark.django_db
def test_spacer_block_definition():
    block = SpacerBlock()
    assert "size" in block.child_blocks
    choices = [c[0] for c in block.child_blocks["size"].field.choices]
    assert "small" in choices
    assert "xlarge" in choices


@pytest.mark.django_db
def test_divider_block_definition():
    block = DividerBlock()
    assert "style" in block.child_blocks
    choices = [c[0] for c in block.child_blocks["style"].field.choices]
    assert "muted" in choices
    assert "accent" in choices


@pytest.mark.django_db
def test_portfolio_item_block_metadata_fields():
    block = PortfolioItemBlock()
    assert "constraint" in block.child_blocks
    assert "material" in block.child_blocks
    assert "outcome" in block.child_blocks


@pytest.mark.django_db
def test_manifesto_block_definition():
    block = ManifestoBlock()
    assert isinstance(block, blocks.StructBlock)
    assert "eyebrow" in block.child_blocks
    assert "heading" in block.child_blocks
    assert "body" in block.child_blocks
    assert "quote" in block.child_blocks
    assert "cta_label" not in block.child_blocks
    assert "cta_url" not in block.child_blocks

    # Check required fields
    assert block.child_blocks["heading"].required
    assert block.child_blocks["body"].required
    assert not block.child_blocks["eyebrow"].required
    assert not block.child_blocks["quote"].required


@pytest.mark.django_db
def test_featured_case_study_block_definition():
    block = FeaturedCaseStudyBlock()
    assert isinstance(block, blocks.StructBlock)

    # Check fields
    expected_fields = [
        "eyebrow",
        "heading",
        "intro",
        "points",
        "cta_text",
        "cta_url",
        "image",
        "image_alt",
        "stats_label",
        "stats_value",
    ]
    for field in expected_fields:
        assert field in block.child_blocks

    # Check requiredness
    assert block.child_blocks["heading"].required
    assert block.child_blocks["image"].required
    assert block.child_blocks["image_alt"].required

    # Check non-required
    assert not block.child_blocks["eyebrow"].required
    assert not block.child_blocks["intro"].required
    assert not block.child_blocks["points"].required
    assert not block.child_blocks["cta_text"].required
    assert not block.child_blocks["cta_url"].required
    assert not block.child_blocks["stats_label"].required
    assert not block.child_blocks["stats_value"].required
