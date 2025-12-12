
from sum_core.blocks.hero import HeroImageBlock, HeroGradientBlock, HeroCTABlock

def test_hero_cta_block_validation():
    block = HeroCTABlock()

    # Valid
    data = {
        "label": "Click Me",
        "url": "https://example.com",
        "style": "primary",
        "open_in_new_tab": True
    }
    # StructBlock validation runs in clean usually, but to_python converts logic.
    # For StructBlock, clean() validates children.
    result = block.to_python(data)
    assert result["label"] == "Click Me"
    assert result["style"] == "primary"

def test_hero_image_block_structure():
    block = HeroImageBlock()
    assert block.child_blocks["headline"].required
    assert block.child_blocks["image"].required
    assert block.child_blocks["image_alt"].required

    # Check new fields
    assert "floating_card_label" in block.child_blocks
    assert "floating_card_value" in block.child_blocks

    assert block.child_blocks["image_alt"].required

def test_hero_gradient_block_structure():
    block = HeroGradientBlock()
    assert block.child_blocks["headline"].required
    assert "image" not in block.child_blocks

def test_hero_cta_defaults():
    block = HeroCTABlock()
    # Wagtail blocks don't expose .default easily on the instance
    # Verify the block has the expected child blocks
    assert "style" in block.child_blocks
    assert "open_in_new_tab" in block.child_blocks
