"""
Name: Blog Search URLs
Path: core/sum_core/search/urls.py
Purpose: URL patterns for blog search functionality.
Family: Search.
"""

from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.blog_search, name="blog_search"),
]
