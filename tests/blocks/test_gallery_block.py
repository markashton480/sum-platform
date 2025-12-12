"""
Name: Gallery Block Tests
Path: tests/blocks/test_gallery_block.py
Purpose: Unit tests for PortfolioBlock and PortfolioItemBlock structure and constraints.
Family: Part of the blocks-level test suite.
Dependencies: sum_core.blocks.content module, Wagtail blocks, pytest.
"""

from sum_core.blocks.content import PortfolioBlock, PortfolioItemBlock
from wagtail.blocks import ListBlock, StructBlock


class TestPortfolioBlockStructure:
    """Test the PortfolioBlock structure and child blocks."""

    def test_portfolio_block_is_struct_block(self) -> None:
        """Test that PortfolioBlock is a StructBlock."""
        block = PortfolioBlock()
        assert isinstance(block, StructBlock)

    def test_portfolio_block_has_required_child_blocks(self) -> None:
        """Test that PortfolioBlock has eyebrow, heading, intro, and items."""
        block = PortfolioBlock()

        assert "eyebrow" in block.child_blocks
        assert "heading" in block.child_blocks
        assert "intro" in block.child_blocks
        assert "items" in block.child_blocks

    def test_items_is_list_block_of_portfolio_item_block(self) -> None:
        """Test that items is a ListBlock containing PortfolioItemBlock."""
        block = PortfolioBlock()
        items_block = block.child_blocks["items"]

        assert isinstance(items_block, ListBlock)
        assert isinstance(items_block.child_block, PortfolioItemBlock)

    def test_items_list_constraints(self) -> None:
        """Test that items ListBlock has min_num=1 and max_num=12."""
        block = PortfolioBlock()
        items_block = block.child_blocks["items"]

        assert items_block.meta.min_num == 1
        assert items_block.meta.max_num == 12

    def test_heading_is_richtext_block(self) -> None:
        """Test that heading is a RichTextBlock with bold/italic features."""
        from wagtail.blocks import RichTextBlock

        block = PortfolioBlock()
        heading_block = block.child_blocks["heading"]
        assert isinstance(heading_block, RichTextBlock)
        assert "bold" in heading_block.features
        assert "italic" in heading_block.features

    def test_optional_fields(self) -> None:
        """Test that eyebrow and intro are optional, heading is required."""
        block = PortfolioBlock()
        assert not block.child_blocks["eyebrow"].required
        assert block.child_blocks["heading"].required
        assert not block.child_blocks["intro"].required

    def test_block_meta_attributes(self) -> None:
        """Test that PortfolioBlock has correct Meta attributes."""
        block = PortfolioBlock()

        assert block.meta.icon == "grip"
        assert block.meta.label == "Portfolio Gallery"
        assert block.meta.template == "sum_core/blocks/portfolio.html"


class TestPortfolioItemBlockStructure:
    """Test the PortfolioItemBlock structure."""

    def test_portfolio_item_block_is_struct_block(self) -> None:
        """Test that PortfolioItemBlock is a StructBlock."""
        block = PortfolioItemBlock()
        assert isinstance(block, StructBlock)

    def test_has_required_fields(self) -> None:
        """Test fields existence."""
        block = PortfolioItemBlock()
        fields = ["image", "alt_text", "title", "location", "services", "link_url"]
        for field in fields:
            assert field in block.child_blocks

    def test_required_fields(self) -> None:
        """Test that image, alt_text, title are required."""
        block = PortfolioItemBlock()
        assert block.child_blocks["image"].required
        assert block.child_blocks["alt_text"].required
        assert block.child_blocks["title"].required

    def test_optional_fields(self) -> None:
        """Test that location, services, link_url are optional."""
        block = PortfolioItemBlock()
        assert not block.child_blocks["location"].required
        assert not block.child_blocks["services"].required
        assert not block.child_blocks["link_url"].required
