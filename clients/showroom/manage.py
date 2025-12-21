#!/usr/bin/env python
"""
Django management command entry point.

Replace 'showroom' with your actual project name after copying.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Load environment variables from .env file (if it exists)
# This allows SUM_CANONICAL_THEME_ROOT and other settings to be configured per-client
try:
    from dotenv import load_dotenv

    env_file = Path(__file__).resolve().parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass  # python-dotenv not installed, skip


def main() -> None:
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "showroom.settings.local")
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
