"""
Name: Trust & Stats Blocks Tests
Path: tests/blocks/test_trust_blocks.py
Purpose: Unit tests for TrustStripBlock (logos) and StatsBlock.
Family: Part of the blocks-level test suite.
Dependencies: sum_core.blocks.trust module, Wagtail blocks.
"""

from sum_core.blocks.trust import (
    StatItemBlock,
    StatsBlock,
    TrustStripBlock,
    TrustStripItemBlock,
)
from wagtail.blocks import ListBlock, StructBlock


class TestTrustStripItemBlock:
    """Test the TrustStripItemBlock structure."""

    def test_block_structure(self) -> None:
        """Test that TrustStripItemBlock has expected fields."""
        block = TrustStripItemBlock()
        assert isinstance(block, StructBlock)

        assert "logo" in block.child_blocks
        assert "alt_text" in block.child_blocks
        assert "url" in block.child_blocks

    def test_required_fields(self) -> None:
        """Test that logo and alt_text are required, url is optional."""
        block = TrustStripItemBlock()

        assert block.child_blocks["logo"].required
        assert block.child_blocks["alt_text"].required
        assert not block.child_blocks["url"].required


class TestTrustStripBlock:
    """Test the TrustStripBlock (logos variant) structure."""

    def test_block_structure(self) -> None:
        """Test that TrustStripBlock has expected fields."""
        block = TrustStripBlock()
        assert isinstance(block, StructBlock)

        assert "eyebrow" in block.child_blocks
        assert "items" in block.child_blocks

        assert isinstance(block.child_blocks["items"], ListBlock)
        assert isinstance(block.child_blocks["items"].child_block, TrustStripItemBlock)

    def test_items_min_max_constraints(self) -> None:
        """Test that items ListBlock has min_num=2 and max_num=8."""
        block = TrustStripBlock()
        items_block = block.child_blocks["items"]

        assert items_block.meta.min_num == 2
        assert items_block.meta.max_num == 8

    def test_eyebrow_optional(self) -> None:
        """Test that eyebrow field is optional."""
        block = TrustStripBlock()
        assert not block.child_blocks["eyebrow"].required

    def test_meta_template(self) -> None:
        """Test that Meta.template is correctly set."""
        block = TrustStripBlock()
        assert block.meta.template == "sum_core/blocks/trust_strip_logos.html"

    def test_meta_icon_and_label(self) -> None:
        """Test Meta icon and label."""
        block = TrustStripBlock()
        assert block.meta.icon == "group"
        assert block.meta.label == "Trust Strip (Logos)"


class TestStatItemBlock:
    """Test the StatItemBlock structure."""

    def test_block_structure(self) -> None:
        """Test that StatItemBlock has expected fields."""
        block = StatItemBlock()
        assert isinstance(block, StructBlock)

        assert "value" in block.child_blocks
        assert "label" in block.child_blocks
        assert "prefix" in block.child_blocks
        assert "suffix" in block.child_blocks

    def test_required_fields(self) -> None:
        """Test that value and label are required, prefix/suffix are optional."""
        block = StatItemBlock()

        assert block.child_blocks["value"].required
        assert block.child_blocks["label"].required
        assert not block.child_blocks["prefix"].required
        assert not block.child_blocks["suffix"].required

    def test_value_accepts_string(self) -> None:
        """Test that value field accepts string values like '500+'."""
        block = StatItemBlock()
        value_block = block.child_blocks["value"]

        # Should accept strings with special characters
        assert value_block.clean("500+") == "500+"
        assert value_block.clean("15") == "15"
        assert value_block.clean("98%") == "98%"


class TestStatsBlock:
    """Test the StatsBlock structure."""

    def test_block_structure(self) -> None:
        """Test that StatsBlock has expected fields."""
        block = StatsBlock()
        assert isinstance(block, StructBlock)

        assert "eyebrow" in block.child_blocks
        assert "intro" in block.child_blocks
        assert "items" in block.child_blocks

        assert isinstance(block.child_blocks["items"], ListBlock)
        assert isinstance(block.child_blocks["items"].child_block, StatItemBlock)

    def test_items_min_max_constraints(self) -> None:
        """Test that items ListBlock has min_num=2 and max_num=4."""
        block = StatsBlock()
        items_block = block.child_blocks["items"]

        assert items_block.meta.min_num == 2
        assert items_block.meta.max_num == 4

    def test_optional_fields(self) -> None:
        """Test that eyebrow and intro are optional."""
        block = StatsBlock()
        assert not block.child_blocks["eyebrow"].required
        assert not block.child_blocks["intro"].required

    def test_meta_template(self) -> None:
        """Test that Meta.template is correctly set."""
        block = StatsBlock()
        assert block.meta.template == "sum_core/blocks/stats.html"

    def test_meta_icon_and_label(self) -> None:
        """Test Meta icon and label."""
        block = StatsBlock()
        assert block.meta.icon == "snippet"
        assert block.meta.label == "Stats"

    def test_round_trip(self) -> None:
        """Test initialising block value dict, clean, and access values."""
        block = StatsBlock()
        value = {
            "eyebrow": "By the Numbers",
            "intro": "Our track record speaks for itself.",
            "items": [
                {
                    "value": "500",
                    "label": "Projects Completed",
                    "prefix": ">",
                    "suffix": "+",
                },
                {
                    "value": "15",
                    "label": "Years Experience",
                    "prefix": "",
                    "suffix": "yrs",
                },
            ],
        }

        clean_value = block.clean(value)

        assert clean_value["eyebrow"] == "By the Numbers"
        assert clean_value["intro"] == "Our track record speaks for itself."
        assert len(clean_value["items"]) == 2
        assert clean_value["items"][0]["value"] == "500"
        assert clean_value["items"][0]["prefix"] == ">"
        assert clean_value["items"][0]["suffix"] == "+"
        assert clean_value["items"][1]["label"] == "Years Experience"
