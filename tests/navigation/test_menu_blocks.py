"""
Name: Navigation Menu Blocks Tests
Path: tests/navigation/test_menu_blocks.py
Purpose: Unit tests for SubmenuItemBlock, MenuItemBlock, and FooterLinkSectionBlock.
Family: Navigation System Test Suite
Dependencies: pytest, wagtail.blocks

Test Coverage:
    - Max item constraints (MenuItemBlock: 8 children, FooterLinkSectionBlock: 10 links)
    - Block validation for minimal valid values
    - Block structure and field presence
"""

import pytest
from sum_core.navigation.blocks import (
    FooterLinkSectionBlock,
    MenuItemBlock,
    SubmenuItemBlock,
)
from wagtail import blocks as wagtail_blocks

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def valid_link_data():
    """Returns valid UniversalLinkBlock data for a page link."""
    return {
        "link_type": "url",
        "url": "https://example.com",
        "page": None,
        "email": "",
        "phone": "",
        "anchor": "",
        "link_text": "Example",
        "open_in_new_tab": None,
    }


@pytest.fixture
def valid_submenu_item_data(valid_link_data):
    """Returns valid SubmenuItemBlock data."""
    return {
        "label": "Submenu Item",
        "link": valid_link_data,
    }


@pytest.fixture
def valid_menu_item_data(valid_link_data):
    """Returns valid MenuItemBlock data with no children."""
    return {
        "label": "Menu Item",
        "link": valid_link_data,
        "children": [],
    }


@pytest.fixture
def valid_footer_section_data(valid_link_data):
    """Returns valid FooterLinkSectionBlock data with one link."""
    return {
        "title": "Footer Section",
        "links": [valid_link_data],
    }


# =============================================================================
# SubmenuItemBlock Tests
# =============================================================================


class TestSubmenuItemBlock:
    """Tests for SubmenuItemBlock."""

    def test_block_has_required_fields(self):
        """Verify SubmenuItemBlock has label and link fields."""
        block = SubmenuItemBlock()
        field_names = [name for name, _ in block.child_blocks.items()]
        assert "label" in field_names
        assert "link" in field_names

    def test_label_max_length_50(self):
        """Verify label field has max_length of 50."""
        block = SubmenuItemBlock()
        label_block = block.child_blocks["label"]
        assert label_block.field.max_length == 50

    def test_submenu_item_can_clean_valid_data(self, valid_submenu_item_data):
        """Verify SubmenuItemBlock validates minimal valid data."""
        block = SubmenuItemBlock()
        # Should not raise an exception
        result = block.clean(valid_submenu_item_data)
        assert result["label"] == "Submenu Item"


# =============================================================================
# MenuItemBlock Tests
# =============================================================================


class TestMenuItemBlock:
    """Tests for MenuItemBlock."""

    def test_block_has_required_fields(self):
        """Verify MenuItemBlock has label, link, and children fields."""
        block = MenuItemBlock()
        field_names = [name for name, _ in block.child_blocks.items()]
        assert "label" in field_names
        assert "link" in field_names
        assert "children" in field_names

    def test_label_max_length_50(self):
        """Verify label field has max_length of 50."""
        block = MenuItemBlock()
        label_block = block.child_blocks["label"]
        assert label_block.field.max_length == 50

    def test_children_is_list_block(self):
        """Verify children field is a ListBlock."""
        block = MenuItemBlock()
        children_block = block.child_blocks["children"]
        assert isinstance(children_block, wagtail_blocks.ListBlock)

    def test_children_max_num_is_8(self):
        """Verify children ListBlock has max_num of 8."""
        block = MenuItemBlock()
        children_block = block.child_blocks["children"]
        assert children_block.meta.max_num == 8

    def test_menu_item_can_clean_valid_data(self, valid_menu_item_data):
        """Verify MenuItemBlock validates minimal valid data."""
        block = MenuItemBlock()
        # Should not raise an exception
        result = block.clean(valid_menu_item_data)
        assert result["label"] == "Menu Item"

    def test_menu_item_children_max_8_enforced(
        self, valid_menu_item_data, valid_submenu_item_data
    ):
        """
        Verify MenuItemBlock raises ValidationError when more than 8 children.

        AC: MenuItemBlock.children enforces max 8 submenu items.
        """
        block = MenuItemBlock()

        # Create data with 9 children (exceeds max of 8)
        data = valid_menu_item_data.copy()
        data["children"] = [valid_submenu_item_data.copy() for _ in range(9)]

        with pytest.raises(wagtail_blocks.StructBlockValidationError) as exc_info:
            block.clean(data)

        # Verify the error is on the children field
        assert "children" in exc_info.value.block_errors

    def test_menu_item_with_8_children_is_valid(
        self, valid_menu_item_data, valid_submenu_item_data
    ):
        """Verify MenuItemBlock accepts exactly 8 children (boundary case)."""
        block = MenuItemBlock()

        # Create data with exactly 8 children (at the limit)
        data = valid_menu_item_data.copy()
        data["children"] = [valid_submenu_item_data.copy() for _ in range(8)]

        # Should not raise an exception
        result = block.clean(data)
        assert len(result["children"]) == 8


# =============================================================================
# FooterLinkSectionBlock Tests
# =============================================================================


class TestFooterLinkSectionBlock:
    """Tests for FooterLinkSectionBlock."""

    def test_block_has_required_fields(self):
        """Verify FooterLinkSectionBlock has title and links fields."""
        block = FooterLinkSectionBlock()
        field_names = [name for name, _ in block.child_blocks.items()]
        assert "title" in field_names
        assert "links" in field_names

    def test_title_max_length_50(self):
        """Verify title field has max_length of 50."""
        block = FooterLinkSectionBlock()
        title_block = block.child_blocks["title"]
        assert title_block.field.max_length == 50

    def test_links_is_list_block(self):
        """Verify links field is a ListBlock."""
        block = FooterLinkSectionBlock()
        links_block = block.child_blocks["links"]
        assert isinstance(links_block, wagtail_blocks.ListBlock)

    def test_links_max_num_is_10(self):
        """Verify links ListBlock has max_num of 10."""
        block = FooterLinkSectionBlock()
        links_block = block.child_blocks["links"]
        assert links_block.meta.max_num == 10

    def test_footer_section_can_clean_valid_data(self, valid_footer_section_data):
        """Verify FooterLinkSectionBlock validates minimal valid data."""
        block = FooterLinkSectionBlock()
        # Should not raise an exception
        result = block.clean(valid_footer_section_data)
        assert result["title"] == "Footer Section"

    def test_footer_section_links_max_10_enforced(
        self, valid_footer_section_data, valid_link_data
    ):
        """
        Verify FooterLinkSectionBlock raises ValidationError when more than 10 links.

        AC: FooterLinkSectionBlock.links enforces max 10 links.
        """
        block = FooterLinkSectionBlock()

        # Create data with 11 links (exceeds max of 10)
        data = valid_footer_section_data.copy()
        data["links"] = [valid_link_data.copy() for _ in range(11)]

        with pytest.raises(wagtail_blocks.StructBlockValidationError) as exc_info:
            block.clean(data)

        # Verify the error is on the links field
        assert "links" in exc_info.value.block_errors

    def test_footer_section_with_10_links_is_valid(
        self, valid_footer_section_data, valid_link_data
    ):
        """Verify FooterLinkSectionBlock accepts exactly 10 links (boundary case)."""
        block = FooterLinkSectionBlock()

        # Create data with exactly 10 links (at the limit)
        data = valid_footer_section_data.copy()
        data["links"] = [valid_link_data.copy() for _ in range(10)]

        # Should not raise an exception
        result = block.clean(data)
        assert len(result["links"]) == 10


class TestBlockDependencies:
    """Tests verifying blocks correctly depend on UniversalLinkBlock."""

    def test_submenu_item_uses_universal_link_block(self):
        """Verify SubmenuItemBlock uses UniversalLinkBlock (not duplicated logic)."""
        from sum_core.blocks import UniversalLinkBlock

        block = SubmenuItemBlock()
        link_block = block.child_blocks["link"]
        assert isinstance(link_block, UniversalLinkBlock)

    def test_menu_item_uses_universal_link_block(self):
        """Verify MenuItemBlock uses UniversalLinkBlock."""
        from sum_core.blocks import UniversalLinkBlock

        block = MenuItemBlock()
        link_block = block.child_blocks["link"]
        assert isinstance(link_block, UniversalLinkBlock)

    def test_footer_section_uses_universal_link_block(self):
        """Verify FooterLinkSectionBlock.links uses UniversalLinkBlock."""
        from sum_core.blocks import UniversalLinkBlock

        block = FooterLinkSectionBlock()
        links_block = block.child_blocks["links"]
        # links is a ListBlock, check its child_block
        assert isinstance(links_block.child_block, UniversalLinkBlock)

    def test_menu_item_children_use_submenu_item_block(self):
        """Verify MenuItemBlock.children uses SubmenuItemBlock."""
        block = MenuItemBlock()
        children_block = block.child_blocks["children"]
        # children is a ListBlock, check its child_block
        assert isinstance(children_block.child_block, SubmenuItemBlock)
