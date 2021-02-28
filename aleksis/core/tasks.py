from django.conf import settings
from django.core import management

from .celery import app
from .util.notifications import send_notification as _send_notification


@app.task
def send_notification(notification: int, resend: bool = False) -> None:
    """Send a notification object to its recipient.

    :param notification: primary key of the notification object to send
    :param resend: Define whether to also send if the notification was already sent
    """
    _send_notification(notification, resend)


@app.task
def backup_data() -> None:
    """Backup database and media using django-dbbackup."""
    # Assemble command-line options for dbbackup management command
    db_options = []
    if settings.DBBACKUP_COMPRESS_DB:
        db_options.append("-z")
    if settings.DBBACKUP_ENCRYPT_DB:
        db_options.append("-e")
    if settings.DBBACKUP_CLEANUP_DB:
        db_options.append("-c")

    media_options = []
    if settings.DBBACKUP_COMPRESS_MEDIA:
        media_options.append("-z")
    if settings.DBBACKUP_ENCRYPT_MEDIA:
        media_options.append("-e")
    if settings.DBBACKUP_CLEANUP_MEDIA:
        media_options.append("-c")

    # Hand off to dbbackup's management commands
    management.call_command("dbbackup", *db_options)
    management.call_command("mediabackup", *media_options)
