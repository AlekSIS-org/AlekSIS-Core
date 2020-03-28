from datetime import time, datetime
from typing import Optional

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_select2.forms import ModelSelect2MultipleWidget, Select2Widget
from material import Layout, Fieldset, Row

from .mixins import ExtensibleForm
from .models import Group, Person, School, SchoolTerm, Announcement, AnnouncementRecipient


class PersonAccountForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ["last", "first", "user"]
        widgets = {"user": Select2Widget}

    new_user = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first"].disabled = True
        self.fields["last"].disabled = True

    def clean(self) -> None:
        User = get_user_model()

        if self.cleaned_data.get("new_user", None):
            if self.cleaned_data.get("user", None):
                self.add_error(
                    "new_user",
                    _("You cannot set a new username when also selecting an existing user."),
                )
            elif User.objects.filter(username=self.cleaned_data["new_user"]).exists():
                self.add_error("new_user", _("This username is already in use."))
            else:
                new_user_obj = User.objects.create_user(
                    self.cleaned_data["new_user"],
                    self.instance.email,
                    first=self.instance.first,
                    last=self.instance.last,
                )

                self.cleaned_data["user"] = new_user_obj


PersonsAccountsFormSet = forms.modelformset_factory(
    Person, form=PersonAccountForm, max_num=0, extra=0
)


class EditPersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            "user",
            "is_active",
            "first",
            "last",
            "middle",
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
            "photo_cropping",
        ]
        widgets = {"user": Select2Widget}

    new_user = forms.CharField(
        required=False, label=_("New user"), help_text=_("Create a new account")
    )

    def clean(self) -> None:
        User = get_user_model()

        if self.cleaned_data.get("new_user", None):
            if self.cleaned_data.get("user", None):
                self.add_error(
                    "new_user",
                    _("You cannot set a new username when also selecting an existing user."),
                )
            elif User.objects.filter(username=self.cleaned_data["new_user"]).exists():
                self.add_error("new_user", _("This username is already in use."))
            else:
                new_user_obj = User.objects.create_user(
                    self.cleaned_data["new_user"],
                    self.instance.email,
                    first=self.instance.first,
                    last=self.instance.last,
                )

                self.cleaned_data["user"] = new_user_obj


class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["name", "short_name", "members", "owners", "parent_groups"]
        widgets = {
            "members": ModelSelect2MultipleWidget(
                search_fields=[
                    "first__icontains",
                    "last__icontains",
                    "short_name__icontains",
                ]
            ),
            "owners": ModelSelect2MultipleWidget(
                search_fields=[
                    "first__icontains",
                    "last__icontains",
                    "short_name__icontains",
                ]
            ),
            "parent_groups": ModelSelect2MultipleWidget(
                search_fields=["name__icontains", "short_name__icontains"]
            ),
        }


class EditSchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ["name", "name_official", "logo", "logo_cropping"]


class EditTermForm(forms.ModelForm):
    class Meta:
        model = SchoolTerm
        fields = ["caption", "date_start", "date_end"]


class AnnouncementForm(ExtensibleForm):
    valid_from = forms.DateTimeField(required=False)
    valid_until = forms.DateTimeField(required=False)

    valid_from_date = forms.DateField(label=_("Date"))
    valid_from_time = forms.TimeField(label=_("Time"))

    valid_until_date = forms.DateField(label=_("Date"))
    valid_until_time = forms.TimeField(label=_("Time"))

    persons = forms.ModelMultipleChoiceField(Person.objects.all(), label=_("Persons"), required=False)
    groups = forms.ModelMultipleChoiceField(Group.objects.all(), label=_("Groups"), required=False)

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

    def clean(self):
        data = super().clean()

        # Check date and time
        from_date = data["valid_from_date"]
        from_time = data["valid_from_time"]
        until_date = data["valid_until_date"]
        until_time = data["valid_until_time"]

        valid_from = datetime.combine(from_date, from_time)
        valid_until = datetime.combine(until_date, until_time)

        if valid_until < datetime.now():
            raise ValidationError(
                _("You are not allowed to create announcements which are only valid in the past.")
            )
        elif valid_from > valid_until:
            raise ValidationError(
                _("The from date and time must be earlier then the until date and time.")
            )

        data["valid_from"] = valid_from
        data["valid_until"] = valid_until

        # Check recipients
        if "groups" not in data and "persons" not in data:
            raise ValidationError(_("You need at least one recipient."))

        recipients = []
        recipients += data.get("groups", [])
        recipients += data.get("persons", [])

        data["recipients"] = recipients

        return data

    def save(self, _=False):
        # Save announcement
        a = self.instance if self.instance is not None else Announcement()
        a.valid_from = self.cleaned_data["valid_from"]
        a.valid_until = self.cleaned_data["valid_until"]
        a.title = self.cleaned_data["title"]
        a.description = self.cleaned_data["description"]
        a.save()

        # Save recipients
        a.recipients.all().delete()
        for recipient in self.cleaned_data["recipients"]:
            a.recipients.create(recipient=recipient)
        a.save()

        return a

    class Meta:
        model = Announcement
        exclude = []
