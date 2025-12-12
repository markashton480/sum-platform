"""
Name: sum_core Navigation Tags Shim
Path: core/sum_core/templatetags/navigation_tags.py
Purpose: Expose navigation template tags at the app root for `{% load navigation_tags %}`.
Family: Django template libraries.
Dependencies: sum_core.navigation.templatetags.navigation_tags.
"""

from __future__ import annotations

from sum_core.navigation.templatetags.navigation_tags import *  # noqa: F401,F403
