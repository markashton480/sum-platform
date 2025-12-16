"""
Name: SUM Client WSGI Configuration
Path: clients/sum_client/sum_client/wsgi.py
Purpose: WSGI application entry point.
Family: Client project consuming sum_core.
Dependencies: Django
"""
from __future__ import annotations

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sum_client.settings.local")

application = get_wsgi_application()
