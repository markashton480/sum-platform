"""
Name: Smoke Consumer WSGI Configuration
Path: clients/_smoke_consumer/smoke_consumer/wsgi.py
Purpose: WSGI application entry point.
Family: Validation/proof project for sum_core consumability.
Dependencies: Django
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smoke_consumer.settings")

application = get_wsgi_application()
