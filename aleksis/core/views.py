from textwrap import wrap
from typing import Any, Dict, Optional, Type

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import QuerySet
from django.forms.models import BaseModelForm, modelform_factory
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

import reversion
from django_tables2 import RequestConfig, SingleTableView
from dynamic_preferences.forms import preference_form_builder
from guardian.shortcuts import get_objects_for_user
from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from health_check.views import MainView
from invitations.views import SendInvite, accept_invitation
from reversion import set_user
from reversion.views import RevisionMixin
from rules.contrib.views import PermissionRequiredMixin, permission_required

from aleksis.core.data_checks import DataCheckRegistry, check_data

from .filters import GroupFilter, PersonFilter
from .forms import (
    AnnouncementForm,
    ChildGroupsForm,
    DashboardWidgetOrderFormSet,
    EditAdditionalFieldForm,
    EditGroupForm,
    EditGroupTypeForm,
    EditPersonForm,
    GroupPreferenceForm,
    InvitationCodeForm,
    PersonPreferenceForm,
    PersonsAccountsFormSet,
    SchoolTermForm,
    SitePreferenceForm,
)
from .mixins import AdvancedCreateView, AdvancedDeleteView, AdvancedEditView
from .models import (
    AdditionalField,
    Announcement,
    DashboardWidget,
    DashboardWidgetOrder,
    DataCheckResult,
    Group,
    GroupType,
    Notification,
    Person,
    PersonInvitation,
    SchoolTerm,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .tables import (
    AdditionalFieldsTable,
    DashboardWidgetTable,
    GroupsTable,
    GroupTypesTable,
    InvitationsTable,
    PersonsTable,
    SchoolTermTable,
)
from .util import messages
from .util.apps import AppConfig
from .util.core_helpers import generate_random_code, objectgetter_optional
from .util.forms import PreferenceLayout


@permission_required("core.view_dashboard")
def index(request: HttpRequest) -> HttpResponse:
    """View for dashboard."""
    context = {}

    activities = request.user.person.activities.all()[:5]
    notifications = request.user.person.notifications.all()[:5]
    unread_notifications = request.user.person.notifications.all().filter(read=False)

    context["activities"] = activities
    context["notifications"] = notifications
    context["unread_notifications"] = unread_notifications

    announcements = Announcement.objects.at_time().for_person(request.user.person)
    context["announcements"] = announcements

    widgets = request.user.person.dashboard_widgets

    if len(widgets) == 0:
        # Use default dashboard if there are no widgets
        widgets = DashboardWidgetOrder.default_dashboard_widgets
        context["default_dashboard"] = True

    media = DashboardWidget.get_media(widgets)

    context["widgets"] = widgets
    context["media"] = media

    return render(request, "core/index.html", context)


class NotificationsListView(PermissionRequiredMixin, ListView):
    permission_required = "core.view_notifications"
    template_name = "core/notifications.html"

    def get_queryset(self) -> QuerySet:
        return self.request.user.person.notifications.order_by("-created")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.get_queryset().filter(read=False).update(read=True)
        return super().get_context_data(**kwargs)


def about(request: HttpRequest) -> HttpResponse:
    """About page listing all apps."""
    context = {}

    context["app_configs"] = list(
        filter(lambda a: isinstance(a, AppConfig), apps.get_app_configs())
    )

    return render(request, "core/pages/about.html", context)


class SchoolTermListView(PermissionRequiredMixin, SingleTableView):
    """Table of all school terms."""

    model = SchoolTerm
    table_class = SchoolTermTable
    permission_required = "core.view_schoolterm"
    template_name = "core/school_term/list.html"


@method_decorator(never_cache, name="dispatch")
class SchoolTermCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for school terms."""

    model = SchoolTerm
    form_class = SchoolTermForm
    permission_required = "core.add_schoolterm"
    template_name = "core/school_term/create.html"
    success_url = reverse_lazy("school_terms")
    success_message = _("The school term has been created.")


@method_decorator(never_cache, name="dispatch")
class SchoolTermEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for school terms."""

    model = SchoolTerm
    form_class = SchoolTermForm
    permission_required = "core.edit_schoolterm"
    template_name = "core/school_term/edit.html"
    success_url = reverse_lazy("school_terms")
    success_message = _("The school term has been saved.")


@permission_required("core.view_persons")
def persons(request: HttpRequest) -> HttpResponse:
    """List view listing all persons."""
    context = {}

    # Get all persons
    persons = get_objects_for_user(
        request.user, "core.view_person", Person.objects.filter(is_active=True)
    )

    # Get filter
    persons_filter = PersonFilter(request.GET, queryset=persons)
    context["persons_filter"] = persons_filter

    # Build table
    persons_table = PersonsTable(persons_filter.qs)
    RequestConfig(request).configure(persons_table)
    context["persons_table"] = persons_table

    return render(request, "core/person/list.html", context)


@permission_required(
    "core.view_person", fn=objectgetter_optional(Person, "request.user.person", True)
)
def person(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """Detail view for one person; defaulting to logged-in person."""
    context = {}

    person = objectgetter_optional(Person, "request.user.person", True)(request, id_)
    context["person"] = person

    # Get groups where person is member of
    groups = Group.objects.filter(members=person)

    # Build table
    groups_table = GroupsTable(groups)
    RequestConfig(request).configure(groups_table)
    context["groups_table"] = groups_table

    return render(request, "core/person/full.html", context)


@permission_required("core.view_group", fn=objectgetter_optional(Group, None, False))
def group(request: HttpRequest, id_: int) -> HttpResponse:
    """Detail view for one group."""
    context = {}

    group = objectgetter_optional(Group, None, False)(request, id_)
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

    # Get statistics
    context["stats"] = group.get_group_stats

    return render(request, "core/group/full.html", context)


@permission_required("core.view_groups")
def groups(request: HttpRequest) -> HttpResponse:
    """List view for listing all groups."""
    context = {}

    # Get all groups
    groups = get_objects_for_user(request.user, "core.view_group", Group)

    # Get filter
    groups_filter = GroupFilter(request.GET, queryset=groups)
    context["groups_filter"] = groups_filter

    # Build table
    groups_table = GroupsTable(groups_filter.qs)
    RequestConfig(request).configure(groups_table)
    context["groups_table"] = groups_table

    return render(request, "core/group/list.html", context)


@never_cache
@permission_required("core.link_persons_accounts")
def persons_accounts(request: HttpRequest) -> HttpResponse:
    """View allowing to batch-process linking of users to persons."""
    context = {}

    # Get all persons
    persons_qs = Person.objects.all()

    # Form set with one form per known person
    persons_accounts_formset = PersonsAccountsFormSet(request.POST or None, queryset=persons_qs)

    if request.method == "POST":
        if persons_accounts_formset.is_valid():
            persons_accounts_formset.save()

    context["persons_accounts_formset"] = persons_accounts_formset

    return render(request, "core/person/accounts.html", context)


@never_cache
@permission_required("core.assign_child_groups_to_groups")
def groups_child_groups(request: HttpRequest) -> HttpResponse:
    """View for batch-processing assignment from child groups to groups."""
    context = {}

    # Apply filter
    filter_ = GroupFilter(request.GET, queryset=Group.objects.all())
    context["filter"] = filter_

    # Paginate
    paginator = Paginator(filter_.qs, 1)
    page_number = request.POST.get("page", request.POST.get("old_page"))

    if page_number:
        page = paginator.get_page(page_number)
        group = page[0]

        if "save" in request.POST:
            form = ChildGroupsForm(request.POST)
            form.is_valid()

            if "child_groups" in form.cleaned_data:
                group.child_groups.set(form.cleaned_data["child_groups"])
                group.save()
                messages.success(request, _("The child groups were successfully saved."))
        else:
            # Init form
            form = ChildGroupsForm(initial={"child_groups": group.child_groups.all()})

        context["paginator"] = paginator
        context["page"] = page
        context["group"] = group
        context["form"] = form

    return render(request, "core/group/child_groups.html", context)


@never_cache
@permission_required("core.edit_person", fn=objectgetter_optional(Person))
def edit_person(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """Edit view for a single person, defaulting to logged-in person."""
    context = {}

    person = objectgetter_optional(Person)(request, id_)
    context["person"] = person

    if id_:
        # Edit form for existing group
        edit_person_form = EditPersonForm(
            request.POST or None, request.FILES or None, instance=person
        )
    else:
        # Empty form to create a new group
        if request.user.has_perm("core.create_person"):
            edit_person_form = EditPersonForm(request.POST or None, request.FILES or None)
        else:
            raise PermissionDenied()
    if request.method == "POST":
        if edit_person_form.is_valid():
            with reversion.create_revision():
                set_user(request.user)
                edit_person_form.save(commit=True)
            messages.success(request, _("The person has been saved."))

    context["edit_person_form"] = edit_person_form

    return render(request, "core/person/edit.html", context)


def get_group_by_id(request: HttpRequest, id_: Optional[int] = None):
    if id_:
        return get_object_or_404(Group, id=id_)
    else:
        return None


@never_cache
@permission_required("core.edit_group", fn=objectgetter_optional(Group, None, False))
def edit_group(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a group."""
    context = {}

    group = objectgetter_optional(Group, None, False)(request, id_)
    context["group"] = group

    if id_:
        # Edit form for existing group
        edit_group_form = EditGroupForm(request.POST or None, instance=group)
    else:
        # Empty form to create a new group
        if request.user.has_perm("core.create_group"):
            edit_group_form = EditGroupForm(request.POST or None)
        else:
            raise PermissionDenied()

    if request.method == "POST":
        if edit_group_form.is_valid():
            with reversion.create_revision():
                set_user(request.user)
                group = edit_group_form.save(commit=True)

            messages.success(request, _("The group has been saved."))

            return redirect("group_by_id", group.pk)

    context["edit_group_form"] = edit_group_form

    return render(request, "core/group/edit.html", context)


@permission_required("core.manage_data")
def data_management(request: HttpRequest) -> HttpResponse:
    """View with special menu for data management."""
    context = {}
    return render(request, "core/management/data_management.html", context)


class SystemStatus(PermissionRequiredMixin, MainView):
    """View giving information about the system status."""

    template_name = "core/pages/system_status.html"
    permission_required = "core.view_system_status"
    context = {}

    def get(self, request, *args, **kwargs):
        status_code = 500 if self.errors else 200
        task_results = []

        if "django_celery_results" in settings.INSTALLED_APPS:
            from django_celery_results.models import TaskResult  # noqa

            from .celery import app  # noqa

            if app.control.inspect().registered_tasks():
                job_list = list(app.control.inspect().registered_tasks().values())[0]
                for job in job_list:
                    task_results.append(
                        TaskResult.objects.filter(task_name=job).order_by("date_done").last()
                    )

        context = {"plugins": self.plugins, "status_code": status_code, "tasks": task_results}
        return self.render_to_response(context, status=status_code)


@permission_required(
    "core.mark_notification_as_read", fn=objectgetter_optional(Notification, None, False)
)
def notification_mark_read(request: HttpRequest, id_: int) -> HttpResponse:
    """Mark a notification read."""
    notification = objectgetter_optional(Notification, None, False)(request, id_)

    notification.read = True
    notification.save()

    # Redirect to dashboard as this is only used from there if JavaScript is unavailable
    return redirect("index")


@permission_required("core.view_announcements")
def announcements(request: HttpRequest) -> HttpResponse:
    """List view of announcements."""
    context = {}

    # Get all announcements
    announcements = Announcement.objects.all()
    context["announcements"] = announcements

    return render(request, "core/announcement/list.html", context)


@never_cache
@permission_required(
    "core.create_or_edit_announcement", fn=objectgetter_optional(Announcement, None, False)
)
def announcement_form(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to create or edit an announcement."""
    context = {}

    announcement = objectgetter_optional(Announcement, None, False)(request, id_)

    if announcement:
        # Edit form for existing announcement
        form = AnnouncementForm(request.POST or None, instance=announcement)
        context["mode"] = "edit"
    else:
        # Empty form to create new announcement
        form = AnnouncementForm(request.POST or None)
        context["mode"] = "add"

    if request.method == "POST":
        if form.is_valid():
            form.save()

            messages.success(request, _("The announcement has been saved."))
            return redirect("announcements")

    context["form"] = form

    return render(request, "core/announcement/form.html", context)


@permission_required(
    "core.delete_announcement", fn=objectgetter_optional(Announcement, None, False)
)
def delete_announcement(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an announcement."""
    if request.method == "POST":
        announcement = objectgetter_optional(Announcement, None, False)(request, id_)
        announcement.delete()
        messages.success(request, _("The announcement has been deleted."))

    return redirect("announcements")


@permission_required("core.search")
def searchbar_snippets(request: HttpRequest) -> HttpResponse:
    """View to return HTML snippet with searchbar autocompletion results."""
    query = request.GET.get("q", "")
    limit = int(request.GET.get("limit", "5"))

    results = SearchQuerySet().filter(text=AutoQuery(query))[:limit]
    context = {"results": results}

    return render(request, "search/searchbar_snippets.html", context)


class PermissionSearchView(PermissionRequiredMixin, SearchView):
    """Wrapper to apply permission to haystack's search view."""

    permission_required = "core.search"

    def create_response(self):
        context = self.get_context()
        if not self.has_permission():
            return self.handle_no_permission()
        return render(self.request, self.template, context)


@never_cache
def preferences(
    request: HttpRequest,
    registry_name: str = "person",
    pk: Optional[int] = None,
    section: Optional[str] = None,
) -> HttpResponse:
    """View for changing preferences."""
    context = {}

    # Decide which registry to use and check preferences
    if registry_name == "site":
        registry = site_preferences_registry
        instance = request.site
        form_class = SitePreferenceForm

        if not request.user.has_perm("core.change_site_preferences", instance):
            raise PermissionDenied()
    elif registry_name == "person":
        registry = person_preferences_registry
        instance = objectgetter_optional(Person, "request.user.person", True)(request, pk)
        form_class = PersonPreferenceForm

        if not request.user.has_perm("core.change_person_preferences", instance):
            raise PermissionDenied()
    elif registry_name == "group":
        registry = group_preferences_registry
        instance = objectgetter_optional(Group, None, False)(request, pk)
        form_class = GroupPreferenceForm

        if not request.user.has_perm("core.change_group_preferences", instance):
            raise PermissionDenied()
    else:
        # Invalid registry name passed from URL
        return HttpResponseNotFound()

    if not section and len(registry.sections()) > 0:
        default_section = list(registry.sections())[0]
        return redirect(f"preferences_{registry_name}", default_section)

    # Build final form from dynamic-preferences
    form_class = preference_form_builder(form_class, instance=instance, section=section)

    # Get layout
    form_class.layout = PreferenceLayout(form_class, section=section)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES or None)
        if form.is_valid():
            form.update_preferences()
            messages.success(request, _("The preferences have been saved successfully."))
    else:
        form = form_class()

    context["registry"] = registry
    context["registry_name"] = registry_name
    context["section"] = section
    context["registry_url"] = "preferences_" + registry_name
    context["form"] = form
    context["instance"] = instance

    return render(request, "dynamic_preferences/form.html", context)


@permission_required("core.delete_person", fn=objectgetter_optional(Person))
def delete_person(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an person."""
    person = objectgetter_optional(Person)(request, id_)

    with reversion.create_revision():
        set_user(request.user)
        person.save()

    person.delete()
    messages.success(request, _("The person has been deleted."))

    return redirect("persons")


@permission_required("core.delete_group", fn=objectgetter_optional(Group))
def delete_group(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an group."""
    group = objectgetter_optional(Group)(request, id_)
    with reversion.create_revision():
        set_user(request.user)
        group.save()

    group.delete()
    messages.success(request, _("The group has been deleted."))

    return redirect("groups")


@never_cache
@permission_required(
    "core.change_additionalfield", fn=objectgetter_optional(AdditionalField, None, False)
)
def edit_additional_field(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a additional_field."""
    context = {}

    additional_field = objectgetter_optional(AdditionalField, None, False)(request, id_)
    context["additional_field"] = additional_field

    if id_:
        # Edit form for existing additional_field
        edit_additional_field_form = EditAdditionalFieldForm(
            request.POST or None, instance=additional_field
        )
    else:
        if request.user.has_perm("core.create_additionalfield"):
            # Empty form to create a new additional_field
            edit_additional_field_form = EditAdditionalFieldForm(request.POST or None)
        else:
            raise PermissionDenied()

    if request.method == "POST":
        if edit_additional_field_form.is_valid():
            edit_additional_field_form.save(commit=True)

            messages.success(request, _("The additional_field has been saved."))

            return redirect("additional_fields")

    context["edit_additional_field_form"] = edit_additional_field_form

    return render(request, "core/additional_field/edit.html", context)


@permission_required("core.view_additionalfield")
def additional_fields(request: HttpRequest) -> HttpResponse:
    """List view for listing all additional fields."""
    context = {}

    # Get all additional fields
    additional_fields = get_objects_for_user(
        request.user, "core.view_additionalfield", AdditionalField
    )

    # Build table
    additional_fields_table = AdditionalFieldsTable(additional_fields)
    RequestConfig(request).configure(additional_fields_table)
    context["additional_fields_table"] = additional_fields_table

    return render(request, "core/additional_field/list.html", context)


@permission_required(
    "core.delete_additionalfield", fn=objectgetter_optional(AdditionalField, None, False)
)
def delete_additional_field(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an additional field."""
    additional_field = objectgetter_optional(AdditionalField, None, False)(request, id_)
    additional_field.delete()
    messages.success(request, _("The additional field has been deleted."))

    return redirect("additional_fields")


@never_cache
@permission_required("core.change_grouptype", fn=objectgetter_optional(GroupType, None, False))
def edit_group_type(request: HttpRequest, id_: Optional[int] = None) -> HttpResponse:
    """View to edit or create a group_type."""
    context = {}

    group_type = objectgetter_optional(GroupType, None, False)(request, id_)
    context["group_type"] = group_type

    if id_:
        # Edit form for existing group_type
        edit_group_type_form = EditGroupTypeForm(request.POST or None, instance=group_type)
    else:
        # Empty form to create a new group_type
        edit_group_type_form = EditGroupTypeForm(request.POST or None)

    if request.method == "POST":
        if edit_group_type_form.is_valid():
            edit_group_type_form.save(commit=True)

            messages.success(request, _("The group type has been saved."))

            return redirect("group_types")

    context["edit_group_type_form"] = edit_group_type_form

    return render(request, "core/group_type/edit.html", context)


@permission_required("core.view_grouptype")
def group_types(request: HttpRequest) -> HttpResponse:
    """List view for listing all group types."""
    context = {}

    # Get all group types
    group_types = get_objects_for_user(request.user, "core.view_grouptype", GroupType)

    # Build table
    group_types_table = GroupTypesTable(group_types)
    RequestConfig(request).configure(group_types_table)
    context["group_types_table"] = group_types_table

    return render(request, "core/group_type/list.html", context)


@permission_required("core.delete_grouptype", fn=objectgetter_optional(GroupType, None, False))
def delete_group_type(request: HttpRequest, id_: int) -> HttpResponse:
    """View to delete an group_type."""
    group_type = objectgetter_optional(GroupType, None, False)(request, id_)
    group_type.delete()
    messages.success(request, _("The group type has been deleted."))

    return redirect("group_types")


class DataCheckView(PermissionRequiredMixin, ListView):
    permission_required = "core.view_datacheckresults"
    model = DataCheckResult
    template_name = "core/data_check/list.html"
    context_object_name = "results"

    def get_queryset(self) -> QuerySet:
        return DataCheckResult.objects.filter(solved=False).order_by("check")

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["registered_checks"] = DataCheckRegistry.data_checks
        return context


class RunDataChecks(PermissionRequiredMixin, View):
    permission_required = "core.run_data_checks"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not check_data()[1]:
            messages.success(
                request,
                _(
                    "The data check has been started. Please note that it may take "
                    "a while before you are able to fetch the data on this page."
                ),
            )
        else:
            messages.success(request, _("The data check has finished."))
        return redirect("check_data")


class SolveDataCheckView(PermissionRequiredMixin, RevisionMixin, DetailView):
    queryset = DataCheckResult.objects.all()
    permission_required = "core.solve_data_problem"

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        solve_option = self.kwargs["solve_option"]
        result = self.get_object()
        if solve_option in result.related_check.solve_options:
            solve_option_obj = result.related_check.solve_options[solve_option]

            msg = _(
                f"The solve option '{solve_option_obj.verbose_name}' "
                f"has been executed on the object '{result.related_object}' "
                f"(type: {result.related_object._meta.verbose_name})."
            )

            result.solve(solve_option)

            messages.success(request, msg)
            return redirect("check_data")
        else:
            return HttpResponseNotFound()


class DashboardWidgetListView(PermissionRequiredMixin, SingleTableView):
    """Table of all dashboard widgets."""

    model = DashboardWidget
    table_class = DashboardWidgetTable
    permission_required = "core.view_dashboardwidget"
    template_name = "core/dashboard_widget/list.html"

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["widget_types"] = [
            (ContentType.objects.get_for_model(m, False), m)
            for m in DashboardWidget.__subclasses__()
        ]
        return context


@method_decorator(never_cache, name="dispatch")
class DashboardWidgetEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for dashboard widgets."""

    def get_form_class(self) -> Type[BaseModelForm]:
        return modelform_factory(self.object.__class__, fields=self.fields)

    model = DashboardWidget
    fields = "__all__"
    permission_required = "core.edit_dashboardwidget"
    template_name = "core/dashboard_widget/edit.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been saved.")


@method_decorator(never_cache, name="dispatch")
class DashboardWidgetCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for dashboard widgets."""

    def get_model(self, request, *args, **kwargs):
        app_label = kwargs.get("app")
        model = kwargs.get("model")
        ct = get_object_or_404(ContentType, app_label=app_label, model=model)
        return ct.model_class()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        return context

    def get(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    fields = "__all__"
    permission_required = "core.add_dashboardwidget"
    template_name = "core/dashboard_widget/create.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been created.")


class DashboardWidgetDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete view for dashboard widgets."""

    model = DashboardWidget
    permission_required = "core.delete_dashboardwidget"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("dashboard_widgets")
    success_message = _("The dashboard widget has been deleted.")


class EditDashboardView(View):
    """View for editing dashboard widget order."""

    def get_context_data(self, request, **kwargs):
        context = {}
        self.default_dashboard = kwargs.get("default", False)

        if self.default_dashboard and not request.user.has_perm("core.edit_default_dashboard"):
            raise PermissionDenied()

        context["default_dashboard"] = self.default_dashboard

        widgets = (
            request.user.person.dashboard_widgets
            if not self.default_dashboard
            else DashboardWidgetOrder.default_dashboard_widgets
        )
        not_used_widgets = DashboardWidget.objects.exclude(pk__in=[w.pk for w in widgets]).filter(
            active=True
        )
        context["widgets"] = widgets
        context["not_used_widgets"] = not_used_widgets

        order = 10
        initial = []
        for widget in widgets:
            initial.append({"pk": widget, "order": order})
            order += 10
        for widget in not_used_widgets:
            initial.append({"pk": widget, "order": 0})

        formset = DashboardWidgetOrderFormSet(
            request.POST or None, initial=initial, prefix="widget_order"
        )
        context["formset"] = formset

        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)

        if context["formset"].is_valid():
            added_objects = []
            for form in context["formset"]:
                if not form.cleaned_data["order"]:
                    continue

                obj, created = DashboardWidgetOrder.objects.update_or_create(
                    widget=form.cleaned_data["pk"],
                    person=request.user.person if not self.default_dashboard else None,
                    default=self.default_dashboard,
                    defaults={"order": form.cleaned_data["order"]},
                )

                added_objects.append(obj.pk)

            DashboardWidgetOrder.objects.filter(
                person=request.user.person if not self.default_dashboard else None,
                default=self.default_dashboard,
            ).exclude(pk__in=added_objects).delete()

            if not self.default_dashboard:
                msg = _("Your dashboard configuration has been saved successfully.")
            else:
                msg = _("The configuration of the default dashboard has been saved successfully.")
            messages.success(request, msg)
            return redirect("index" if not self.default_dashboard else "dashboard_widgets")

    def get(self, request, **kwargs):
        context = self.get_context_data(request, **kwargs)

        return render(request, "core/edit_dashboard.html", context=context)


class InvitePerson(PermissionRequiredMixin, SingleTableView, SendInvite):
    """View to invite a person to register an account."""

    template_name = "invitations/forms/_invite.html"
    permission_required = "core.can_invite"
    model = PersonInvitation
    table_class = InvitationsTable
    context = {}

    def get_context_data(self, **kwargs):
        queryset = kwargs.pop("object_list", None)
        if queryset is None:
            self.object_list = self.model.objects.all()[:5]
        return super().get_context_data(**kwargs)


def enter_invitation_code(request: HttpRequest) -> HttpResponse:
    """View to enter an invite code."""
    context = {}

    invitation_code_form = InvitationCodeForm(request.POST or None)
    context["invitation_code_form"] = invitation_code_form

    if request.method == "POST":
        if invitation_code_form.is_valid():
            code = "".join(invitation_code_form.cleaned_data["code"].split("-"))
            if (
                PersonInvitation.objects.filter(key=code).exists()
                and not PersonInvitation.objects.get(key=code).accepted
                and not PersonInvitation.objects.get(key=code).key_expired()
            ):
                invitation = PersonInvitation.objects.get(key=code)
                accept_invitation(
                    invitation=invitation, request=request, signal_sender=request.user
                )
                return redirect("account_signup")
            else:
                messages.error(
                    request,
                    _(
                        "The entered code is invalid. The invitation"
                        " is either expired or does not exist."
                    ),
                )

    return render(request, "invitations/enter.html", context)


def generate_invitation_code(request: HttpRequest) -> HttpResponse:
    """View to generate an invitation code."""
    context = {}

    code = generate_random_code()

    PersonInvitation.objects.create(
        email="", inviter=request.user, key=code,
    )

    code = "-".join(wrap(code, 5))

    messages.success(
        request, _(f"The invitation was successfully created. The invitation code is {code}"),
    )

    return redirect("invite_person")
