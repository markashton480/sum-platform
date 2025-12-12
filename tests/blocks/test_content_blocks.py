import pytest
from sum_core.blocks.content import (
    ButtonGroupBlock,
    DividerBlock,
    ImageBlock,
    QuoteBlock,
    RichTextContentBlock,
    SpacerBlock,
)
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
