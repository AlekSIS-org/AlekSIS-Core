from django.template import Library, loader

register = Library()


@register.simple_tag(takes_context=True)
def include_widget(context, widget) -> dict:
    """Render a template with context from a defined widget."""
    template = loader.get_template(widget.get_template())
    request = context["request"]
    context = widget.get_context(request)

    return template.render(context)
