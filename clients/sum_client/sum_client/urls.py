"""
Name: SUM Client URL Configuration
Path: clients/sum_client/sum_client/urls.py
Purpose: URL routing including all sum_core endpoints.
Family: Client project consuming sum_core.
Dependencies: Django, Wagtail, sum_core
"""
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Django admin (for FormConfiguration etc.)
    path("django-admin/", admin.site.urls),
    # Wagtail admin
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # SUM Core endpoints
    path("forms/", include("sum_core.forms.urls")),  # Form submissions
    path("", include("sum_core.ops.urls")),  # /health/
    path("", include("sum_core.seo.urls")),  # sitemap.xml, robots.txt
    # Wagtail page serving (must be last)
    path("", include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
