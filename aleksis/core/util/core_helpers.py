import os
import sys
import time
from datetime import datetime, timedelta
from importlib import import_module
from itertools import groupby
from operator import itemgetter
from typing import Any, Callable, Optional, Sequence, Union
from uuid import uuid4

if sys.version_info >= (3, 9):
    from importlib import metadata
else:
    import importlib_metadata as metadata

from django.conf import settings
from django.db import transaction
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import lazy

from cache_memoize import cache_memoize
from django_global_request.middleware import get_request

from aleksis.core.util import messages


def copyright_years(years: Sequence[int], seperator: str = ", ", joiner: str = "–") -> str:
    """Take a sequence of integegers and produces a string with ranges.

    >>> copyright_years([1999, 2000, 2001, 2005, 2007, 2008, 2009])
    '1999–2001, 2005, 2007–2009'
    """
    ranges = [
        list(map(itemgetter(1), group))
        for _, group in groupby(enumerate(years), lambda e: e[1] - e[0])
    ]
    years_strs = [
        str(range_[0]) if len(range_) == 1 else joiner.join([str(range_[0]), str(range_[-1])])
        for range_ in ranges
    ]

    return seperator.join(years_strs)


def dt_show_toolbar(request: HttpRequest) -> bool:
    """Add a helper to determin if Django debug toolbar should be displayed.

    Extends the default behaviour by enabling DJDT for superusers independent
    of source IP.
    """
    from debug_toolbar.middleware import show_toolbar  # noqa

    if not settings.DEBUG:
        return False

    if show_toolbar(request):
        return True
    elif hasattr(request, "user") and request.user.is_superuser:
        return True

    return False


def get_app_packages() -> Sequence[str]:
    """Find all registered apps from the setuptools entrypoint."""
    return [f"{ep.module}.{ep.attr}" for ep in metadata.entry_points().get("aleksis.app", [])]


def merge_app_settings(
    setting: str, original: Union[dict, list], deduplicate: bool = False
) -> Union[dict, list]:
    """Merge app settings.

    Get a named settings constant from all apps and merge it into the original.
    To use this, add a settings.py file to the app, in the same format as Django's
    main settings.py.

    Note: Only selected names will be imported frm it to minimise impact of
    potentially malicious apps!
    """
    for app in get_app_packages():
        pkg = ".".join(app.split(".")[:-2])
        mod_settings = None
        while "." in pkg:
            try:
                mod_settings = import_module(pkg + ".settings")
            except ImportError:
                # Import errors are non-fatal.
                pkg = ".".join(pkg.split(".")[:-1])
                continue
            break
        if not mod_settings:
            # The app does not have settings
            continue

        app_setting = getattr(mod_settings, setting, None)
        if not app_setting:
            # The app might not have this setting or it might be empty. Ignore it in that case.
            continue

        for entry in app_setting:
            if entry in original:
                if not deduplicate:
                    raise AttributeError(f"{entry} already set in original.")
            else:
                if isinstance(original, list):
                    original.append(entry)
                elif isinstance(original, dict):
                    original[entry] = app_setting[entry]
                else:
                    raise TypeError("Only dict and list settings can be merged.")


def get_site_preferences():
    """Get the preferences manager of the current site."""
    from django.contrib.sites.models import Site  # noqa

    return Site.objects.get_current().preferences


def lazy_preference(section: str, name: str) -> Callable[[str, str], Any]:
    """Lazily get a config value from dynamic preferences.

    Useful to bind preferences
    to other global settings to make them available to third-party apps that are not
    aware of dynamic preferences.
    """

    def _get_preference(section: str, name: str) -> Any:
        return get_site_preferences()[f"{section}__{name}"]

    # The type is guessed from the default value to improve lazy()'s behaviour
    # FIXME Reintroduce the behaviour described above
    return lazy(_get_preference, str)(section, name)


def lazy_get_favicon_url(
    title: str, size: int, rel: str, default: Optional[str] = None
) -> Callable[[str, str], Any]:
    """Lazily get the URL to a favicon image."""

    @cache_memoize(3600)
    def _get_favicon_url(size: int, rel: str) -> Any:
        from favicon.models import Favicon  # noqa

        try:
            favicon = Favicon.on_site.get(title=title)
        except Favicon.DoesNotExist:
            return default
        else:
            return favicon.get_favicon(size, rel).faviconImage.url

    return lazy(_get_favicon_url, str)(size, rel)


def is_impersonate(request: HttpRequest) -> bool:
    """Check whether the user was impersonated by an admin."""
    if hasattr(request, "user"):
        return getattr(request.user, "is_impersonate", False)
    else:
        return False


def has_person(obj: Union[HttpRequest, Model]) -> bool:
    """Check wehether a model object has a person attribute linking it to a Person object.

    The passed object can also be a HttpRequest object, in which case its
    associated User object is unwrapped and tested.
    """
    if isinstance(obj, HttpRequest):
        if hasattr(obj, "user"):
            obj = obj.user
        else:
            return False

    if obj.is_anonymous:
        return False

    person = getattr(obj, "person", None)
    if person is None:
        return False
    elif getattr(person, "is_dummy", False):
        return False
    else:
        return True


def is_celery_enabled():
    """Check whether celery support is enabled."""
    return hasattr(settings, "CELERY_RESULT_BACKEND")


def celery_optional(orig: Callable) -> Callable:
    """Add a decorator that makes Celery optional for a function.

    If Celery is configured and available, it wraps the function in a Task
    and calls its delay method when invoked; if not, it leaves it untouched
    and it is executed synchronously.

    The wrapped function returns a tuple with either
    the return value of the task's delay method and False
    if the method has been executed asynchronously
    or the return value of the executed method and True
    if the method has been executed synchronously.
    """
    if is_celery_enabled():
        from ..celery import app  # noqa

        task = app.task(orig)

    def wrapped(*args, **kwargs):
        if is_celery_enabled():
            return transaction.on_commit(lambda: task.delay(*args, **kwargs)), False
        else:
            return orig(*args, **kwargs), True

    return wrapped


class DummyRecorder:
    def set_progress(self, *args, **kwargs):
        pass

    def add_message(self, level: int, message: str, **kwargs) -> Optional[Any]:
        request = get_request()
        return messages.add_message(request, level, message, **kwargs)


def celery_optional_progress(orig: Callable) -> Callable:
    """Add a decorator that makes Celery with progress bar support optional for a function.

    If Celery is configured and available, it wraps the function in a Task
    and calls its delay method when invoked; if not, it leaves it untouched
    and it is executed synchronously.

    Additionally, it adds a recorder class as first argument
    (`ProgressRecorder` if Celery is enabled, else `DummyRecoder`).

    This recorder provides the functions `set_progress` and `add_message`
    which can be used to track the status of the task.
    For further information, see the respective recorder classes.

    How to use
    ----------
    1. Write a function and include tracking methods

    ::

        from django.contrib import messages

        from aleksis.core.util.core_helpers import celery_optional_progress

        @celery_optional_progress
        def do_something(recorder: Union[ProgressRecorder, DummyRecorder], foo, bar, baz=None):
            # ...
            recorder.total = len(list_with_data)

            for i, item in list_with_data:
                # ...
                recorder.set_progress(i + 1)
                # ...

            recorder.add_message(messages.SUCCESS, "All data were imported successfully.")

    2. Track process in view:

    ::

        def my_view(request):
            context = {}
            # ...
            result = do_something(foo, bar, baz=baz)

            if result:
                context = {
                    "title": _("Progress: Import data"),
                    "back_url": reverse("index"),
                    "progress": {
                        "task_id": result.task_id,
                        "title": _("Import objects …"),
                        "success": _("The import was done successfully."),
                        "error": _("There was a problem while importing data."),
                    },
                }

                # Render progress view
                return render(request, "core/progress.html", context)

            # Render other view if Celery isn't enabled
            return render(request, "my-app/other-view.html", context)
    """

    def recorder_func(self, *args, **kwargs):
        if is_celery_enabled():
            from .celery_progress import ProgressRecorder  # noqa

            recorder = ProgressRecorder(self)
        else:
            recorder = DummyRecorder()
        orig(recorder, *args, **kwargs)

        # Needed to ensure that all messages are displayed by frontend
        time.sleep(0.7)

    var_name = f"{orig.__module__}.{orig.__name__}"

    if is_celery_enabled():
        from ..celery import app  # noqa

        task = app.task(recorder_func, bind=True, name=var_name)

    def wrapped(*args, **kwargs):
        if is_celery_enabled():
            return task.delay(*args, **kwargs)
        else:
            recorder_func(None, *args, **kwargs)
            return None

    return wrapped


def path_and_rename(instance, filename: str, upload_to: str = "files") -> str:
    """Update path of an uploaded file and renames it to a random UUID in Django FileField."""
    _, ext = os.path.splitext(filename)

    # set filename as random string
    new_filename = f"{uuid4().hex}{ext}"

    # Create upload directory if necessary
    os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_to), exist_ok=True)

    # return the whole path to the file
    return os.path.join(upload_to, new_filename)


def custom_information_processor(request: HttpRequest) -> dict:
    """Provide custom information in all templates."""
    from ..models import CustomMenu

    return {
        "FOOTER_MENU": CustomMenu.get_default("footer"),
        "ALTERNATIVE_LOGIN_VIEWS_LIST": [
            a[0]
            for a in settings.ALTERNATIVE_LOGIN_VIEWS
            if a[0] in settings.AUTHENTICATION_BACKENDS
        ],
        "ALTERNATIVE_LOGIN_VIEWS": [
            a for a in settings.ALTERNATIVE_LOGIN_VIEWS if a[0] in settings.AUTHENTICATION_BACKENDS
        ],
    }


def now_tomorrow() -> datetime:
    """Return current time tomorrow."""
    return timezone.now() + timedelta(days=1)


def objectgetter_optional(
    model: Model, default: Optional[Any] = None, default_eval: bool = False
) -> Callable[[HttpRequest, Optional[int]], Model]:
    """Get an object by pk, defaulting to None."""

    def get_object(request: HttpRequest, id_: Optional[int] = None, **kwargs) -> Model:
        if id_ is not None:
            return get_object_or_404(model, pk=id_)
        else:
            return eval(default) if default_eval else default  # noqa:S307

    return get_object


def handle_uploaded_file(f, filename: str):
    with open(filename, "wb+") as destination:
        for chunk in f.chunks():
            destination.write(chunk)


@cache_memoize(3600)
def get_content_type_by_perm(perm: str) -> Union["ContentType", None]:
    from django.contrib.contenttypes.models import ContentType  # noqa

    try:
        return ContentType.objects.get(
            app_label=perm.split(".", 1)[0], permission__codename=perm.split(".", 1)[1]
        )
    except ContentType.DoesNotExist:
        return None


@cache_memoize(3600)
def queryset_rules_filter(
    obj: Union[HttpRequest, Model], queryset: QuerySet, perm: str
) -> QuerySet:
    """Filter queryset by user and permission."""
    wanted_objects = set()
    if isinstance(obj, HttpRequest) and hasattr(obj, "user"):
        obj = obj.user

    for item in queryset:
        if obj.has_perm(perm, item):
            wanted_objects.add(item.pk)

    return queryset.filter(pk__in=wanted_objects)


def generate_random_code() -> str:
    """Generate random code for e.g. invitations."""
    length = get_site_preferences()["auth__invite_code_length"]
    return get_random_string(5*length).lower()


def unread_notifications_badge(request: HttpRequest) -> int:
    """Generate badge content with the number of unread notifications."""
    return request.user.person.unread_notifications_count
