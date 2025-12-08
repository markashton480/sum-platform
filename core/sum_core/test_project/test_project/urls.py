"""
Name: Test Project URL Configuration
Path: core/sum_core/test_project/test_project/urls.py
Purpose: Minimal URL configuration to expose Wagtail admin and root page.
Family: Used by test_project when running the development server or checks.
Dependencies: Django, Wagtail
"""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include("wagtail.admin.urls")),
    path("documents/", include("wagtail.documents.urls")),
]
