"""Management utilities for an AlekSIS installation."""

import os
import sys

import django.__main__
from django.core.management import execute_from_command_line


def aleksis_cmd():
    """Run django-admin command with correct settings path."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aleksis.core.settings")
    sys.argv[0] = django.__main__.__file__
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    sys.exit(aleksis_cmd())
