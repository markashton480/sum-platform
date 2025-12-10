"""
Name: Test Project Home Page Models
Path: core/sum_core/test_project/home/models.py
Purpose: Provide a minimal HomePage type for exercising the SUM base layout and branding.
Family: Used only by sum_core.test_project; client projects will define their own page types later.
Dependencies: Wagtail Page model, sum_core base template.
"""
from __future__ import annotations

from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class HomePage(Page):
    """
    Minimal homepage for the test project.

    NOTE: This is an enabling stub for Milestone 1 and does NOT yet satisfy
    the full US-P01 Homepage acceptance criteria (StreamField, SEO mixins, etc.).
    Those will be implemented in the Page Types milestone.
    """

    intro: RichTextField = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    template: str = "sum_core/home_page.html"
