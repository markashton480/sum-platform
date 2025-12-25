"""
Name: Blog Snippets
Path: core/sum_core/pages/blog.py
Purpose: Strategy models and admin representations for blog-related taxonomy.
Family: Pages.
"""

from __future__ import annotations

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class Category(models.Model):
    """
    Blog post category (single-level taxonomy).

    Allows content editors to group posts without hierarchical parents.
    """

    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'News', 'Tutorials', 'Case Studies')",
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional category description for SEO",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return str(self.name)


class CategorySnippetViewSet(SnippetViewSet):
    """Wagtail snippet viewset for blog categories."""

    model = Category
    icon = "list-ul"
    menu_label = "Blog Categories"
    list_display = ["name", "slug"]
    search_fields = ["name", "description"]
    panels = Category.panels


register_snippet(CategorySnippetViewSet)
