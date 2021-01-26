# noqa

from django.contrib import admin

from guardian.admin import GuardedModelAdminMixin
from reversion.admin import VersionAdmin

from .mixins import BaseModelAdmin
from .models import (
    Activity,
    Announcement,
    AnnouncementRecipient,
    CustomMenuItem,
    DataCheckResult,
    Group,
    Notification,
    Person,
)

admin.site.register(Activity, VersionAdmin)
admin.site.register(Notification, VersionAdmin)
admin.site.register(CustomMenuItem, VersionAdmin)


class AnnouncementRecipientInline(admin.StackedInline):
    model = AnnouncementRecipient


class AnnouncementAdmin(BaseModelAdmin, VersionAdmin):
    inlines = [
        AnnouncementRecipientInline,
    ]


class GuardedVersionAdmin(GuardedModelAdminMixin, VersionAdmin):
    pass


admin.site.register(Announcement, AnnouncementAdmin)
admin.site.register(DataCheckResult)
admin.site.register(Person, GuardedVersionAdmin)
admin.site.register(Group, GuardedVersionAdmin)
