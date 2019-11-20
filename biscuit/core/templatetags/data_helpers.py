from typing import Dict, Any

from django import template

register = template.Library()


@register.filter
def get_dict(value: Any, arg: Any) -> Any:
    """Gets an attribute of an object dynamically from a string name"""

    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, 'has_key') and value.has_key(arg):
        return value[arg]
    elif str(arg).isnumeric() and len(value) > int(arg):
        return value[int(arg)]
    else:
        return None
