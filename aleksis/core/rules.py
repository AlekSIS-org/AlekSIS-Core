import rules

from .models import AdditionalField, Announcement, Group, GroupType, Person
from .util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
    is_current_person,
    is_group_owner,
    is_notification_recipient,
    is_site_preference_set,
)

rules.add_perm("core", rules.always_allow)

# View dashboard
view_dashboard_predicate = is_site_preference_set("general", "anonymous_dashboard") | has_person
rules.add_perm("core.view_dashboard", view_dashboard_predicate)

# View notifications
rules.add_perm("core.view_notifications", has_person)

# Use search
search_predicate = has_person & has_global_perm("core.search")
rules.add_perm("core.search", search_predicate)

# View persons
view_persons_predicate = has_person & (
    has_global_perm("core.view_person") | has_any_object("core.view_person", Person)
)
rules.add_perm("core.view_persons", view_persons_predicate)

# View person
view_person_predicate = has_person & (
    has_global_perm("core.view_person") | has_object_perm("core.view_person") | is_current_person
)
rules.add_perm("core.view_person", view_person_predicate)

# View person address
view_address_predicate = has_person & (
    has_global_perm("core.view_address") | has_object_perm("core.view_address") | is_current_person
)
rules.add_perm("core.view_address", view_address_predicate)

# View person contact details
view_contact_details_predicate = has_person & (
    has_global_perm("core.view_contact_details")
    | has_object_perm("core.view_contact_details")
    | is_current_person
)
rules.add_perm("core.view_contact_details", view_contact_details_predicate)

# View person photo
view_photo_predicate = has_person & (
    has_global_perm("core.view_photo") | has_object_perm("core.view_photo") | is_current_person
)
rules.add_perm("core.view_photo", view_photo_predicate)

# View persons groups
view_groups_predicate = has_person & (
    has_global_perm("core.view_person_groups")
    | has_object_perm("core.view_person_groups")
    | is_current_person
)
rules.add_perm("core.view_person_groups", view_groups_predicate)

# Edit person
edit_person_predicate = has_person & (
    has_global_perm("core.change_person") | has_object_perm("core.change_person")
)
rules.add_perm("core.edit_person", edit_person_predicate)

# Delete person
delete_person_predicate = has_person & (
    has_global_perm("core.delete_person") | has_object_perm("core.delete_person")
)
rules.add_perm("core.delete_person", delete_person_predicate)

# Link persons with accounts
link_persons_accounts_predicate = has_person & has_global_perm("core.link_persons_accounts")
rules.add_perm("core.link_persons_accounts", link_persons_accounts_predicate)

# View groups
view_groups_predicate = has_person & (
    has_global_perm("core.view_group") | has_any_object("core.view_group", Group)
)
rules.add_perm("core.view_groups", view_groups_predicate)

# View group
view_group_predicate = has_person & (
    has_global_perm("core.view_group") | has_object_perm("core.view_group")
)
rules.add_perm("core.view_group", view_group_predicate)

# Edit group
edit_group_predicate = has_person & (
    has_global_perm("core.change_group") | has_object_perm("core.change_group")
)
rules.add_perm("core.edit_group", edit_group_predicate)

# Delete group
delete_group_predicate = has_person & (
    has_global_perm("core.delete_group") | has_object_perm("core.delete_group")
)
rules.add_perm("core.delete_group", delete_group_predicate)

# Assign child groups to groups
assign_child_groups_to_groups_predicate = has_person & has_global_perm(
    "core.assign_child_groups_to_groups"
)
rules.add_perm("core.assign_child_groups_to_groups", assign_child_groups_to_groups_predicate)

# Edit school information
edit_school_information_predicate = has_person & has_global_perm("core.change_school")
rules.add_perm("core.edit_school_information", edit_school_information_predicate)

# Manage data
manage_data_predicate = has_person & has_global_perm("core.manage_data")
rules.add_perm("core.manage_data", manage_data_predicate)

# Mark notification as read
mark_notification_as_read_predicate = has_person & is_notification_recipient
rules.add_perm("core.mark_notification_as_read", mark_notification_as_read_predicate)

# View announcements
view_announcements_predicate = has_person & (
    has_global_perm("core.view_announcement")
    | has_any_object("core.view_announcement", Announcement)
)
rules.add_perm("core.view_announcements", view_announcements_predicate)

# Create or edit announcement
create_or_edit_announcement_predicate = has_person & (
    has_global_perm("core.add_announcement")
    & (has_global_perm("core.change_announcement") | has_object_perm("core.change_announcement"))
)
rules.add_perm("core.create_or_edit_announcement", create_or_edit_announcement_predicate)

# Delete announcement
delete_announcement_predicate = has_person & (
    has_global_perm("core.delete_announcement") | has_object_perm("core.delete_announcement")
)
rules.add_perm("core.delete_announcement", delete_announcement_predicate)

# Use impersonate
impersonate_predicate = has_person & has_global_perm("core.impersonate")
rules.add_perm("core.impersonate", impersonate_predicate)

# View system status
view_system_status_predicate = has_person & has_global_perm("core.view_system_status")
rules.add_perm("core.view_system_status", view_system_status_predicate)

# View people menu (persons + objects)
rules.add_perm(
    "core.view_people_menu",
    has_person
    & (
        view_persons_predicate
        | view_groups_predicate
        | link_persons_accounts_predicate
        | assign_child_groups_to_groups_predicate
    ),
)

# View person personal details
view_personal_details_predicate = has_person & (
    has_global_perm("core.view_personal_details")
    | has_object_perm("core.view_personal_details")
    | is_current_person
)
rules.add_perm("core.view_personal_details", view_personal_details_predicate)

# Change site preferences
change_site_preferences = has_person & (
    has_global_perm("core.change_site_preferences")
    | has_object_perm("core.change_site_preferences")
)
rules.add_perm("core.change_site_preferences", change_site_preferences)

# Change person preferences
change_person_preferences = has_person & (
    has_global_perm("core.change_person_preferences")
    | has_object_perm("core.change_person_preferences")
    | is_current_person
)
rules.add_perm("core.change_person_preferences", change_person_preferences)

# Change group preferences
change_group_preferences = has_person & (
    has_global_perm("core.change_group_preferences")
    | has_object_perm("core.change_group_preferences")
    | is_group_owner
)
rules.add_perm("core.change_group_preferences", change_group_preferences)


# Edit additional field
change_additional_field_predicate = has_person & (
    has_global_perm("core.change_additionalfield") | has_object_perm("core.change_additionalfield")
)
rules.add_perm("core.change_additionalfield", change_additional_field_predicate)

# Edit additional field
create_additional_field_predicate = has_person & (
    has_global_perm("core.create_additionalfield") | has_object_perm("core.create_additionalfield")
)
rules.add_perm("core.create_additionalfield", create_additional_field_predicate)


# Delete additional field
delete_additional_field_predicate = has_person & (
    has_global_perm("core.delete_additionalfield") | has_object_perm("core.delete_additionalfield")
)
rules.add_perm("core.delete_additionalfield", delete_additional_field_predicate)

# View additional fields
view_additional_field_predicate = has_person & (
    has_global_perm("core.view_additionalfield")
    | has_any_object("core.view_additionalfield", AdditionalField)
)
rules.add_perm("core.view_additionalfield", view_additional_field_predicate)

# Edit group type
change_group_type_predicate = has_person & (
    has_global_perm("core.change_grouptype") | has_object_perm("core.change_grouptype")
)
rules.add_perm("core.edit_grouptype", change_group_type_predicate)

# Create group type
create_group_type_predicate = has_person & (
    has_global_perm("core.create_grouptype") | has_object_perm("core.change_grouptype")
)
rules.add_perm("core.create_grouptype", create_group_type_predicate)


# Delete group type
delete_group_type_predicate = has_person & (
    has_global_perm("core.delete_grouptype") | has_object_perm("core.delete_grouptype")
)
rules.add_perm("core.delete_grouptype", delete_group_type_predicate)

# View group types
view_group_type_predicate = has_person & (
    has_global_perm("core.view_grouptype") | has_any_object("core.view_grouptype", GroupType)
)
rules.add_perm("core.view_grouptype", view_group_type_predicate)

# Create person
create_person_predicate = has_person & (
    has_global_perm("core.create_person") | has_object_perm("core.create_person")
)
rules.add_perm("core.create_person", create_person_predicate)

# Create group
create_group_predicate = has_person & (
    has_global_perm("core.create_group") | has_object_perm("core.create_group")
)
rules.add_perm("core.create_group", create_group_predicate)

# School years
view_school_term_predicate = has_person & has_global_perm("core.view_schoolterm")
rules.add_perm("core.view_schoolterm", view_school_term_predicate)

create_school_term_predicate = has_person & has_global_perm("core.add_schoolterm")
rules.add_perm("core.create_schoolterm", create_school_term_predicate)

edit_school_term_predicate = has_person & has_global_perm("core.change_schoolterm")
rules.add_perm("core.edit_schoolterm", edit_school_term_predicate)

# View admin menu
view_admin_menu_predicate = has_person & (
    manage_data_predicate
    | view_school_term_predicate
    | impersonate_predicate
    | view_system_status_predicate
    | view_announcements_predicate
)
rules.add_perm("core.view_admin_menu", view_admin_menu_predicate)

# View group stats
view_group_stats_predicate = has_person & (
    has_global_perm("core.view_group_stats") | has_object_perm("core.view_group_stats")
)
rules.add_perm("core.view_group_stats", view_group_stats_predicate)

# View data check results
view_data_check_results_predicate = has_person & has_global_perm("core.view_datacheckresult")
rules.add_perm("core.view_datacheckresults", view_data_check_results_predicate)

# Run data checks
run_data_checks_predicate = (
    has_person & view_data_check_results_predicate & has_global_perm("core.run_data_checks")
)
rules.add_perm("core.run_data_checks", run_data_checks_predicate)

# Solve data problems
solve_data_problem_predicate = (
    has_person & view_data_check_results_predicate & has_global_perm("core.solve_data_problem")
)
rules.add_perm("core.solve_data_problem", solve_data_problem_predicate)

view_dashboard_widget_predicate = has_person & has_global_perm("core.view_dashboardwidget")
rules.add_perm("core.view_dashboardwidget", view_dashboard_widget_predicate)

create_dashboard_widget_predicate = has_person & has_global_perm("core.add_dashboardwidget")
rules.add_perm("core.create_dashboardwidget", create_dashboard_widget_predicate)

edit_dashboard_widget_predicate = has_person & has_global_perm("core.change_dashboardwidget")
rules.add_perm("core.edit_dashboardwidget", edit_dashboard_widget_predicate)

delete_dashboard_widget_predicate = has_person & has_global_perm("core.delete_dashboardwidget")
rules.add_perm("core.delete_dashboardwidget", delete_dashboard_widget_predicate)

edit_dashboard_predicate = is_site_preference_set("general", "dashboard_editing") & has_person
rules.add_perm("core.edit_dashboard", edit_dashboard_predicate)

edit_default_dashboard_predicate = has_person & has_global_perm("core.edit_default_dashboard")
rules.add_perm("core.edit_default_dashboard", edit_default_dashboard_predicate)

# django-allauth
can_register_predicate = is_site_preference_set(
    section="auth", pref="signup_enabled"
) & is_site_preference_set(section="auth", pref="signup_open")
rules.add_perm("core.can_register", can_register_predicate)

can_change_password_predicate = is_site_preference_set(section="auth", pref="allow_password_change")
rules.add_perm("core.can_change_password", can_change_password_predicate)

# django-invitations
can_invite_predicate = is_site_preference_set(section="auth", pref="invite_enabled")
rules.add_perm("core.can_invite", can_invite_predicate)

# Upload and browse files via CKEditor
upload_files_ckeditor_predicate = has_person & has_global_perm("core.upload_files_ckeditor")
rules.add_perm("core.upload_files_ckeditor", upload_files_ckeditor_predicate)
