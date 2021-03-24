from typing import Optional

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Model
from django.http import HttpRequest

from guardian.backends import ObjectPermissionBackend
from guardian.shortcuts import get_objects_for_user
from rules import predicate

from ..mixins import ExtensibleModel
from ..models import Group
from .core_helpers import get_content_type_by_perm, get_site_preferences
from .core_helpers import has_person as has_person_helper
from .core_helpers import queryset_rules_filter


def permission_validator(request: HttpRequest, perm: str) -> bool:
    """Check whether the request user has a permission."""
    if request.user:
        return request.user.has_perm(perm)
    return False


def check_global_permission(user: User, perm: str) -> bool:
    """Check whether a user has a global permission."""
    return ModelBackend().has_perm(user, perm)


def check_object_permission(
    user: User, perm: str, obj: Model, checker_obj: Optional[ExtensibleModel] = None
) -> bool:
    """Check whether a user has a permission on an object.

    You can provide a custom ``ObjectPermissionChecker`` for prefetching object permissions
    by annotating an extensible model with ``set_object_permission_checker``.
    This can be the provided object (``obj``)  or a special object
    which is only used to get the checker class (``checker_obj``).
    """
    if not checker_obj:
        checker_obj = obj
    if hasattr(checker_obj, "_permission_checker"):
        return checker_obj._permission_checker.has_perm(perm, obj)
    return ObjectPermissionBackend().has_perm(user, perm, obj)


def has_global_perm(perm: str):
    """Build predicate which checks whether a user has a global permission."""
    name = f"has_global_perm:{perm}"

    @predicate(name)
    def fn(user: User) -> bool:
        return check_global_permission(user, perm)

    return fn


def has_object_perm(perm: str):
    """Build predicate which checks whether a user has a permission on a object."""
    name = f"has_global_perm:{perm}"

    @predicate(name)
    def fn(user: User, obj: Model) -> bool:
        if not obj:
            return False
        return check_object_permission(user, perm, obj)

    return fn


def has_any_object(perm: str, klass):
    """Check if has any object.

    Build predicate which checks whether a user has access
    to objects with the provided permission or rule.
    """
    name = f"has_any_object:{perm}"

    @predicate(name)
    def fn(user: User) -> bool:
        ct_perm = get_content_type_by_perm(perm)
        if ct_perm and ct_perm.model_class() == klass:
            return get_objects_for_user(user, perm, klass).exists()
        else:
            return queryset_rules_filter(user, klass.objects.all(), perm).exists()

    return fn


def is_site_preference_set(section: str, pref: str):
    """Check the boolean value of a given site preference."""
    name = f"check_site_preference:{section}__{pref}"

    @predicate(name)
    def fn() -> bool:
        return bool(get_site_preferences()[f"{section}__{pref}"])

    return fn


@predicate
def has_person(user: User) -> bool:
    """Predicate which checks whether a user has a linked person."""
    return has_person_helper(user)


@predicate
def is_current_person(user: User, obj: Model) -> bool:
    """Predicate which checks if the provided object is the person linked to the user object."""
    return user.person == obj


@predicate
def is_group_owner(user: User, group: Group) -> bool:
    """Predicate which checks if the user is a owner of the provided group."""
    return group.owners.filter(owners=user.person).exists()


@predicate
def is_group_member(user: User, group: Group) -> bool:
    """Predicate which checks if the user is a member of the provided group."""
    return user.person in group.members.all()


@predicate
def is_notification_recipient(user: User, obj: Model) -> bool:
    """Check if is a notification recipient.

    Predicate which checks whether the recipient of the
    notification a user wants to mark read is this user.
    """
    return user == obj.recipient.user
