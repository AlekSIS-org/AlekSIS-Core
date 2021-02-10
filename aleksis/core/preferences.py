from django.conf import settings
from django.forms import EmailField, ImageField, URLField
from django.forms.widgets import SelectMultiple
from django.utils.translation import gettext_lazy as _

from colorfield.widgets import ColorWidget
from dynamic_preferences.preferences import Section
from dynamic_preferences.types import (
    BooleanPreference,
    ChoicePreference,
    FilePreference,
    IntegerPreference,
    ModelMultipleChoicePreference,
    MultipleChoicePreference,
    StringPreference,
)

from .models import Group, Person
from .registries import person_preferences_registry, site_preferences_registry
from .util.notifications import get_notification_choices_lazy

general = Section("general")
school = Section("school")
theme = Section("theme")
mail = Section("mail")
notification = Section("notification")
footer = Section("footer")
account = Section("account")
auth = Section("auth", verbose_name=_("Authentication"))
internationalisation = Section("internationalisation", verbose_name=_("Internationalisation"))


@site_preferences_registry.register
class SiteTitle(StringPreference):
    section = general
    name = "title"
    default = "AlekSIS"
    required = False
    verbose_name = _("Site title")


@site_preferences_registry.register
class SiteDescription(StringPreference):
    section = general
    name = "description"
    default = "The Free School Information System"
    required = False
    verbose_name = _("Site description")


@site_preferences_registry.register
class ColourPrimary(StringPreference):
    section = theme
    name = "primary"
    default = "#0d5eaf"
    required = False
    verbose_name = _("Primary colour")
    widget = ColorWidget


@site_preferences_registry.register
class ColourSecondary(StringPreference):
    section = theme
    name = "secondary"
    default = "#0d5eaf"
    required = False
    verbose_name = _("Secondary colour")
    widget = ColorWidget


@site_preferences_registry.register
class Logo(FilePreference):
    section = theme
    field_class = ImageField
    name = "logo"
    verbose_name = _("Logo")


@site_preferences_registry.register
class Favicon(FilePreference):
    section = theme
    field_class = ImageField
    name = "favicon"
    verbose_name = _("Favicon")


@site_preferences_registry.register
class PWAIcon(FilePreference):
    section = theme
    field_class = ImageField
    name = "pwa_icon"
    verbose_name = _("PWA-Icon")


@site_preferences_registry.register
class MailOutName(StringPreference):
    section = mail
    name = "name"
    default = "AlekSIS"
    required = False
    verbose_name = _("Mail out name")


@site_preferences_registry.register
class MailOut(StringPreference):
    section = mail
    name = "address"
    default = settings.DEFAULT_FROM_EMAIL
    required = False
    verbose_name = _("Mail out address")
    field_class = EmailField


@site_preferences_registry.register
class PrivacyURL(StringPreference):
    section = footer
    name = "privacy_url"
    default = ""
    required = False
    verbose_name = _("Link to privacy policy")
    field_class = URLField


@site_preferences_registry.register
class ImprintURL(StringPreference):
    section = footer
    name = "imprint_url"
    default = ""
    required = False
    verbose_name = _("Link to imprint")
    field_class = URLField


@person_preferences_registry.register
class AdressingNameFormat(ChoicePreference):
    section = notification
    name = "addressing_name_format"
    default = "first_last"
    required = False
    verbose_name = _("Name format for addressing")
    choices = (
        ("first_last", "John Doe"),
        ("last_fist", "Doe, John"),
    )


@person_preferences_registry.register
class NotificationChannels(ChoicePreference):
    # FIXME should be a MultipleChoicePreference
    section = notification
    name = "channels"
    default = "email"
    required = False
    verbose_name = _("Channels to use for notifications")
    choices = get_notification_choices_lazy()


@site_preferences_registry.register
class PrimaryGroupPattern(StringPreference):
    section = account
    name = "primary_group_pattern"
    default = ""
    required = False
    verbose_name = _("Regular expression to match primary group, e.g. '^Class .*'")


@site_preferences_registry.register
class PrimaryGroupField(ChoicePreference):
    section = account
    name = "primary_group_field"
    default = "name"
    required = False
    verbose_name = _("Field on person to match primary group against")

    def get_choices(self):
        return Person.syncable_fields_choices()


@site_preferences_registry.register
class AutoCreatePerson(BooleanPreference):
    section = account
    name = "auto_create_person"
    default = False
    required = False
    verbose_name = _("Automatically create new persons for new users")


@site_preferences_registry.register
class AutoLinkPerson(BooleanPreference):
    section = account
    name = "auto_link_person"
    default = False
    required = False
    verbose_name = _("Automatically link existing persons to new users by their e-mail address")


@site_preferences_registry.register
class SchoolName(StringPreference):
    section = school
    name = "name"
    default = ""
    required = False
    verbose_name = _("Display name of the school")


@site_preferences_registry.register
class SchoolNameOfficial(StringPreference):
    section = school
    name = "name_official"
    default = ""
    required = False
    verbose_name = _("Official name of the school, e.g. as given by supervisory authority")


@site_preferences_registry.register
class AllowPasswordChange(BooleanPreference):
    section = auth
    name = "allow_password_change"
    default = True
    verbose_name = _("Allow users to change their passwords")


@site_preferences_registry.register
class SignupEnabled(BooleanPreference):
    section = auth
    name = "signup_enabled"
    default = False
    verbose_name = _("Enable signup")


@site_preferences_registry.register
class SignupOpen(BooleanPreference):
    section = auth
    name = "signup_open"
    default = False
    verbose_name = _("Signup open for everyone or invite only.")


@site_preferences_registry.register
class InviteEnabled(BooleanPreference):
    section = auth
    name = "invite_enabled"
    default = False
    verbose_name = _("Enable invitations")


@site_preferences_registry.register
class InviteCodeLength(IntegerPreference):
    section = auth
    name = "invite_code_length"
    default = 3
    verbose_name = _("Length of invite code. (Default 3: abcde-acbde-abcde)")


@site_preferences_registry.register
class InviteCodePacketSize(IntegerPreference):
    section = auth
    name = "invite_code_packet_size"
    default = 5
    verbose_name = _("Size of packets. (Default 5: abcde)")


@site_preferences_registry.register
class InviteDayExpiry(IntegerPreference):
    section = auth
    name = "invite_day_expiry"
    default = 3
    verbose_name = _("Expiration time of invitations in days.")


@site_preferences_registry.register
class AvailableLanguages(MultipleChoicePreference):
    section = internationalisation
    name = "languages"
    default = [code[0] for code in settings.LANGUAGES]
    widget = SelectMultiple
    verbose_name = _("Available languages")
    field_attribute = {"initial": []}
    choices = settings.LANGUAGES


@site_preferences_registry.register
class DataChecksSendEmails(BooleanPreference):
    """Enable email sending if data checks detect problems."""

    section = general
    name = "data_checks_send_emails"
    default = False
    verbose_name = _("Send emails if data checks detect problems")


@site_preferences_registry.register
class DataChecksEmailsRecipients(ModelMultipleChoicePreference):
    """Email recipients for data check problem emails."""

    section = general
    name = "data_checks_recipients"
    default = []
    model = Person
    verbose_name = _("Email recipients for data checks problem emails")


@site_preferences_registry.register
class DataChecksEmailsRecipientGroups(ModelMultipleChoicePreference):
    """Email recipient groups for data check problem emails."""

    section = general
    name = "data_checks_recipient_groups"
    default = []
    model = Group
    verbose_name = _("Email recipient groups for data checks problem emails")
