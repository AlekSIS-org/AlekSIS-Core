from importlib import import_module
import pkgutil
from typing import Sequence


def get_app_packages() -> Sequence:
    """ Find all packages within the biscuit.apps namespace. """

    # Import error are non-fatal here because probably simply no app is installed.
    try:
        import biscuit.apps
    except ImportError:
        return []

    pkgs = []
    for pkg in pkgutil.iter_modules(biscuit.apps.__path__):
        mod = import_module('biscuit.apps.%s' % pkg[1])

        # Add additional apps defined in module's INSTALLED_APPS constant
        additional_apps = getattr(mod, 'INSTALLED_APPS', [])
        for app in additional_apps:
            if not app in pkgs:
                pkgs.append(app)

        pkgs.append('biscuit.apps.%s' % pkg[1])

    return pkgs