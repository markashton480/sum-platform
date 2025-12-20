"""
WSGI application entry point.

Replace 'test_project_2' with your actual project name after copying.
For production, ensure DJANGO_SETTINGS_MODULE points to production settings.
"""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "test_project_2.settings.local")

application = get_wsgi_application()
