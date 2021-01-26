import json
from typing import Any, Optional, Union

from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model

register = template.Library()


@register.filter
def get_dict(value: Any, arg: Any) -> Any:
    """Get an attribute of an object dynamically from a string name."""
    if hasattr(value, str(arg)):
        return getattr(value, arg)
    elif hasattr(value, "keys") and arg in value.keys():
        return value[arg]
    elif str(arg).isnumeric() and len(value) > int(arg):
        return value[int(arg)]
    else:
        return None


@register.simple_tag
def verbose_name(app_label: str, model: str, field: Optional[str] = None) -> str:
    """Get a verbose name of a model or a field by app label and model name."""
    ct = ContentType.objects.get(app_label=app_label, model=model).model_class()

    if field:
        # Field
        return ct._meta.get_field(field).verbose_name.title()
    else:
        # Whole model
        return ct._meta.verbose_name.title()


@register.simple_tag
def verbose_name_object(model: Model, field: Optional[str] = None) -> str:
    """Get a verbose name of a model or a field by a model or an instance of a model."""
    if field:
        # Field
        return model._meta.get_field(field).verbose_name.title()
    else:
        # Whole model
        return model._meta.verbose_name.title()


@register.simple_tag
def parse_json(value: Optional[str] = None) -> Union[dict, None]:
    """Template tag for parsing JSON from a string."""
    if not value:
        return None
    return json.loads(value)


@register.simple_tag(takes_context=True)
def build_badge(context: dict, item: dict) -> Any:
    """Get menu badge content from django-menu-generator dict."""
    request = context["request"]
    badge = item.get("badge")
    if callable(badge):
        return badge(request)
    else:
        return badge
