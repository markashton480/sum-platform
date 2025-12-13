"""
Name: Nested Menus Tests
Path: tests/navigation/test_nested_menus.py
Purpose: Unit tests for nested menu structure and active state propagation.
Family: Navigation System Test Suite
Dependencies: pytest, django.template, sum_core.navigation
"""

from unittest.mock import MagicMock, patch

import pytest
from django.test import RequestFactory
from sum_core.navigation.templatetags.navigation_tags import header_nav


@pytest.mark.django_db
class TestNestedMenus:
    """Tests for nested menu structure and active state propagation."""

    @pytest.fixture
    def nested_menu_data(self):
        """
        Returns a mock-like structure mirroring what StreamField would return.
        We pretend these are blocks/values.
        """
        # Top Level
        return [
            {
                "label": "Top Level",
                "link": {"link_type": "url", "url": "/top/"},
                "children": [
                    {
                        "label": "Submenu",
                        "link": {"link_type": "url", "url": "/top/sub/"},
                        "children": [
                            {
                                "label": "Grandchild",
                                "link": {"link_type": "url", "url": "/top/sub/grand/"},
                            }
                        ],
                    }
                ],
            }
        ]

    @patch(
        "sum_core.navigation.templatetags.navigation_tags.get_effective_header_settings"
    )
    def test_builds_nested_structure_3_levels(
        self, mock_settings, wagtail_default_site, nested_menu_data
    ):
        """Verify header_nav builds 3 levels of menu items."""
        # Setup context
        rf = RequestFactory()
        request = rf.get("/")
        template_context = {"request": request}

        # Mock settings to return our data
        mock_obj = MagicMock()
        mock_obj.menu_items = nested_menu_data
        # Mock other required fields to avoid errors
        mock_obj.header_cta.link = []
        mock_obj.phone_number = ""
        mock_obj.show_phone_in_header = False
        mock_settings.return_value = mock_obj

        result = header_nav(template_context)

        items = result["menu_items"]
        assert len(items) == 1
        top = items[0]
        assert top["label"] == "Top Level"
        assert top["has_children"] is True

        children = top["children"]
        assert len(children) == 1
        sub = children[0]
        assert sub["label"] == "Submenu"
        assert sub["has_children"] is True

        grand_children = sub["children"]
        assert len(grand_children) == 1
        grand = grand_children[0]
        assert grand["label"] == "Grandchild"
        assert grand["has_children"] is False

    @patch(
        "sum_core.navigation.templatetags.navigation_tags.get_effective_header_settings"
    )
    def test_active_state_propagates_from_grandchild(
        self, mock_settings, wagtail_default_site, nested_menu_data
    ):
        """Verify active state bubbles up from grandchild to top level."""
        # Setup request for the grandchild URL
        rf = RequestFactory()
        request = rf.get("/top/sub/grand/")
        context = {"request": request}

        mock_obj = MagicMock()
        mock_obj.menu_items = nested_menu_data
        mock_obj.header_cta.link = []
        mock_obj.phone_number = ""
        mock_obj.show_phone_in_header = False
        mock_settings.return_value = mock_obj

        result = header_nav(context)

        top = result["menu_items"][0]
        sub = top["children"][0]
        grand = sub["children"][0]

        # Grandchild should be active and current
        assert grand["is_current"] is True
        assert grand["is_active"] is True

        # Parent (Submenu) should be active but NOT current
        assert sub["is_current"] is False
        assert sub["is_active"] is True

        # Grandparent (Top) should be active but NOT current
        assert top["is_current"] is False
        assert top["is_active"] is True
