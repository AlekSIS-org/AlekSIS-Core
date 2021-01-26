from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from django.views.i18n import JavaScriptCatalog

import calendarweek.django
import debug_toolbar
from django_js_reverse.views import urls_js
from health_check.urls import urlpatterns as health_urls
from two_factor.urls import urlpatterns as tf_urls

from . import views
from .util.core_helpers import is_celery_enabled

urlpatterns = [
    path("", include("django_prometheus.urls")),
    path("", include("pwa.urls"), name="pwa"),
    path("about/", views.about, name="about_aleksis"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/", include("allauth.urls")),
    path("invitations/send-invite", views.InvitePerson.as_view(), name="invite_person"),
    path("invitations/code/enter", views.enter_invitation_code, name="enter_invitation_code"),
    path(
        "invitations/code/generate", views.generate_invitation_code, name="generate_invitation_code"
    ),
    path("invitations/", include("invitations.urls")),
    path("admin/", admin.site.urls),
    path("data_management/", views.data_management, name="data_management"),
    path("status/", views.SystemStatus.as_view(), name="system_status"),
    path("", include(tf_urls)),
    path("school_terms/", views.SchoolTermListView.as_view(), name="school_terms"),
    path("school_terms/create/", views.SchoolTermCreateView.as_view(), name="create_school_term"),
    path("school_terms/<int:pk>/", views.SchoolTermEditView.as_view(), name="edit_school_term"),
    path("persons", views.persons, name="persons"),
    path("persons/accounts", views.persons_accounts, name="persons_accounts"),
    path("person", views.person, name="person"),
    path("person/create", views.edit_person, name="create_person"),
    path("person/<int:id_>", views.person, name="person_by_id"),
    path("person/<int:id_>/edit", views.edit_person, name="edit_person_by_id"),
    path("person/<int:id_>/delete", views.delete_person, name="delete_person_by_id"),
    path("groups", views.groups, name="groups"),
    path("groups/additional_fields", views.additional_fields, name="additional_fields"),
    path("groups/child_groups/", views.groups_child_groups, name="groups_child_groups"),
    path(
        "groups/additional_field/<int:id_>/edit",
        views.edit_additional_field,
        name="edit_additional_field_by_id",
    ),
    path(
        "groups/additional_field/create",
        views.edit_additional_field,
        name="create_additional_field",
    ),
    path(
        "groups/additional_field/<int:id_>/delete",
        views.delete_additional_field,
        name="delete_additional_field_by_id",
    ),
    path("group/create", views.edit_group, name="create_group"),
    path("group/<int:id_>", views.group, name="group_by_id"),
    path("group/<int:id_>/edit", views.edit_group, name="edit_group_by_id"),
    path("group/<int:id_>/delete", views.delete_group, name="delete_group_by_id"),
    path("", views.index, name="index"),
    path("notifications/", views.NotificationsListView.as_view(), name="notifications"),
    path("dashboard/edit/", views.EditDashboardView.as_view(), name="edit_dashboard"),
    path(
        "notifications/mark-read/<int:id_>",
        views.notification_mark_read,
        name="notification_mark_read",
    ),
    path("groups/group_type/create", views.edit_group_type, name="create_group_type"),
    path(
        "groups/group_type/<int:id_>/delete",
        views.delete_group_type,
        name="delete_group_type_by_id",
    ),
    path("groups/group_type/<int:id_>/edit", views.edit_group_type, name="edit_group_type_by_id"),
    path("groups/group_types", views.group_types, name="group_types"),
    path("announcements/", views.announcements, name="announcements"),
    path("announcement/create/", views.announcement_form, name="add_announcement"),
    path("announcement/edit/<int:id_>/", views.announcement_form, name="edit_announcement"),
    path("announcement/delete/<int:id_>/", views.delete_announcement, name="delete_announcement"),
    path("search/searchbar/", views.searchbar_snippets, name="searchbar_snippets"),
    path("search/", views.PermissionSearchView(), name="haystack_search"),
    path("maintenance-mode/", include("maintenance_mode.urls")),
    path("impersonate/", include("impersonate.urls")),
    path("__i18n__/", include("django.conf.urls.i18n")),
    path("select2/", include("django_select2.urls")),
    path("jsreverse.js", urls_js, name="js_reverse"),
    path("calendarweek_i18n.js", calendarweek.django.i18n_js, name="calendarweek_i18n_js"),
    path("gettext.js", JavaScriptCatalog.as_view(), name="javascript-catalog"),
    path(
        "preferences/site/", views.preferences, {"registry_name": "site"}, name="preferences_site"
    ),
    path(
        "preferences/person/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<int:pk>/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path(
        "preferences/site/<str:section>/",
        views.preferences,
        {"registry_name": "site"},
        name="preferences_site",
    ),
    path(
        "preferences/person/<str:section>/",
        views.preferences,
        {"registry_name": "person"},
        name="preferences_person",
    ),
    path(
        "preferences/group/<str:section>/",
        views.preferences,
        {"registry_name": "group"},
        name="preferences_group",
    ),
    path("health/", include(health_urls)),
    path("data_check/", views.DataCheckView.as_view(), name="check_data",),
    path("data_check/run/", views.RunDataChecks.as_view(), name="data_check_run",),
    path(
        "data_check/<int:pk>/<str:solve_option>/",
        views.SolveDataCheckView.as_view(),
        name="data_check_solve",
    ),
    path("dashboard_widgets/", views.DashboardWidgetListView.as_view(), name="dashboard_widgets"),
    path(
        "dashboard_widgets/<int:pk>/edit/",
        views.DashboardWidgetEditView.as_view(),
        name="edit_dashboard_widget",
    ),
    path(
        "dashboard_widgets/<int:pk>/delete/",
        views.DashboardWidgetDeleteView.as_view(),
        name="delete_dashboard_widget",
    ),
    path(
        "dashboard_widgets/<str:app>/<str:model>/new/",
        views.DashboardWidgetCreateView.as_view(),
        name="create_dashboard_widget",
    ),
    path(
        "dashboard_widgets/default/",
        views.EditDashboardView.as_view(),
        {"default": True},
        name="edit_default_dashboard",
    ),
]

# Serve static files from STATIC_ROOT to make it work with runserver
# collectstatic is also required in development for this
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files from MEDIA_ROOT to make it work with runserver
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add URLs for optional features
if hasattr(settings, "TWILIO_ACCOUNT_SID"):
    from two_factor.gateways.twilio.urls import urlpatterns as tf_twilio_urls  # noqa

    urlpatterns += [path("", include(tf_twilio_urls))]

if is_celery_enabled():
    urlpatterns.append(path("celery_progress/", include("celery_progress.urls")))

# Serve javascript-common if in development
if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include(debug_toolbar.urls)))

# Automatically mount URLs from all installed AlekSIS apps
for app_config in apps.app_configs.values():
    if not app_config.name.startswith("aleksis.apps."):
        continue

    try:
        urlpatterns.append(path(f"app/{app_config.label}/", include(f"{app_config.name}.urls")))
    except ModuleNotFoundError:
        # Ignore exception as app just has no URLs
        pass  # noqa
