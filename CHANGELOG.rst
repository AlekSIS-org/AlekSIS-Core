Changelog
=========

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_,
and this project adheres to `Semantic Versioning`_.

Unreleased
----------

Changed
~~~~~~~

* Add verbose names for all preference sections.
* Add verbose names for all openid connect scopes and show them in grant
  view.

Fixed
~~~~~

* Fix broken backup health check

Removed
~~~~~~~

* Drop all leftovers of DataTables.

`2.0b1`_ - 2021-06-01
---------------------

Changed
~~~~~~~

* Rename every occurance of "social account" by "third-party account".
* Use own templates and views for PWA meta and manifest.
* Use term "application" for all authorized OAuth2 applications/tokens.
* Use importlib instead of pkg_resources (no functional changes)

Fixed
~~~~~

* Fix installation documentation (nginx, uWSGI).
* Use a set for data checks registry to prevent double entries.
* Progress page tried to redirect even if the URL is empty.

Removed
~~~~~~~

* Drop django-pwa completely.

`2.0b0`_ - 2021-05-21
---------------------

Added
~~~~~

* Allow defining several search configs for LDAP users and groups
* Use setuptools entrypoints to find apps
* Add django-cachalot as query cache
* Add `syncable_fields` property to `ExtensibleModel to discover fields
  sync backends can write to
* Add `aleksis-admin` script to wrap django-admin with pre-configured settings
* Auto-create persons for users if matching attributes are found
* Add `django-allauth` to allow authentication using OAuth, user registration,
  password changes and password reset
* Add OAuth2 and OpenID Connect provider support
* Add `django-uwsgi` to use uWSGI and Celery in development
* Add loading page for displaying Celery task progress
* Implement generic PDF generation using Chromium
* Support Amazon S3 storage for /media files
* Enable Django REST framework for apps to use at own discretion
* Add method to inject permissions to ExtensibleModels dynamically
* Add helper function which filters queryset by permission and user
* Add generic support for Select 2 with materialize theme
* Add simple message that is shown whenever a page is served from the PWA cache
* Add possibility to upload files using ckeditor
* Show guardians and children on person full page
* Manage object-level permissions in frontend
* Add a generic deletion confirmation view
* Serve Prometheus metrics from app
* Provide system health check endpoint and checks for some components
* Add impersonate button to person view
* Implement a data check system for sanity checks and guided resolution of inconsistencies
* Make the dashboard configurable for users and as default dashboard by admins
* Support dynamic badges in menu items
* Auto-delete old /media files when related model instance is deleted
* Add SortableJS
* Add a widget for links/buttons to other websites

Changed
~~~~~~~

* Make Redis non-optional (see documentation)
* Use Redis as caching and session store to allow horizontal scaling
* Enable PostgreSQL connection pooling
* Use uWSGI to serve /static under development
* Use a token-secured storage as default /media storage
* Rewrite Docker image to serve as generic base image for AlekSIS distributions
* Make Docker image run completely read-only
* Ensure Docker image is compatible with K8s
* Remove legacy file upload functoin; all code is required to use the storage API
* Default search index backend is now Whoosh with Redis storage
* Re-style search result page
* Move notifications to separate page with indicator in menu
* Move to `BigAutoField` for all AlekSIS apps
* Require Django 3.2 and Python 3.9
* Person and group lists can now be filtered
* Allow displaying the default widget to anonymous users

Fixed
~~~~~

* Correct behavious of celery-beat in development
* Fix precaching of offline fallback page
* Use correct styling for language selector
* Rewrite notification e-mail template for AlekSIS
* Global search now obeys permissions correctly
* Improve performance of favicon generation
* Dashboard widgets now handle exceptions gracefully
* Roboto font was not available for serving locally

Removed
~~~~~~~

* Dropped support for other search backends than Whoosh
* Drop django-middleware-global-request completely

`2.0a2`_ - 2020-05-04
---------------------

Added
~~~~~

* Frontend-ased announcement management.
* Auto-create Person on User creation.
* Select primary group by pattern if unset.
* Shortcut to personal information page.
* Support for defining group types.
* Add description to Person.
* age_at method and age property to Person.
* Synchronise AlekSIS groups with Django groups.
* Add celery worker, celery-beat worker and celery broker to docker-compose setup.
* Global search.
* License information page.
* Roles and permissions.
* User preferences.
* Additional fields for people per group.
* Support global permission flags by LDAP group.
* Persistent announcements.
* Custom menu entries (e.g. in footer).
* New logo for AlekSIS.
* Two factor authentication with Yubikey, OTP or SMS.
* Devs: Add ExtensibleModel to allow apps to add fields, properties.
* Devs: Support multiple recipient object for one announcement.

Changes
~~~~~~~

* Make short_name for group optional.
* Generalised live loading of widgets for dashboard.
* Devs: Add some CSS helper classes for colours.
* Devs: Mandate use of AlekSIS base model.
* Devs: Drop import_ref field(s); apps shold now define their own reference fields.

Fixed
~~~~~

* DateTimeField Announcement.valid_from received a naive datetime.
* Enable SASS processor in production.
* Fix too short fields.
* Load select2 locally.

`2.0a1`_ - 2020-02-01
---------------------

Added
~~~~~

* Migrate to MaterializeCSS.
* Dashboard.
* Notifications via SMS (Twilio), Email or on the dashboard.
* Admin interface.
* Turn into installable, progressive web app.
* Devs: Background Tasks with Celery.

Changed
~~~~~~~

* Customisable save_button template.
* Redesign error pages.

Fixed
~~~~~

* setup_data no longer forces database connection.

`1.0a4`_ - 2019-11-25
---------------------

Added
~~~~~

* Two-factor authentication with TOTP (Google Authenticator), Yubikey, SMS
  and phone call.
* Devs: CRUDMixin provides a crud_event relation that returns all CRUD
  events for an object.

`1.0a2`_ - 2019-11-11
---------------------

Added
~~~~~

* Devs: Add ExtensibleModel to allow injection of methods and properties into models.


`1.0a1`_ - 2019-09-17
---------------------

Added
~~~~~

* Devs: Add API to get an audit trail for any school-related object.
* Devs: Provide template snippet to display an audit trail.
* Devs: Provide base template for views that allow browsing back/forth.
* Add management command and Cron job for full backups.
* Add system status overview page.
* Allow enabling and disabling maintenance mode from frontend.
* Allow editing the dates of the current school term.
* Add logo to school information.
* Allow editing school information.
* Ensure all actions are reverted if something fails (atomic requests).

Fixed
~~~~~

* Only show active persons in group and persons views.
* Silence KeyError in get_dict template tag.
* Use bootstrap buttons everywhere.

.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html

.. _1.0a1: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/1.0a1
.. _1.0a2: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/1.0a2
.. _1.0a4: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/1.0a4
.. _2.0a1: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/2.0a1
.. _2.0a2: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/2.0a2
.. _2.0b0: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/2.0b0
.. _2.0b1: https://edugit.org/AlekSIS/Official/AlekSIS/-/tags/2.0b1
