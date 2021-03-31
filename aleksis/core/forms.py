from datetime import datetime, time
from typing import Callable, Dict, List, Sequence, Tuple

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm
from allauth.account.utils import get_user_model, setup_user_email
from dj_cleavejs import CleaveWidget
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget, Select2Widget
from dynamic_preferences.forms import PreferenceForm
from material import Fieldset, Layout, Row

from .mixins import ExtensibleForm, SchoolTermRelatedExtensibleForm
from .models import (
    AdditionalField,
    Announcement,
    DashboardWidget,
    Group,
    GroupType,
    Person,
    SchoolTerm,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .util.core_helpers import get_site_preferences


class PersonAccountForm(forms.ModelForm):
    """Form to assign user accounts to persons in the frontend."""

    class Meta:
        model = Person
        fields = ["last_name", "first_name", "user"]
        widgets = {"user": Select2Widget(attrs={"class": "browser-default"})}

    new_user = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields displayed only for informational purposes
        self.fields["first_name"].disabled = True
        self.fields["last_name"].disabled = True

    def clean(self) -> None:
        user = get_user_model()

        if self.cleaned_data.get("new_user", None):
            if self.cleaned_data.get("user", None):
                # The user selected both an existing user and provided a name to create a new one
                self.add_error(
                    "new_user",
                    _("You cannot set a new username when also selecting an existing user."),
                )
            elif user.objects.filter(username=self.cleaned_data["new_user"]).exists():
                # The user tried to create a new user with the name of an existing user
                self.add_error("new_user", _("This username is already in use."))
            else:
                # Create new User object and assign to form field for existing user
                new_user_obj = user.objects.create_user(
                    self.cleaned_data["new_user"],
                    self.instance.email,
                    first_name=self.instance.first_name,
                    last_name=self.instance.last_name,
                )

                self.cleaned_data["user"] = new_user_obj


# Formset for batch-processing of assignments of users to persons
PersonsAccountsFormSet = forms.modelformset_factory(
    Person, form=PersonAccountForm, max_num=0, extra=0
)


class EditPersonForm(ExtensibleForm):
    """Form to edit an existing person object in the frontend."""

    layout = Layout(
        Fieldset(
            _("Base data"),
            "short_name",
            Row("user", "primary_group"),
            "is_active",
            Row("first_name", "additional_name", "last_name"),
        ),
        Fieldset(_("Address"), Row("street", "housenumber"), Row("postal_code", "place")),
        Fieldset(_("Contact data"), "email", Row("phone_number", "mobile_number")),
        Fieldset(
            _("Advanced personal data"), Row("sex", "date_of_birth"), Row("photo"), "guardians",
        ),
    )

    class Meta:
        model = Person
        fields = [
            "user",
            "is_active",
            "first_name",
            "last_name",
            "additional_name",
            "short_name",
            "street",
            "housenumber",
            "postal_code",
            "place",
            "phone_number",
            "mobile_number",
            "email",
            "date_of_birth",
            "sex",
            "photo",
            "guardians",
            "primary_group",
        ]
        widgets = {
            "user": Select2Widget(attrs={"class": "browser-default"}),
            "primary_group": ModelSelect2Widget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "guardians": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }

    new_user = forms.CharField(
        required=False, label=_("New user"), help_text=_("Create a new account")
    )

    def clean(self) -> None:
        # Use code implemented in dedicated form to verify user selection
        return PersonAccountForm.clean(self)


class EditGroupForm(SchoolTermRelatedExtensibleForm):
    """Form to edit an existing group in the frontend."""

    layout = Layout(
        Fieldset(_("School term"), "school_term"),
        Fieldset(_("Common data"), "name", "short_name", "group_type"),
        Fieldset(_("Persons"), "members", "owners", "parent_groups"),
        Fieldset(_("Additional data"), "additional_fields"),
    )

    class Meta:
        model = Group
        exclude = []
        widgets = {
            "members": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "owners": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "parent_groups": ModelSelect2MultipleWidget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "additional_fields": ModelSelect2MultipleWidget(
                search_fields=["title__icontains",],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class AnnouncementForm(ExtensibleForm):
    """Form to create or edit an announcement in the frontend."""

    valid_from = forms.DateTimeField(required=False)
    valid_until = forms.DateTimeField(required=False)

    valid_from_date = forms.DateField(label=_("Date"))
    valid_from_time = forms.TimeField(label=_("Time"))

    valid_until_date = forms.DateField(label=_("Date"))
    valid_until_time = forms.TimeField(label=_("Time"))

    persons = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        label=_("Persons"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=None,
        label=_("Groups"),
        required=False,
        widget=ModelSelect2MultipleWidget(
            search_fields=["name__icontains", "short_name__icontains",],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )

    layout = Layout(
        Fieldset(
            _("From when until when should the announcement be displayed?"),
            Row("valid_from_date", "valid_from_time", "valid_until_date", "valid_until_time"),
        ),
        Fieldset(_("Who should see the announcement?"), Row("groups", "persons")),
        Fieldset(_("Write your announcement:"), "title", "description"),
    )

    def __init__(self, *args, **kwargs):
        if "instance" not in kwargs:
            # Default to today and whole day for new announcements
            kwargs["initial"] = {
                "valid_from_date": datetime.now(),
                "valid_from_time": time(0, 0),
                "valid_until_date": datetime.now(),
                "valid_until_time": time(23, 59),
            }
        else:
            announcement = kwargs["instance"]

            # Fill special fields from given announcement instance
            kwargs["initial"] = {
                "valid_from_date": announcement.valid_from.date(),
                "valid_from_time": announcement.valid_from.time(),
                "valid_until_date": announcement.valid_until.date(),
                "valid_until_time": announcement.valid_until.time(),
                "groups": announcement.get_recipients_for_model(Group),
                "persons": announcement.get_recipients_for_model(Person),
            }

        super().__init__(*args, **kwargs)

        self.fields["groups"].queryset = Group.objects.for_current_school_term_or_all()

    def clean(self):
        data = super().clean()

        # Combine date and time fields into datetime objects
        valid_from = datetime.combine(data["valid_from_date"], data["valid_from_time"])
        valid_until = datetime.combine(data["valid_until_date"], data["valid_until_time"])

        # Sanity check validity range
        if valid_until < datetime.now():
            raise ValidationError(
                _("You are not allowed to create announcements which are only valid in the past.")
            )
        elif valid_from > valid_until:
            raise ValidationError(
                _("The from date and time must be earlier then the until date and time.")
            )

        # Inject real time data if all went well
        data["valid_from"] = valid_from
        data["valid_until"] = valid_until

        # Ensure at least one group or one person is set as recipient
        if "groups" not in data and "persons" not in data:
            raise ValidationError(_("You need at least one recipient."))

        # Unwrap all recipients into single user objects and generate final list
        data["recipients"] = []
        data["recipients"] += data.get("groups", [])
        data["recipients"] += data.get("persons", [])

        return data

    def save(self, _=False):
        # Save announcement, respecting data injected in clean()
        if self.instance is None:
            self.instance = Announcement()
        self.instance.valid_from = self.cleaned_data["valid_from"]
        self.instance.valid_until = self.cleaned_data["valid_until"]
        self.instance.title = self.cleaned_data["title"]
        self.instance.description = self.cleaned_data["description"]
        self.instance.save()

        # Save recipients
        self.instance.recipients.all().delete()
        for recipient in self.cleaned_data["recipients"]:
            self.instance.recipients.create(recipient=recipient)
        self.instance.save()

        return self.instance

    class Meta:
        model = Announcement
        exclude = []


class ChildGroupsForm(forms.Form):
    """Inline form for group editing to select child groups."""

    child_groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())


class SitePreferenceForm(PreferenceForm):
    """Form to edit site preferences."""

    registry = site_preferences_registry


class PersonPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for one person."""

    registry = person_preferences_registry


class GroupPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for members of a group."""

    registry = group_preferences_registry


class EditAdditionalFieldForm(forms.ModelForm):
    """Form to manage additional fields."""

    class Meta:
        model = AdditionalField
        exclude = []


class EditGroupTypeForm(forms.ModelForm):
    """Form to manage group types."""

    class Meta:
        model = GroupType
        exclude = []


class SchoolTermForm(ExtensibleForm):
    """Form for managing school years."""

    layout = Layout("name", Row("date_start", "date_end"))

    class Meta:
        model = SchoolTerm
        exclude = []


class DashboardWidgetOrderForm(ExtensibleForm):
    pk = forms.ModelChoiceField(
        queryset=DashboardWidget.objects.all(),
        widget=forms.HiddenInput(attrs={"class": "pk-input"}),
    )
    order = forms.IntegerField(initial=0, widget=forms.HiddenInput(attrs={"class": "order-input"}))

    class Meta:
        model = DashboardWidget
        fields = []


DashboardWidgetOrderFormSet = forms.formset_factory(
    form=DashboardWidgetOrderForm, max_num=0, extra=0
)


class InvitationCodeForm(forms.Form):
    """Form to enter an invitation code."""

    code = forms.CharField(
        label=_("Invitation code"), help_text=_("Please enter your invitation code."),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Calculate number of fields
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        blocks = [packet_size,] * length

        self.fields["code"].widget = CleaveWidget(blocks=blocks, delimiter="-", uppercase=True)


class AccountRegisterForm(SignupForm, ExtensibleForm):
    """Form to register new user accounts."""

    class Meta:
        model = Person
        fields = []

    layout = Layout(
        Fieldset(_("Base data"), Row("first_name", "last_name"),),
        Fieldset(
            _("Account data"), "username", Row("email", "email2"), Row("password1", "password2"),
        ),
        Fieldset(_("Consents"), Row("privacy_policy"),),
    )

    def __init__(self, *args, **kwargs):
        super(AccountRegisterForm, self).__init__(*args, **kwargs)
        self.fields["password1"] = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

        privacy_policy = get_site_preferences()["footer__privacy_url"]

        if settings.SIGNUP_PASSWORD_ENTER_TWICE:
            self.fields["password2"] = forms.CharField(
                label=_("Password (again)"), widget=forms.PasswordInput
            )

        self.fields["first_name"] = forms.CharField(
            required=True, widget=forms.TextInput(attrs={"placeholder": _("First name"),})
        )

        self.fields["last_name"] = forms.CharField(
            required=True, widget=forms.TextInput(attrs={"placeholder": _("Last name"),})
        )

        self.fields["privacy_policy"] = forms.BooleanField(
            label=_("I have read the Privacy policy and agree with them."),
            help_text=_(f"<a href='{privacy_policy}'>Privacy policy</a>"),
            required=True,
        )

    def clean(self):
        super(AccountRegisterForm, self).clean()

        dummy_user = get_user_model()
        password = self.cleaned_data.get("password1")
        if password:
            try:
                get_adapter().clean_password(password, user=dummy_user)
            except forms.ValidationError as e:
                self.add_error("password1", e)

        if (
            settings.SIGNUP_PASSWORD_ENTER_TWICE
            and "password1" in self.cleaned_data
            and "password2" in self.cleaned_data
        ):
            if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
                self.add_error(
                    "password2", _("You must type the same password each time."),
                )
        return self.cleaned_data

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class ActionForm(forms.Form):
    """Generic form for executing actions on multiple items of a queryset.

    This should be used together with a ``Table`` from django-tables2
    which includes a ``SelectColumn``.

    The queryset can be defined in two different ways:
    You can use ``get_queryset`` or provide ``queryset`` as keyword argument
    at the initialization of this form class.
    If both are declared, it will use the keyword argument.

    Any actions can be defined using the ``actions`` class attribute
    or overriding the method ``get_actions``.
    The actions use the same syntax like the Django Admin actions with one important difference:
    Instead of the related model admin,
    these actions will get the related ``ActionForm`` as first argument.
    Here you can see an example for such an action:

    .. code-block:: python

        from django.utils.translation import gettext as _

        def example_action(form, request, queryset):
            # Do something with this queryset

        example_action.short_description = _("Example action")

    If you can include the ``ActionForm`` like any other form in your views,
    but you must add the request as first argument.
    When the form is valid, you should run ``execute``:

    .. code-block:: python

        from aleksis.core.forms import ActionForm

        def your_view(request, ...):
            # Something
            action_form = ActionForm(request, request.POST or None, ...)
            if request.method == "POST" and form.is_valid():
                form.execute()

            # Something
    """

    layout = Layout("action")
    actions = []

    def get_actions(self) -> Sequence[Callable]:
        """Get all defined actions."""
        return self.actions

    def _get_actions_dict(self) -> Dict[str, Callable]:
        """Get all defined actions as dictionary."""
        return {value.__name__: value for value in self.get_actions()}

    def _get_action_choices(self) -> List[Tuple[str, str]]:
        """Get all defined actions as Django choices."""
        return [
            (value.__name__, getattr(value, "short_description", value.__name__))
            for value in self.get_actions()
        ]

    def get_queryset(self) -> QuerySet:
        """Get the related queryset."""
        raise NotImplementedError("Queryset necessary.")

    action = forms.ChoiceField(choices=[])
    selected_objects = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, request: HttpRequest, *args, queryset: QuerySet = None, **kwargs):
        self.request = request
        self.queryset = queryset if isinstance(queryset, QuerySet) else self.get_queryset()
        super().__init__(*args, **kwargs)
        self.fields["selected_objects"].queryset = self.queryset
        self.fields["action"].choices = self._get_action_choices()

    def execute(self) -> bool:
        """Execute the selected action on all selected objects.

        :return: If the form is not valid, it will return ``False``.
        """
        if self.is_valid():
            data = self.cleaned_data["selected_objects"]
            action = self._get_actions_dict()[self.cleaned_data["action"]]
            action(None, self.request, data)
            return True
        return False


class ListActionForm(ActionForm):
    """Generic form for executing actions on multiple items of a list of dictionaries.

    Sometimes you want to implement actions for data from different sources
    than querysets or even querysets from multiple models. For these cases,
    you can use this form.

    To provide an unique identification of each item, the dictionaries **must**
    include the attribute ``pk``. This attribute has to be unique for the whole list.
    If you don't mind this aspect, this will cause unexpected behavior.

    Any actions can be defined as described in ``ActionForm``, but, of course,
    the last argument won't be a queryset but a list of dictionaries.

    For further information on usage, you can take a look at ``ActionForm``.
    """

    selected_objects = forms.MultipleChoiceField(choices=[])

    def get_queryset(self):
        # Return None in order not to raise an unwanted exception
        return None

    def _get_dict(self) -> Dict[str, dict]:
        """Get the items sorted by pk attribute."""
        return {item["pk"]: item for item in self.items}

    def _get_choices(self) -> List[Tuple[str, str]]:
        """Get the items as Django choices."""
        return [(item["pk"], item["pk"]) for item in self.items]

    def _get_real_items(self, items: Sequence[dict]) -> List[dict]:
        """Get the real dictionaries from a list of pks."""
        items_dict = self._get_dict()
        real_items = []
        for item in items:
            if item not in items_dict:
                raise ValidationError(_("No valid selection."))
            real_items.append(items_dict[item])
        return real_items

    def clean_selected_objects(self) -> List[dict]:
        data = self.cleaned_data["selected_objects"]
        items = self._get_real_items(data)
        return items

    def __init__(self, request: HttpRequest, items, *args, **kwargs):
        self.items = items
        super().__init__(request, *args, **kwargs)
        self.fields["selected_objects"].choices = self._get_choices()
