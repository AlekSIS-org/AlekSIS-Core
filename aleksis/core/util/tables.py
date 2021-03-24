from django.utils.safestring import mark_safe

from django_tables2 import CheckBoxColumn
from django_tables2.utils import A, AttributeDict, computed_values


class MaterializeCheckboxColumn(CheckBoxColumn):
    """Checkbox column with Materialize support."""

    empty_values = ()

    @property
    def header(self):
        """Render the header cell."""
        default = {"type": "checkbox"}
        general = self.attrs.get("input")
        specific = self.attrs.get("th__input")
        attrs = AttributeDict(default, **(specific or general or {}))
        return mark_safe("<label><input %s/><span></span></label>" % attrs.as_html())  # noqa

    def render(self, value, bound_column, record):
        """Render a data cell."""
        default = {"type": "checkbox", "name": bound_column.name, "value": value}
        if self.is_checked(value, record):
            default.update({"checked": "checked"})

        general = self.attrs.get("input")
        specific = self.attrs.get("td__input")

        attrs = dict(default, **(specific or general or {}))
        attrs = computed_values(attrs, kwargs={"record": record, "value": value})
        return mark_safe(  # noqa
            "<label><input %s/><span></span</label>" % AttributeDict(attrs).as_html()
        )


class SelectColumn(MaterializeCheckboxColumn):
    """Column with a check box prepared for `ActionForm` forms."""

    def __init__(self, *args, **kwargs):
        kwargs["attrs"] = {
            "td__input": {"name": "selected_objects"},
            "th__input": {"class": "select--header-box"},
        }
        kwargs.setdefault("accessor", A("pk"))
        super().__init__(*args, **kwargs)
