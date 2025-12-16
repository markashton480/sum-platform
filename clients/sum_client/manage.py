#!/usr/bin/env python
"""
Name: SUM Client manage.py
Path: clients/sum_client/manage.py
Purpose: Django management command entry point for the sum_client project.
Family: Client project consuming sum_core.
Dependencies: Django
"""
from __future__ import annotations

import os
import sys


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sum_client.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
