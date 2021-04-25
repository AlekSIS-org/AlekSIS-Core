"""Helpers for SASS/SCSS compilation."""

from colour import web2hex
from sass import SassColor
from sass_processor.storage import SassFileStorage

from .core_helpers import get_site_preferences


def get_colour(html_colour: str) -> SassColor:
    """Get a SASS colour object from an HTML colour string."""
    rgb = web2hex(html_colour, force_long=True)[1:]
    r, g, b = int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16)

    return SassColor(r, g, b, 255)


def get_preference(section: str, name: str) -> str:
    """Get a preference from dynamic-preferences."""
    return get_site_preferences()[f"{section}__{name}"]


def clean_scss(*args, **kwargs) -> None:
    """Unlink compiled CSS (i.e. cache invalidation)."""
    sass_storage = SassFileStorage()
    __, files = sass_storage.listdir("")

    for source_map in filter(lambda x: x.endswith(".css.map"), files):
        sass_storage.delete(source_map)
