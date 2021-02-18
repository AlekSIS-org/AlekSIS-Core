from datetime import datetime

from django.conf import settings
from django.utils.translation import gettext as _

from dbbackup import utils as dbbackup_utils
from dbbackup.storage import get_storage
from django_celery_results.models import TaskResult
from health_check.backends import BaseHealthCheckBackend

from aleksis.core.models import DataCheckResult


class DataChecksHealthCheckBackend(BaseHealthCheckBackend):
    """Checks whether there are unresolved data problems."""

    critical_service = False

    def check_status(self):
        if DataCheckResult.objects.filter(solved=False).exists():
            self.add_error(_("There are unresolved data problems."))

    def identifier(self):
        return self.__class__.__name__


class BaseBackupHealthCheck(BaseHealthCheckBackend):
    """Common base class for backup age checks."""

    critical_service = False

    def check_status(self):
        storage = get_storage()
        last_backup = storage.list_backups(content_type=self.content_type)[-1]
        last_backup_time = dbbackup_utils.filename_to_date(last_backup)
        time_gone_since_backup = last_backup_time - datetime.now()

        # Check if backup is older than configured time
        if time_gone_since_backup.seconds > settings.DBBACKUP_SECONDS:
            self.add_error(_(f"Last backup {time_gone_since_backup}!"))


class DbBackupAgeHealthCheck(BaseBackupHealthCheck):
    """Checks if last backup file is less than configured seconds ago."""

    content_type = "db"

    def identifier(self):
        return self.__class__.__name__


class MediaBackupAgeHealthCheck(BaseBackupHealthCheck):
    """Checks if last backup file is less than configured seconds ago."""

    content_type = "media"

    def identifier(self):
        return self.__class__.__name__


class BackupJobHealthCheck(BaseHealthCheckBackend):
    """Checks if last backup file is less than configured seconds ago."""

    critical_service = False

    def check_status(self):
        task = TaskResult.objects.filter(task_name="aleksis.core.tasks.backup_data")

        # Check if state is success
        if not task.last():
            self.add_error(_("No backup result found!"))
        if task.last() and task.last().status != "SUCCESS":
            self.add_error(_(f"{task.last().status} - {task.last().result}"))

    def identifier(self):
        return self.__class__.__name__
