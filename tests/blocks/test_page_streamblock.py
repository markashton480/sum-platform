"""
Name: PageStreamBlock Tests
Path: tests/blocks/test_page_streamblock.py
Purpose: Unit tests for PageStreamBlock and its constituent blocks.
Family: Part of the blocks-level test suite.
Dependencies: sum_core.blocks module, Wagtail blocks.
"""

from __future__ import annotations

import pytest
from sum_core.blocks import PageStreamBlock
from wagtail import blocks

pytestmark = pytest.mark.django_db


class TestPageStreamBlock:
    """Test the PageStreamBlock StreamBlock definition."""

    def test_page_streamblock_can_be_instantiated(self) -> None:
        """Test that PageStreamBlock can be created without errors."""
        block = PageStreamBlock()
        assert block is not None

    def test_page_streamblock_has_rich_text_block(self) -> None:
        """Test that PageStreamBlock includes a rich_text block."""
        block = PageStreamBlock()
        assert "rich_text" in block.child_blocks

        rich_text_block = block.child_blocks["rich_text"]
        assert isinstance(rich_text_block, blocks.RichTextBlock)

    def test_rich_text_block_features(self) -> None:
        """Test that the rich_text block has the correct features configured."""
        block = PageStreamBlock()
        rich_text_block = block.child_blocks["rich_text"]

        # Check that only H2-H4 are allowed (no H1)
        expected_features = ["h2", "h3", "h4", "bold", "italic", "link", "ol", "ul"]
        assert set(rich_text_block.features) == set(expected_features)

        # Ensure H1 is NOT in features
        assert "h1" not in rich_text_block.features

    def test_page_streamblock_includes_hero_blocks(self) -> None:
        """Test that PageStreamBlock includes hero block types."""
        block = PageStreamBlock()
        assert "hero_image" in block.child_blocks
        assert "hero_gradient" in block.child_blocks

    def test_page_streamblock_includes_content_blocks(self) -> None:
        """Test that PageStreamBlock includes standard content blocks."""
        block = PageStreamBlock()
        assert "service_cards" in block.child_blocks
        assert "testimonials" in block.child_blocks
        assert "gallery" in block.child_blocks
        assert "trust_strip" in block.child_blocks
        assert "trust_strip_logos" in block.child_blocks
        assert "stats" in block.child_blocks
        assert "features" in block.child_blocks
        assert "comparison" in block.child_blocks
        assert "manifesto" in block.child_blocks
        assert "portfolio" in block.child_blocks
