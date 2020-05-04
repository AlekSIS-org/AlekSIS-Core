from django.conf import settings
from django.forms import EmailField, ImageField, URLField
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import ChoicePreference, FilePreference, StringPreference

from .registries import person_preferences_registry, site_preferences_registry
from .util.notifications import get_notification_choices_lazy

general = Section("general")
school = Section("school")
theme = Section("theme")
mail = Section("mail")
notification = Section("notification")
footer = Section("footer")
account = Section("account")


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


@site_preferences_registry.register
class ColourSecondary(StringPreference):
    section = theme
    name = "secondary"
    default = "#0d5eaf"
    required = False
    verbose_name = _("Secondary colour")


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