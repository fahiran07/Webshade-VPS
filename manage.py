#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Import Celery to initialize it
from webshade.celery import app as celery_app

# Ensuring that Celery is always imported when Django starts
__all__ = ('celery_app',)

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webshade.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
