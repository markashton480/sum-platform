#!/usr/bin/env python
"""
Name: Smoke Consumer manage.py
Path: clients/_smoke_consumer/manage.py
Purpose: Django management command entry point for the smoke consumer project.
Family: Validation/proof project for sum_core consumability.
Dependencies: Django
"""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smoke_consumer.settings")
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
