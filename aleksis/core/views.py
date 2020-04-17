from typing import Optional

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from django_tables2 import RequestConfig
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from .decorators import admin_required, person_required
from .forms import (
    EditGroupForm,
    EditPersonForm,
    EditSchoolForm,
    EditTermForm,
    PersonsAccountsFormSet,
    AnnouncementForm,
)
from .models import Activity, Group, Notification, Person, School, DashboardWidget, Announcement
from .tables import GroupsTable, PersonsTable
from .util import messages


@person_required
def index(request: HttpRequest) -> HttpResponse:
    context = {}

    activities = request.user.person.activities.all()[:5]
    notifications = request.user.person.notifications.all()[:5]
    unread_notifications = request.user.person.notifications.all().filter(read=False)

    context["activities"] = activities
    context["notifications"] = notifications
    context["unread_notifications"] = unread_notifications

    announcements = Announcement.objects.at_time().for_person(request.user.person)
    context["announcements"] = announcements

    widgets = DashboardWidget.objects.filter(active=True)
    media = DashboardWidget.get_media(widgets)

    context["widgets"] = widgets
    context["media"] = media

    return render(request, "core/index.html", context)


def offline(request):
    return render(request, "core/offline.html")


@login_required
def persons(request: HttpRequest) -> HttpResponse:
    context = {}

    # Get all persons
    persons = Person.objects.filter(is_active=True)

    # Build table
    persons_table = PersonsTable(persons)
    RequestConfig(request).configure(persons_table)
    context["persons_table"] = persons_table

    return render(request, "core/persons.html", context)


@login_required
def person(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    context = {}

    # Get person and check access
    try:
        if id_ is None:
            person = request.user.person
        else:
            person = Person.objects.get(pk=id_)
    except Person.DoesNotExist as e:
        # Turn not-found object into a 404 error
        raise Http404 from e

    context["person"] = person

    # Get groups where person is member of
    groups = Group.objects.filter(members=person)

    # Build table
    groups_table = GroupsTable(groups)
    RequestConfig(request).configure(groups_table)
    context["groups_table"] = groups_table

    return render(request, "core/person_full.html", context)


@login_required
def group(request: HttpRequest, id_: int) -> HttpResponse:
    context = {}

    # Get group and check if it exist
    try:
        group = Group.objects.get(pk=id_)
    except Group.DoesNotExist as e:
        # Turn not-found object into a 404 error
        raise Http404 from e

    context["group"] = group

    # Get group
    group = Group.objects.get(pk=id_)

    # Get members
    members = group.members.filter(is_active=True)

    # Build table
    members_table = PersonsTable(members)
    RequestConfig(request).configure(members_table)
    context["members_table"] = members_table

    # Get owners
    owners = group.owners.filter(is_active=True)

    # Build table
    owners_table = PersonsTable(owners)
    RequestConfig(request).configure(owners_table)
    context["owners_table"] = owners_table

    return render(request, "core/group_full.html", context)


@login_required
def groups(request: HttpRequest) -> HttpResponse:
    context = {}

    # Get all groups
    groups = Group.objects.all()

    # Build table
    groups_table = GroupsTable(groups)
    RequestConfig(request).configure(groups_table)
    context["groups_table"] = groups_table

    return render(request, "core/groups.html", context)


@admin_required
def persons_accounts(request: HttpRequest) -> HttpResponse:
    context = {}

    persons_qs = Person.objects.all()
    persons_accounts_formset = PersonsAccountsFormSet(request.POST or None, queryset=persons_qs)

    if request.method == "POST":
        if persons_accounts_formset.is_valid():
            persons_accounts_formset.save()

    context["persons_accounts_formset"] = persons_accounts_formset

    return render(request, "core/persons_accounts.html", context)


@admin_required
def edit_person(request: HttpRequest, id_: int) -> HttpResponse:
    context = {}

    person = get_object_or_404(Person, id=id_)

    edit_person_form = EditPersonForm(request.POST or None, request.FILES or None, instance=person)

    context["person"] = person

    if request.method == "POST":
        if edit_person_form.is_valid():
            edit_person_form.save(commit=True)

            messages.success(request, _("The person has been saved."))
            return redirect("edit_person_by_id", id_=person.id)

    context["edit_person_form"] = edit_person_form

    return render(request, "core/edit_person.html", context)


@admin_required
def edit_group(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    context = {}

    if id_:
        group = get_object_or_404(Group, id=id_)
        edit_group_form = EditGroupForm(request.POST or None, instance=group)
    else:
        group = None
        edit_group_form = EditGroupForm(request.POST or None)

    if request.method == "POST":
        if edit_group_form.is_valid():
            edit_group_form.save(commit=True)

            messages.success(request, _("The group has been saved."))
            return redirect("groups")

    context["group"] = group
    context["edit_group_form"] = edit_group_form

    return render(request, "core/edit_group.html", context)


@admin_required
def data_management(request: HttpRequest) -> HttpResponse:
    context = {}
    return render(request, "core/data_management.html", context)


@admin_required
def system_status(request: HttpRequest) -> HttpResponse:
    context = {}

    return render(request, "core/system_status.html", context)


@admin_required
def school_management(request: HttpRequest) -> HttpResponse:
    context = {}
    return render(request, "core/school_management.html", context)


@admin_required
def edit_school(request: HttpRequest) -> HttpResponse:
    context = {}

    school = School.objects.first()
    edit_school_form = EditSchoolForm(request.POST or None, request.FILES or None, instance=school)

    context["school"] = school

    if request.method == "POST":
        if edit_school_form.is_valid():
            edit_school_form.save(commit=True)

            messages.success(request, _("The school has been saved."))
            return redirect("index")

    context["edit_school_form"] = edit_school_form

    return render(request, "core/edit_school.html", context)


@admin_required
def edit_schoolterm(request: HttpRequest) -> HttpResponse:
    context = {}

    term = School.objects.first().current_term
    edit_term_form = EditTermForm(request.POST or None, instance=term)

    if request.method == "POST":
        if edit_term_form.is_valid():
            edit_term_form.save(commit=True)

            messages.success(request, _("The term has been saved."))
            return redirect("index")

    context["edit_term_form"] = edit_term_form

    return render(request, "core/edit_schoolterm.html", context)


def notification_mark_read(request: HttpRequest, id_: int) -> HttpResponse:
    context = {}

    notification = get_object_or_404(Notification, pk=id_)

    if notification.recipient.user == request.user:
        notification.read = True
        notification.save()
    else:
        raise PermissionDenied(_("You are not allowed to mark notifications from other users as read!"))

    return redirect("index")


@admin_required
def announcements(request: HttpRequest) -> HttpResponse:
    context = {}

    # Get all persons
    announcements = Announcement.objects.all()
    context["announcements"] = announcements

    return render(request, "core/announcement/list.html", context)


@admin_required
def announcement_form(request: HttpRequest, pk: Optional[int] = None) -> HttpResponse:
    context = {}

    if pk:
        announcement = get_object_or_404(Announcement, pk=pk)
        form = AnnouncementForm(
            request.POST or None,
            instance=announcement
        )
        context["mode"] = "edit"
    else:
        form = AnnouncementForm(request.POST or None)
        context["mode"] = "add"

    if request.method == "POST":
        if form.is_valid():
            form.save()

            messages.success(request, _("The announcement has been saved."))
            return redirect("announcements")

    context["form"] = form

    return render(request, "core/announcement/form.html", context)


@admin_required
def delete_announcement(request: HttpRequest, pk: int) -> HttpResponse:
    if request.method == "POST":
        announcement = get_object_or_404(Announcement, pk=pk)
        announcement.delete()
        messages.success(request, _("The announcement has been deleted."))

    return redirect("announcements")


@login_required
def searchbar_snippets(request: HttpRequest) -> HttpResponse:
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', '5'))

    results = SearchQuerySet().filter(text=AutoQuery(query))[:limit]
    context = {"results": results}

    return render(request, "search/searchbar_snippets.html", context)
