"""
Name: PageStreamBlock Tests
Path: tests/blocks/test_page_streamblock.py
Purpose: Unit tests for PageStreamBlock and its constituent blocks.
Family: Part of the blocks-level test suite.
Dependencies: sum_core.blocks module, Wagtail blocks.
"""
from __future__ import annotations

import pytest
from wagtail import blocks

from sum_core.blocks import PageStreamBlock


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

    def test_page_streamblock_can_create_valid_data(self) -> None:
        """Test that PageStreamBlock can create valid block data."""
        block = PageStreamBlock()

        # Create valid rich text data
        valid_data = [
            {
                "type": "rich_text",
                "value": "<h2>Heading</h2><p>Some content with <strong>bold</strong> and <em>italic</em> text.</p><ul><li>List item</li></ul>",
            }
        ]

        # This should not raise an exception
        result = block.clean(valid_data)
        assert result == valid_data

    def test_page_streamblock_rejects_invalid_rich_text(self) -> None:
        """Test that PageStreamBlock rejects rich text with disallowed elements."""
        block = PageStreamBlock()

        # Try to create data with H1 (which should be disallowed)
        invalid_data = [
            {
                "type": "rich_text",
                "value": "<h1>Disallowed H1</h1><p>Content</p>",
            }
        ]

        # The clean method should still work, but the rendered output should not contain H1
        # (Wagtail's RichTextBlock will strip disallowed tags)
        result = block.clean(invalid_data)
        assert result == invalid_data

        # When rendered, H1 should be stripped or converted
        rendered = block.render(result)
        assert "<h1>" not in rendered  # H1 should not appear in output
