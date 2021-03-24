# flake8: noqa: DJ01

from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional, Sequence, Union

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group as DjangoGroup
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models, transaction
from django.db.models import QuerySet
from django.dispatch import receiver
from django.forms.widgets import Media
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import jsonstore
from cache_memoize import cache_memoize
from dynamic_preferences.models import PerInstancePreferenceModel
from invitations import signals
from invitations.adapters import get_invitations_adapter
from invitations.base_invitation import AbstractBaseInvitation
from invitations.models import Invitation
from model_utils import FieldTracker
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
from polymorphic.models import PolymorphicModel

from aleksis.core.data_checks import DataCheck, DataCheckRegistry

from .managers import (
    CurrentSiteManagerWithoutMigrations,
    GroupManager,
    GroupQuerySet,
    SchoolTermQuerySet,
)
from .mixins import (
    ExtensibleModel,
    GlobalPermissionModel,
    PureDjangoModel,
    SchoolTermRelatedExtensibleModel,
)
from .tasks import send_notification
from .util.core_helpers import generate_random_code, get_site_preferences, now_tomorrow
from .util.model_helpers import ICONS

FIELD_CHOICES = (
    ("BooleanField", _("Boolean (Yes/No)")),
    ("CharField", _("Text (one line)")),
    ("DateField", _("Date")),
    ("DateTimeField", _("Date and time")),
    ("DecimalField", _("Decimal number")),
    ("EmailField", _("E-mail address")),
    ("IntegerField", _("Integer")),
    ("GenericIPAddressField", _("IP address")),
    ("NullBooleanField", _("Boolean or empty (Yes/No/Neither)")),
    ("TextField", _("Text (multi-line)")),
    ("TimeField", _("Time")),
    ("URLField", _("URL / Link")),
)


class SchoolTerm(ExtensibleModel):
    """School term model.

    This is used to manage start and end times of a school term and link data to it.
    """

    objects = CurrentSiteManagerWithoutMigrations.from_queryset(SchoolTermQuerySet)()

    name = models.CharField(verbose_name=_("Name"), max_length=255, unique=True)

    date_start = models.DateField(verbose_name=_("Start date"))
    date_end = models.DateField(verbose_name=_("End date"))

    @classmethod
    @cache_memoize(3600)
    def get_current(cls, day: Optional[date] = None):
        if not day:
            day = timezone.now().date()
        try:
            return cls.objects.on_day(day).first()
        except SchoolTerm.DoesNotExist:
            return None

    @classproperty
    def current(cls):
        return cls.get_current()

    def clean(self):
        """Ensure there is only one school term at each point of time."""
        if self.date_end < self.date_start:
            raise ValidationError(_("The start date must be earlier than the end date."))

        qs = SchoolTerm.objects.within_dates(self.date_start, self.date_end)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                _("There is already a school term for this time or a part of this time.")
            )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("School term")
        verbose_name_plural = _("School terms")


class Person(ExtensibleModel):
    """Person model.

    A model describing any person related to a school, including, but not
    limited to, students, teachers and guardians (parents).
    """

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        permissions = (
            ("view_address", _("Can view address")),
            ("view_contact_details", _("Can view contact details")),
            ("view_photo", _("Can view photo")),
            ("view_person_groups", _("Can view persons groups")),
            ("view_personal_details", _("Can view personal details")),
        )

    icon_ = "person"

    SEX_CHOICES = [("f", _("female")), ("m", _("male"))]

    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="person",
        verbose_name=_("Linked user"),
    )
    is_active = models.BooleanField(verbose_name=_("Is person active?"), default=True)

    first_name = models.CharField(verbose_name=_("First name"), max_length=255)
    last_name = models.CharField(verbose_name=_("Last name"), max_length=255)
    additional_name = models.CharField(
        verbose_name=_("Additional name(s)"), max_length=255, blank=True
    )

    short_name = models.CharField(
        verbose_name=_("Short name"), max_length=255, blank=True, null=True, unique=True  # noqa
    )

    street = models.CharField(verbose_name=_("Street"), max_length=255, blank=True)
    housenumber = models.CharField(verbose_name=_("Street number"), max_length=255, blank=True)
    postal_code = models.CharField(verbose_name=_("Postal code"), max_length=255, blank=True)
    place = models.CharField(verbose_name=_("Place"), max_length=255, blank=True)

    phone_number = PhoneNumberField(verbose_name=_("Home phone"), blank=True)
    mobile_number = PhoneNumberField(verbose_name=_("Mobile phone"), blank=True)

    email = models.EmailField(verbose_name=_("E-mail address"), blank=True)

    date_of_birth = models.DateField(verbose_name=_("Date of birth"), blank=True, null=True)
    sex = models.CharField(verbose_name=_("Sex"), max_length=1, choices=SEX_CHOICES, blank=True)

    photo = models.ImageField(verbose_name=_("Photo"), blank=True, null=True)

    guardians = models.ManyToManyField(
        "self",
        verbose_name=_("Guardians / Parents"),
        symmetrical=False,
        related_name="children",
        blank=True,
    )

    primary_group = models.ForeignKey(
        "Group", models.SET_NULL, null=True, blank=True, verbose_name=_("Primary group")
    )

    description = models.TextField(verbose_name=_("Description"), blank=True)

    def get_absolute_url(self) -> str:
        return reverse("person_by_id", args=[self.id])

    @property
    def primary_group_short_name(self) -> Optional[str]:
        """Return the short_name field of the primary group related object."""
        if self.primary_group:
            return self.primary_group.short_name

    @primary_group_short_name.setter
    def primary_group_short_name(self, value: str) -> None:
        """
        Set the primary group related object by a short name.

        It uses the first existing group
        with this short name it can find, creating one
        if it can't find one.
        """
        group, created = Group.objects.get_or_create(short_name=value, defaults={"name": value})
        self.primary_group = group

    @property
    def full_name(self) -> str:
        """Full name of person in last name, first name order."""
        return f"{self.last_name}, {self.first_name}"

    @property
    def addressing_name(self) -> str:
        """Full name of person in format configured for addressing."""
        if self.preferences["notification__addressing_name_format"] == "last_first":
            return f"{self.last_name}, {self.first_name}"
        elif self.preferences["notification__addressing_name_format"] == "first_last":
            return f"{self.first_name} {self.last_name}"

    @property
    def mail_sender(self) -> str:
        """E-mail sender in "Name <email>" format."""
        return f'"{self.addressing_name}" <{self.email}>'

    @property
    def mail_sender_via(self) -> str:
        """E-mail sender for via addresses, in "Name via Site <email>" format."""
        site_mail = get_site_preferences()["mail__address"]
        site_name = get_site_preferences()["general__title"]

        return f'"{self.addressing_name} via {site_name}" <{site_mail}>'

    @property
    def age(self):
        """Age of the person at current time."""
        return self.age_at(timezone.now().date())

    def age_at(self, today):
        if self.date_of_birth:
            years = today.year - self.date_of_birth.year
            if self.date_of_birth.month > today.month or (
                self.date_of_birth.month == today.month and self.date_of_birth.day > today.day
            ):
                years -= 1
            return years

    @property
    def dashboard_widgets(self):
        return [
            w.widget
            for w in DashboardWidgetOrder.objects.filter(person=self, widget__active=True).order_by(
                "order"
            )
        ]

    @property
    def unread_notifications(self) -> QuerySet:
        """Get all unread notifications for this person."""
        return self.notifications.filter(read=False)

    @property
    def unread_notifications_count(self) -> int:
        """Return the count of unread notifications for this person."""
        return self.unread_notifications.count()

    user_info_tracker = FieldTracker(fields=("first_name", "last_name", "email"))

    def save(self, *args, **kwargs):
        # Determine all fields that were changed since last load
        dirty = self.pk is None or bool(self.user_info_tracker.changed())

        super().save(*args, **kwargs)

        if self.user and dirty:
            # Synchronise user fields to linked User object to keep it up to date
            self.user.first_name = self.first_name
            self.user.last_name = self.last_name
            self.user.email = self.email
            self.user.save()

        # Select a primary group if none is set
        self.auto_select_primary_group()

    def __str__(self) -> str:
        return self.full_name

    @classmethod
    def maintain_default_data(cls):
        # Ensure we have an admin user
        user = get_user_model()
        if not user.objects.filter(is_superuser=True).exists():
            admin = user.objects.create_superuser(**settings.AUTH_INITIAL_SUPERUSER)
            admin.save()

    def auto_select_primary_group(
        self, pattern: Optional[str] = None, field: Optional[str] = None, force: bool = False
    ) -> None:
        """Auto-select the primary group among the groups the person is member of.

        Uses either the pattern passed as argument, or the pattern configured system-wide.

        Does not do anything if either no pattern is defined or the user already has
        a primary group, unless force is True.
        """
        pattern = pattern or get_site_preferences()["account__primary_group_pattern"]
        field = field or get_site_preferences()["account__primary_group_field"]

        if pattern:
            if force or not self.primary_group:
                self.primary_group = self.member_of.filter(**{f"{field}__regex": pattern}).first()


class DummyPerson(Person):
    """A dummy person that is not stored into the database.

    Used to temporarily inject a Person object into a User.
    """

    class Meta:
        managed = False
        proxy = True

    is_dummy = True

    def save(self, *args, **kwargs):
        # Do nothing, not even call Model's save(), so this is never persisted
        pass


class AdditionalField(ExtensibleModel):
    """An additional field that can be linked to a group."""

    title = models.CharField(verbose_name=_("Title of field"), max_length=255)
    field_type = models.CharField(
        verbose_name=_("Type of field"), choices=FIELD_CHOICES, max_length=50
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = _("Addtitional field for groups")
        verbose_name_plural = _("Addtitional fields for groups")


class Group(SchoolTermRelatedExtensibleModel):
    """Group model.

    Any kind of group of persons in a school, including, but not limited
    classes, clubs, and the like.
    """

    objects = GroupManager.from_queryset(GroupQuerySet)()

    class Meta:
        ordering = ["short_name", "name"]
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        permissions = (
            ("assign_child_groups_to_groups", _("Can assign child groups to groups")),
            ("view_group_stats", _("Can view statistics about group.")),
        )
        constraints = [
            models.UniqueConstraint(fields=["school_term", "name"], name="unique_school_term_name"),
            models.UniqueConstraint(
                fields=["school_term", "short_name"], name="unique_school_term_short_name"
            ),
        ]

    icon_ = "group"

    name = models.CharField(verbose_name=_("Long name"), max_length=255)
    short_name = models.CharField(
        verbose_name=_("Short name"), max_length=255, blank=True, null=True  # noqa
    )

    members = models.ManyToManyField(
        "Person",
        related_name="member_of",
        blank=True,
        through="PersonGroupThrough",
        verbose_name=_("Members"),
    )
    owners = models.ManyToManyField(
        "Person", related_name="owner_of", blank=True, verbose_name=_("Owners")
    )

    parent_groups = models.ManyToManyField(
        "self",
        related_name="child_groups",
        symmetrical=False,
        verbose_name=_("Parent groups"),
        blank=True,
    )

    group_type = models.ForeignKey(
        "GroupType",
        on_delete=models.SET_NULL,
        related_name="type",
        verbose_name=_("Type of group"),
        null=True,
        blank=True,
    )
    additional_fields = models.ManyToManyField(
        AdditionalField, verbose_name=_("Additional fields"), blank=True
    )

    def get_absolute_url(self) -> str:
        return reverse("group_by_id", args=[self.id])

    @property
    def announcement_recipients(self):
        """Flat list of all members and owners to fulfill announcement API contract."""
        return list(self.members.all()) + list(self.owners.all())

    @property
    def get_group_stats(self) -> dict:
        """ Get stats about a given group """
        stats = {}

        stats["members"] = len(self.members.all())

        ages = [person.age for person in self.members.filter(date_of_birth__isnull=False)]

        if ages:
            stats["age_avg"] = sum(ages) / len(ages)
            stats["age_range_min"] = min(ages)
            stats["age_range_max"] = max(ages)

        return stats

    def __str__(self) -> str:
        if self.school_term:
            return f"{self.name} ({self.short_name}) ({self.school_term})"
        else:
            return f"{self.name} ({self.short_name})"

    group_info_tracker = FieldTracker(fields=("name", "short_name", "members", "owners"))

    def save(self, force: bool = False, *args, **kwargs):
        # Determine state of object in relation to database
        dirty = self.pk is None or bool(self.group_info_tracker.changed())

        super().save(*args, **kwargs)

        if force or dirty:
            # Synchronise group to Django group with same name
            dj_group, _ = DjangoGroup.objects.get_or_create(name=self.name)
            dj_group.user_set.set(
                list(
                    self.members.filter(user__isnull=False)
                    .values_list("user", flat=True)
                    .union(self.owners.filter(user__isnull=False).values_list("user", flat=True))
                )
            )
            dj_group.save()


class PersonGroupThrough(ExtensibleModel):
    """Through table for many-to-many relationship of group members.

    It does not have any fields on its own; these are generated upon instantiation
    by inspecting the additional fields selected for the linked group.
    """

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.group.additional_fields.all():
            field_class = getattr(jsonstore, field.field_type)
            field_name = slugify(field.title).replace("-", "_")
            field_instance = field_class(verbose_name=field.title)
            setattr(self, field_name, field_instance)


@receiver(models.signals.m2m_changed, sender=PersonGroupThrough)
def save_group_on_m2m_changed(
    sender: PersonGroupThrough,
    instance: models.Model,
    action: str,
    reverse: bool,
    model: models.Model,
    pk_set: Optional[set],
    **kwargs,
) -> None:
    """Ensure user and group data is synced to Django's models.

    AlekSIS maintains personal information and group meta-data / membership
    in its Person and Group models. As third-party libraries have no knowledge
    about this, we need to keep django.contrib.auth in sync.

    This signal handler triggers a save of group objects whenever a membership
    changes. The save() code will decide whether to update the Django objects
    or not.
    """
    if action not in ("post_add", "post_remove", "post_clear"):
        # Only trigger once, after the change was applied to the database
        return

    if reverse:
        # Relationship was changed on the Person side, saving all groups
        # that have been touched there
        for group in model.objects.filter(pk__in=pk_set):
            group.save(force=True)
    else:
        # Relationship was changed on the Group side
        instance.save(force=True)


class Activity(ExtensibleModel, TimeStampedModel):
    """Activity of a user to trace some actions done in AlekSIS in displayable form."""

    user = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="activities", verbose_name=_("User")
    )

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"))

    app = models.CharField(max_length=100, verbose_name=_("Application"))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Activity")
        verbose_name_plural = _("Activities")


class Notification(ExtensibleModel, TimeStampedModel):
    """Notification to submit to a user."""

    sender = models.CharField(max_length=100, verbose_name=_("Sender"))
    recipient = models.ForeignKey(
        "Person",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("Recipient"),
    )

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"))
    link = models.URLField(blank=True, verbose_name=_("Link"))

    read = models.BooleanField(default=False, verbose_name=_("Read"))
    sent = models.BooleanField(default=False, verbose_name=_("Sent"))

    def __str__(self):
        return str(self.title)

    def save(self, **kwargs):
        super().save(**kwargs)
        if not self.sent:
            send_notification(self.pk, resend=True)
        self.sent = True
        super().save(**kwargs)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")


class AnnouncementQuerySet(models.QuerySet):
    """Queryset for announcements providing time-based utility functions."""

    def relevant_for(self, obj: Union[models.Model, models.QuerySet]) -> models.QuerySet:
        """Get all relevant announcements.

        Get a QuerySet with all announcements relevant for a certain Model (e.g. a Group)
        or a set of models in a QuerySet.
        """
        if isinstance(obj, models.QuerySet):
            ct = ContentType.objects.get_for_model(obj.model)
            pks = list(obj.values_list("pk", flat=True))
        else:
            ct = ContentType.objects.get_for_model(obj)
            pks = [obj.pk]

        return self.filter(recipients__content_type=ct, recipients__recipient_id__in=pks)

    def at_time(self, when: Optional[datetime] = None) -> models.QuerySet:
        """Get all announcements at a certain time."""
        when = when or timezone.now()

        # Get announcements by time
        announcements = self.filter(valid_from__lte=when, valid_until__gte=when)

        return announcements

    def on_date(self, when: Optional[date] = None) -> models.QuerySet:
        """Get all announcements at a certain date."""
        when = when or timezone.now().date()

        # Get announcements by time
        announcements = self.filter(valid_from__date__lte=when, valid_until__date__gte=when)

        return announcements

    def within_days(self, start: date, stop: date) -> models.QuerySet:
        """Get all announcements valid for a set of days."""
        # Get announcements
        announcements = self.filter(valid_from__date__lte=stop, valid_until__date__gte=start)

        return announcements

    def for_person(self, person: Person) -> List:
        """Get all announcements for one person."""
        # Filter by person
        announcements_for_person = []
        for announcement in self:
            if person in announcement.recipient_persons:
                announcements_for_person.append(announcement)

        return announcements_for_person


class Announcement(ExtensibleModel):
    """Announcement model.

    Persistent announcement to display to groups or persons in various places during a
    specific time range.
    """

    objects = models.Manager.from_queryset(AnnouncementQuerySet)()

    title = models.CharField(max_length=150, verbose_name=_("Title"))
    description = models.TextField(max_length=500, verbose_name=_("Description"), blank=True)
    link = models.URLField(blank=True, verbose_name=_("Link to detailed view"))

    valid_from = models.DateTimeField(
        verbose_name=_("Date and time from when to show"), default=timezone.now
    )
    valid_until = models.DateTimeField(
        verbose_name=_("Date and time until when to show"), default=now_tomorrow,
    )

    @property
    def recipient_persons(self) -> Sequence[Person]:
        """Return a list of Persons this announcement is relevant for."""
        persons = []
        for recipient in self.recipients.all():
            persons += recipient.persons
        return persons

    def get_recipients_for_model(self, obj: Union[models.Model]) -> Sequence[models.Model]:
        """Get all recipients.

        Get all recipients for this announcement
        with a special content type (provided through model)
        """
        ct = ContentType.objects.get_for_model(obj)
        return [r.recipient for r in self.recipients.filter(content_type=ct)]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Announcement")
        verbose_name_plural = _("Announcements")


class AnnouncementRecipient(ExtensibleModel):
    """Announcement recipient model.

    Generalisation of a recipient for an announcement, used to wrap arbitrary
    objects that can receive announcements.

    Contract: Objects to serve as recipient have a property announcement_recipients
    returning a flat list of Person objects.
    """

    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name="recipients"
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    recipient_id = models.PositiveIntegerField()
    recipient = GenericForeignKey("content_type", "recipient_id")

    @property
    def persons(self) -> Sequence[Person]:
        """Return a list of Persons selected by this recipient object.

        If the recipient is a Person, return that object. If not, it returns the list
        from the announcement_recipients field on the target model.
        """
        if isinstance(self.recipient, Person):
            return [self.recipient]
        else:
            return getattr(self.recipient, "announcement_recipients", [])

    def __str__(self):
        return str(self.recipient)

    class Meta:
        verbose_name = _("Announcement recipient")
        verbose_name_plural = _("Announcement recipients")


class DashboardWidget(PolymorphicModel, PureDjangoModel):
    """Base class for dashboard widgets on the index page.

    To implement a widget, add a model that subclasses DashboardWidget, sets the template
    and implements the get_context method to return a dictionary to be passed as context
    to the template.

    If your widget does not add any database fields, you should mark it as a proxy model.

    You can provide a Media meta class with custom JS and CSS files which
    will be added to html head.  For further information on media definition
    see https://docs.djangoproject.com/en/3.0/topics/forms/media/

    Example::

      from django.forms.widgets import Media

      from aleksis.core.models import DashboardWidget

      class MyWidget(DashboardWidget):
          template = "myapp/widget.html"

          def get_context(self, request):
              context = {"some_content": "foo"}
              return context

          class Meta:
              proxy = True

          media = Media(css={
                  'all': ('pretty.css',)
              },
              js=('animations.js', 'actions.js')
          )
    """

    @staticmethod
    def get_media(widgets: Union[QuerySet, Iterable]):
        """Return all media required to render the selected widgets."""
        media = Media()
        for widget in widgets:
            media = media + widget.media
        return media

    template = None
    media = Media()

    title = models.CharField(max_length=150, verbose_name=_("Widget Title"))
    active = models.BooleanField(verbose_name=_("Activate Widget"))

    size_s = models.PositiveSmallIntegerField(
        verbose_name=_("Size on mobile devices"),
        help_text=_("<= 600 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=12,
    )
    size_m = models.PositiveSmallIntegerField(
        verbose_name=_("Size on tablet devices"),
        help_text=_("> 600 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=12,
    )
    size_l = models.PositiveSmallIntegerField(
        verbose_name=_("Size on desktop devices"),
        help_text=_("> 992 px, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=6,
    )
    size_xl = models.PositiveSmallIntegerField(
        verbose_name=_("Size on large desktop devices"),
        help_text=_("> 1200 px>, 12 columns"),
        validators=[MaxValueValidator(12)],
        default=4,
    )

    def get_context(self, request):
        """Get the context dictionary to pass to the widget template."""
        raise NotImplementedError("A widget subclass needs to implement the get_context method.")

    def get_template(self):
        """Get template.

        Get the template to render the widget with. Defaults to the template attribute,
        but can be overridden to allow more complex template generation scenarios.
        """
        return self.template

    def __str__(self):
        return self.title

    class Meta:
        permissions = (("edit_default_dashboard", _("Can edit default dashboard")),)
        verbose_name = _("Dashboard Widget")
        verbose_name_plural = _("Dashboard Widgets")


class ExternalLinkWidget(DashboardWidget):
    template = "core/dashboard_widget/external_link_widget.html"

    url = models.URLField(verbose_name=_("URL"))
    icon_url = models.URLField(verbose_name=_("Icon URL"))

    def get_context(self, request):
        return {"title": self.title, "url": self.url, "icon_url": self.icon_url}

    class Meta:
        verbose_name = _("External link widget")
        verbose_name_plural = _("External link widgets")


class DashboardWidgetOrder(ExtensibleModel):
    widget = models.ForeignKey(
        DashboardWidget, on_delete=models.CASCADE, verbose_name=_("Dashboard widget")
    )
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name=_("Person"), null=True, blank=True
    )
    order = models.PositiveIntegerField(verbose_name=_("Order"))
    default = models.BooleanField(default=False, verbose_name=_("Part of the default dashboard"))

    @classproperty
    def default_dashboard_widgets(cls):
        """Get default order for dashboard widgets."""
        return [
            w.widget
            for w in cls.objects.filter(person=None, default=True, widget__active=True).order_by(
                "order"
            )
        ]

    class Meta:
        verbose_name = _("Dashboard widget order")
        verbose_name_plural = _("Dashboard widget orders")


class CustomMenu(ExtensibleModel):
    """A custom menu to display in the footer."""

    name = models.CharField(max_length=100, verbose_name=_("Menu ID"), unique=True)

    def __str__(self):
        return self.name if self.name != "" else self.id

    @classmethod
    @cache_memoize(3600)
    def get_default(cls, name):
        """Get a menu by name or create if it does not exist."""
        menu, _ = cls.objects.prefetch_related("items").get_or_create(name=name)
        return menu

    class Meta:
        verbose_name = _("Custom menu")
        verbose_name_plural = _("Custom menus")


class CustomMenuItem(ExtensibleModel):
    """Single item in a custom menu."""

    menu = models.ForeignKey(
        CustomMenu, models.CASCADE, verbose_name=_("Menu"), related_name="items"
    )
    name = models.CharField(max_length=150, verbose_name=_("Name"))
    url = models.URLField(verbose_name=_("Link"))
    icon = models.CharField(max_length=50, blank=True, choices=ICONS, verbose_name=_("Icon"))

    def __str__(self):
        return f"[{self.menu}] {self.name}"

    class Meta:
        verbose_name = _("Custom menu item")
        verbose_name_plural = _("Custom menu items")


class GroupType(ExtensibleModel):
    """Group type model.

    Descriptive type of a group; used to tag groups and for apps to distinguish
    how to display or handle a certain group.
    """

    name = models.CharField(verbose_name=_("Title of type"), max_length=50)
    description = models.CharField(verbose_name=_("Description"), max_length=500)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = _("Group type")
        verbose_name_plural = _("Group types")


class GlobalPermissions(GlobalPermissionModel):
    """Container for global permissions."""

    class Meta(GlobalPermissionModel.Meta):
        permissions = (
            ("view_system_status", _("Can view system status")),
            ("link_persons_accounts", _("Can link persons to accounts")),
            ("manage_data", _("Can manage data")),
            ("impersonate", _("Can impersonate")),
            ("search", _("Can use search")),
            ("change_site_preferences", _("Can change site preferences")),
            ("change_person_preferences", _("Can change person preferences")),
            ("change_group_preferences", _("Can change group preferences")),
        )


class SitePreferenceModel(PerInstancePreferenceModel, PureDjangoModel):
    """Preference model to hold pereferences valid for a site."""

    instance = models.ForeignKey(Site, on_delete=models.CASCADE)

    class Meta:
        app_label = "core"


class PersonPreferenceModel(PerInstancePreferenceModel, PureDjangoModel):
    """Preference model to hold pereferences valid for a person."""

    instance = models.ForeignKey(Person, on_delete=models.CASCADE)

    class Meta:
        app_label = "core"


class GroupPreferenceModel(PerInstancePreferenceModel, PureDjangoModel):
    """Preference model to hold pereferences valid for members of a group."""

    instance = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        app_label = "core"


class DataCheckResult(ExtensibleModel):
    """Save the result of a data check for a specific object."""

    check = models.CharField(
        max_length=255,
        verbose_name=_("Related data check task"),
        choices=DataCheckRegistry.data_checks_choices,
    )

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=255)
    related_object = GenericForeignKey("content_type", "object_id")

    solved = models.BooleanField(default=False, verbose_name=_("Issue solved"))
    sent = models.BooleanField(default=False, verbose_name=_("Notification sent"))

    @property
    def related_check(self) -> DataCheck:
        return DataCheckRegistry.data_checks_by_name[self.check]

    def solve(self, solve_option: str = "default"):
        self.related_check.solve(self, solve_option)

    def __str__(self):
        return f"{self.related_object}: {self.related_check.problem_name}"

    class Meta:
        verbose_name = _("Data check result")
        verbose_name_plural = _("Data check results")
        permissions = (
            ("run_data_checks", _("Can run data checks")),
            ("solve_data_problem", _("Can solve data check problems")),
        )


class PersonInvitation(AbstractBaseInvitation, PureDjangoModel):
    """Custom model for invitations to allow to generate invitations codes without email address."""

    email = models.EmailField(verbose_name=_("E-Mail address"), blank=True)

    @classmethod
    def create(cls, email, inviter=None, **kwargs):
        length = get_site_preferences()["auth__invite_code_length"]
        packet_size = get_site_preferences()["auth__invite_code_packet_size"]
        key = generate_random_code(length, packet_size)
        instance = cls._default_manager.create(email=email, key=key, inviter=inviter, **kwargs)
        return instance

    def __str__(self) -> str:
        return _(f"Invitation: {self.email}")

    key_expired = Invitation.key_expired

    send_invitation = Invitation.send_invitation
