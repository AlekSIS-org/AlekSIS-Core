import dbsettings
from django.db import models


class KanboardSettings(dbsettings.Group):
    # term = dbsettings.IntegerValue(widget=forms.Select, choices=choices)
    api_token = dbsettings.StringValue("API token")
    kb_project_id_rebus = dbsettings.PositiveIntegerValue("Project ID for REBUS tasks")
    kb_project_id_feedback = dbsettings.PositiveIntegerValue("Project ID for feedback tasks")


class MailSettings(dbsettings.Group):
    mail_rebus = dbsettings.EmailValue("Email address for REBUS")
    mail_feedback = dbsettings.EmailValue("Email address for Feedback")

class Support(models.Model):
    class Meta:
        permissions = (
            ('use_rebus', 'Can use REBUS'),
            ('send_feedback', 'Can send feedback')
        )


kanboard_settings = KanboardSettings("Kanboard")
mail_settings = MailSettings("Mail adresses")
