import os
from glob import glob

from django.utils.translation import gettext_lazy as _

from dynaconf import LazySettings

from .util.core_helpers import (
    get_app_packages,
    lazy_get_favicon_url,
    lazy_preference,
    merge_app_settings,
)

IN_PYTEST = "PYTEST_CURRENT_TEST" in os.environ or "TOX_ENV_DIR" in os.environ

ENVVAR_PREFIX_FOR_DYNACONF = "ALEKSIS"
DIRS_FOR_DYNACONF = ["/etc/aleksis"]

SETTINGS_FILE_FOR_DYNACONF = []
for directory in DIRS_FOR_DYNACONF:
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.ini"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.yaml"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.toml"))

_settings = LazySettings(
    ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
    SETTINGS_FILE_FOR_DYNACONF=SETTINGS_FILE_FOR_DYNACONF,
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SILENCED_SYSTEM_CHECKS = []

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _settings.get("secret_key", "DoNotUseInProduction")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _settings.get("maintenance.debug", False)
INTERNAL_IPS = _settings.get("maintenance.internal_ips", [])
DEBUG_TOOLBAR_CONFIG = {
    "RENDER_PANELS": True,
    "SHOW_COLLAPSED": True,
    "JQUERY_URL": "",
    "SHOW_TOOLBAR_CALLBACK": "aleksis.core.util.core_helpers.dt_show_toolbar",
    "DISABLE_PANELS": {},
}

DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.logging.LoggingPanel",
    "debug_toolbar.panels.profiling.ProfilingPanel",
    "django_uwsgi.panels.UwsgiPanel",
]

UWSGI = {
    "module": "aleksis.core.wsgi",
}
UWSGI_SERVE_STATIC = True
UWSGI_SERVE_MEDIA = True

ALLOWED_HOSTS = _settings.get("http.allowed_hosts", [])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_uwsgi",
    "django_extensions",
    "guardian",
    "rules.apps.AutodiscoverRulesConfig",
    "haystack",
    "polymorphic",
    "dj_cleavejs.apps.DjCleaveJSConfig",
    "django_global_request",
    "dbbackup",
    "django_celery_beat",
    "django_celery_results",
    "celery_progress",
    "health_check.contrib.celery",
    "djcelery_email",
    "celery_haystack",
    "settings_context_processor",
    "sass_processor",
    "django_any_js",
    "django_yarnpkg",
    "django_tables2",
    "maintenance_mode",
    "menu_generator",
    "reversion",
    "phonenumber_field",
    "debug_toolbar",
    "django_prometheus",
    "django_select2",
    "hattori",
    "templated_email",
    "html2text",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "django_otp",
    "otp_yubikey",
    "aleksis.core",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "invitations",
    "health_check",
    "health_check.db",
    "health_check.cache",
    "health_check.storage",
    "health_check.contrib.psutil",
    "health_check.contrib.migrations",
    "dynamic_preferences",
    "dynamic_preferences.users.apps.UserPreferencesConfig",
    "impersonate",
    "two_factor",
    "material",
    "pwa",
    "ckeditor",
    "ckeditor_uploader",
    "django_js_reverse",
    "colorfield",
    "django_bleach",
    "favicon",
    "django_filters",
]

merge_app_settings("INSTALLED_APPS", INSTALLED_APPS, True)
INSTALLED_APPS += get_app_packages()

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_yarnpkg.finders.NodeModulesFinder",
    "sass_processor.finders.CssFinder",
]

MIDDLEWARE = [
    #    'django.middleware.cache.UpdateCacheMiddleware',
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.http.ConditionalGetMiddleware",
    "django_global_request.middleware.GlobalRequestMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "impersonate.middleware.ImpersonateMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "maintenance_mode.middleware.MaintenanceModeMiddleware",
    "aleksis.core.util.middlewares.EnsurePersonMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
    #    'django.middleware.cache.FetchFromCacheMiddleware'
]

ROOT_URLCONF = "aleksis.core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "maintenance_mode.context_processors.maintenance_mode",
                "settings_context_processor.context_processors.settings",
                "dynamic_preferences.processors.global_preferences",
                "aleksis.core.util.core_helpers.custom_information_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "aleksis.core.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": _settings.get("database.name", "aleksis"),
        "USER": _settings.get("database.username", "aleksis"),
        "PASSWORD": _settings.get("database.password", None),
        "HOST": _settings.get("database.host", "127.0.0.1"),
        "PORT": _settings.get("database.port", "5432"),
        "CONN_MAX_AGE": _settings.get("database.conn_max_age", None),
    }
}

merge_app_settings("DATABASES", DATABASES, False)

REDIS_HOST = _settings.get("redis.host", "localhost")
REDIS_PORT = _settings.get("redis.port", 6379)
REDIS_DB = _settings.get("redis.database", 0)
REDIS_PASSWORD = _settings.get("redis.password", None)
REDIS_USER = _settings.get("redis.user", None if REDIS_PASSWORD is None else "default")

REDIS_URL = (
    f"redis://{REDIS_USER+':'+REDIS_PASSWORD+'@' if REDIS_USER else ''}"
    f"{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
)

if _settings.get("caching.redis.enabled", not IN_PYTEST):
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _settings.get("caching.redis.address", REDIS_URL),
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient",},
        }
    }
    if REDIS_PASSWORD:
        CACHES["default"]["OPTIONS"]["PASSWORD"] = REDIS_PASSWORD
    DJANGO_REDIS_IGNORE_EXCEPTIONS = True
    DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True
else:
    CACHES = {
        "default": {
            # Use uWSGI if available (will auot-fallback to LocMemCache)
            "BACKEND": "django_uwsgi.cache.UwsgiCache"
        }
    }

INSTALLED_APPS.append("cachalot")
DEBUG_TOOLBAR_PANELS.append("cachalot.panels.CachalotPanel")
CACHALOT_TIMEOUT = _settings.get("caching.cachalot.timeout", None)
CACHALOT_DATABASES = set(["default"])
SILENCED_SYSTEM_CHECKS += ["cachalot.W001", "cachalot.E003"]

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

AUTH_INITIAL_SUPERUSER = {
    "username": _settings.get("auth.superuser.username", "admin"),
    "password": _settings.get("auth.superuser.password", "admin"),
    "email": _settings.get("auth.superuser.email", "root@example.com"),
}

# Authentication backends are dynamically populated
AUTHENTICATION_BACKENDS = []

# Configuration for django-allauth.

# Use custom adapter to override some behaviour, i.e. honour the LDAP backend
SOCIALACCOUNT_ADAPTER = "aleksis.core.util.auth_helpers.OurSocialAccountAdapter"

# Get django-allauth providers from config
_SOCIALACCOUNT_PROVIDERS = _settings.get("auth.providers", None)
if _SOCIALACCOUNT_PROVIDERS:
    SOCIALACCOUNT_PROVIDERS = _SOCIALACCOUNT_PROVIDERS.to_dict()

    # Add configured social auth providers to INSTALLED_APPS
    for provider, config in SOCIALACCOUNT_PROVIDERS.items():
        INSTALLED_APPS.append(f"allauth.socialaccount.providers.{provider}")
        for k in config:
            kupper = k.upper()
            if k != kupper:
                config[kupper] = config[k]
                del config[k]

# Configure custom forms

ACCOUNT_FORMS = {
    "signup": "aleksis.core.forms.AccountRegisterForm",
}

# Require password confirmation
SIGNUP_PASSWORD_ENTER_TWICE = True

INVITATIONS_GONE_ON_ACCEPT_ERROR = False

# Allow login by either username or email
ACCOUNT_AUTHENTICATION_METHOD = _settings.get("auth.registration.method", "username_email")

# Require email address to sign up
ACCOUNT_EMAIL_REQUIRED = _settings.get("auth.registration.email_required", True)
SOCIALACCOUNT_EMAIL_REQUIRED = False

# Require email verification after sigm up
ACCOUNT_EMAIL_VERIFICATION = _settings.get("auth.registration.email_verification", "mandatory")
SOCIALACCOUNT_EMAIL_VERIFICATION = False

# Email subject prefix for verification mails
ACCOUNT_EMAIL_SUBJECT_PREFIX = _settings.get("auth.registration.subject", "[AlekSIS] ")

# Max attempts before login timeout
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = _settings.get("auth.login.login_limit", 5)

# Login timeout after max attempts in seconds
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = _settings.get("auth.login.login_timeout", 300)

# Email confirmation field in form
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True

# Enforce uniqueness of email addresses
ACCOUNT_UNIQUE_EMAIL = _settings.get("auth.login.registration.unique_email", True)

# Configuration for django-invitations

ACCOUNT_ADAPTER = "invitations.models.InvitationsAdapter"

INVITATIONS_INVITATION_EXPIRY = _settings.get("auth.invitation.expiry", 3)

INVITATIONS_INVITATION_ONLY = lazy_preference("auth", "invite_only")

INVITATIONS_EMAIL_SUBJECT_PREFIX = ACCOUNT_EMAIL_SUBJECT_PREFIX

INVITATIONS_INVITATION_MODEL = "core.PersonInvitation"

# LDAP config

if _settings.get("ldap.uri", None):
    # LDAP dependencies are not necessarily installed, so import them here
    import ldap  # noqa
    from django_auth_ldap.config import (
        LDAPSearch,
        LDAPSearchUnion,
        NestedGroupOfNamesType,
        NestedGroupOfUniqueNamesType,
        PosixGroupType,
    )

    # Enable Django's integration to LDAP
    AUTHENTICATION_BACKENDS.append("aleksis.core.util.ldap.LDAPBackend")

    AUTH_LDAP_SERVER_URI = _settings.get("ldap.uri")

    # Optional: non-anonymous bind
    if _settings.get("ldap.bind.dn", None):
        AUTH_LDAP_BIND_DN = _settings.get("ldap.bind.dn")
        AUTH_LDAP_BIND_PASSWORD = _settings.get("ldap.bind.password")

    # Keep local password for users to be required to proveide their old password on change
    AUTH_LDAP_SET_USABLE_PASSWORD = True

    # Keep bound as the authenticating user
    # Ensures proper read permissions, and ability to change password without admin
    AUTH_LDAP_BIND_AS_AUTHENTICATING_USER = True

    # The TOML config might contain either one table or an array of tables
    _AUTH_LDAP_USER_SETTINGS = _settings.get("ldap.users.search")
    if not isinstance(_AUTH_LDAP_USER_SETTINGS, list):
        _AUTH_LDAP_USER_SETTINGS = [_AUTH_LDAP_USER_SETTINGS]

    # Search attributes to find users by username
    AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
        *[
            LDAPSearch(entry["base"], ldap.SCOPE_SUBTREE, entry.get("filter", "(uid=%(user)s)"),)
            for entry in _AUTH_LDAP_USER_SETTINGS
        ]
    )

    # Mapping of LDAP attributes to Django model fields
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": _settings.get("ldap.users.map.first_name", "givenName"),
        "last_name": _settings.get("ldap.users.map.last_name", "sn"),
        "email": _settings.get("ldap.users.map.email", "mail"),
    }

    # Discover flags by LDAP groups
    if _settings.get("ldap.groups.search", None):
        group_type = _settings.get("ldap.groups.type", "groupOfNames")

        # The TOML config might contain either one table or an array of tables
        _AUTH_LDAP_GROUP_SETTINGS = _settings.get("ldap.groups.search")
        if not isinstance(_AUTH_LDAP_GROUP_SETTINGS, list):
            _AUTH_LDAP_GROUP_SETTINGS = [_AUTH_LDAP_GROUP_SETTINGS]

        AUTH_LDAP_GROUP_SEARCH = LDAPSearchUnion(
            *[
                LDAPSearch(
                    entry["base"],
                    ldap.SCOPE_SUBTREE,
                    entry.get("filter", f"(objectClass={group_type})"),
                )
                for entry in _AUTH_LDAP_GROUP_SETTINGS
            ]
        )

        _group_type = _settings.get("ldap.groups.type", "groupOfNames").lower()
        if _group_type == "groupofnames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType()
        elif _group_type == "groupofuniquenames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfUniqueNamesType()
        elif _group_type == "posixgroup":
            AUTH_LDAP_GROUP_TYPE = PosixGroupType()

        AUTH_LDAP_USER_FLAGS_BY_GROUP = {}
        for _flag in ["is_active", "is_staff", "is_superuser"]:
            _dn = _settings.get(f"ldap.groups.flags.{_flag}", None)
            if _dn:
                AUTH_LDAP_USER_FLAGS_BY_GROUP[_flag] = _dn

        # Backend admin requires superusers to also be staff members
        if (
            "is_superuser" in AUTH_LDAP_USER_FLAGS_BY_GROUP
            and "is_staff" not in AUTH_LDAP_USER_FLAGS_BY_GROUP
        ):
            AUTH_LDAP_USER_FLAGS_BY_GROUP["is_staff"] = AUTH_LDAP_USER_FLAGS_BY_GROUP[
                "is_superuser"
            ]

CUSTOM_AUTHENTICATION_BACKENDS = []
merge_app_settings("AUTHENTICATION_BACKENDS", CUSTOM_AUTHENTICATION_BACKENDS)

# Add ModelBckend last so all other backends get a chance
# to verify passwords first
AUTHENTICATION_BACKENDS.append("django.contrib.auth.backends.ModelBackend")

# Authentication backend for django-allauth.
AUTHENTICATION_BACKENDS.append("allauth.account.auth_backends.AuthenticationBackend")

# Structure of items: backend, URL name, icon name, button title
ALTERNATIVE_LOGIN_VIEWS = []
merge_app_settings("ALTERNATIVE_LOGIN_VIEWS", ALTERNATIVE_LOGIN_VIEWS, True)

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
    ("fr", _("French")),
    ("nb", _("Norwegian (bokmål)")),
]
LANGUAGE_CODE = _settings.get("l10n.lang", "en")
TIME_ZONE = _settings.get("l10n.tz", "UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/


STATIC_URL = _settings.get("static.url", "/static/")
MEDIA_URL = _settings.get("media.url", "/media/")

LOGIN_REDIRECT_URL = "index"
LOGOUT_REDIRECT_URL = "index"

STATIC_ROOT = _settings.get("static.root", os.path.join(BASE_DIR, "static"))
MEDIA_ROOT = _settings.get("media.root", os.path.join(BASE_DIR, "media"))
NODE_MODULES_ROOT = _settings.get("node_modules.root", os.path.join(BASE_DIR, "node_modules"))

YARN_INSTALLED_APPS = [
    "cleave.js",
    "@fontsource/roboto",
    "datatables",
    "jquery",
    "materialize-css",
    "material-design-icons-iconfont",
    "select2",
    "select2-materialize",
    "paper-css",
    "jquery-sortablejs",
    "sortablejs",
]

merge_app_settings("YARN_INSTALLED_APPS", YARN_INSTALLED_APPS, True)

CLEAVE_JS = "cleave.js/dist/cleave.min.js"

JS_URL = _settings.get("js_assets.url", STATIC_URL)
JS_ROOT = _settings.get("js_assets.root", NODE_MODULES_ROOT + "/node_modules")

SELECT2_CSS = JS_URL + "/select2/dist/css/select2.min.css"
SELECT2_JS = JS_URL + "/select2/dist/js/select2.min.js"
SELECT2_I18N_PATH = JS_URL + "/select2/dist/js/i18n"

ANY_JS = {
    "DataTables": {"js_url": JS_URL + "/datatables/media/js/jquery.dataTables.min.js"},
    "materialize": {"js_url": JS_URL + "/materialize-css/dist/js/materialize.min.js"},
    "jQuery": {"js_url": JS_URL + "/jquery/dist/jquery.min.js"},
    "material-design-icons": {
        "css_url": JS_URL + "/material-design-icons-iconfont/dist/material-design-icons.css"
    },
    "paper-css": {"css_url": JS_URL + "/paper-css/paper.min.css"},
    "select2-materialize": {
        "css_url": JS_URL + "/select2-materialize/select2-materialize.css",
        "js_url": JS_URL + "/select2-materialize/index.js",
    },
    "sortablejs": {"js_url": JS_URL + "/sortablejs/Sortable.min.js"},
    "jquery-sortablejs": {"js_url": JS_URL + "/jquery-sortablejs/jquery-sortable.js"},
    "Roboto": {"css_url": JS_URL + "/@fontsource/roboto/index.css"},
}

merge_app_settings("ANY_JS", ANY_JS, True)

SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_AUTO_INCLUDE = False
SASS_PROCESSOR_CUSTOM_FUNCTIONS = {
    "get-colour": "aleksis.core.util.sass_helpers.get_colour",
    "get-preference": "aleksis.core.util.sass_helpers.get_preference",
}
SASS_PROCESSOR_INCLUDE_DIRS = [
    _settings.get("materialize.sass_path", JS_ROOT + "/materialize-css/sass/"),
    STATIC_ROOT + "/materialize-css/sass/",
    STATIC_ROOT,
]

ADMINS = _settings.get("contact.admins", [])
SERVER_EMAIL = _settings.get("contact.from", "root@localhost")
DEFAULT_FROM_EMAIL = _settings.get("contact.from", "root@localhost")
MANAGERS = _settings.get("contact.admins", [])

if _settings.get("mail.server.host", None):
    EMAIL_HOST = _settings.get("mail.server.host")
    EMAIL_USE_TLS = _settings.get("mail.server.tls", False)
    EMAIL_USE_SSL = _settings.get("mail.server.ssl", False)
    if _settings.get("mail.server.port", None):
        EMAIL_PORT = _settings.get("mail.server.port")
    if _settings.get("mail.server.user", None):
        EMAIL_HOST_USER = _settings.get("mail.server.user")
        EMAIL_HOST_PASSWORD = _settings.get("mail.server.password")

TEMPLATED_EMAIL_BACKEND = "templated_email.backends.vanilla_django"
TEMPLATED_EMAIL_AUTO_PLAIN = True


TEMPLATE_VISIBLE_SETTINGS = ["ADMINS", "DEBUG"]

DYNAMIC_PREFERENCES = {
    "REGISTRY_MODULE": "preferences",
}

MAINTENANCE_MODE = _settings.get("maintenance.enabled", None)
MAINTENANCE_MODE_IGNORE_IP_ADDRESSES = _settings.get(
    "maintenance.ignore_ips", _settings.get("maintenance.internal_ips", [])
)
MAINTENANCE_MODE_GET_CLIENT_IP_ADDRESS = "ipware.ip.get_ip"
MAINTENANCE_MODE_IGNORE_SUPERUSER = True
MAINTENANCE_MODE_STATE_FILE_NAME = _settings.get(
    "maintenance.statefile", "maintenance_mode_state.txt"
)
MAINTENANCE_MODE_STATE_BACKEND = "maintenance_mode.backends.DefaultStorageBackend"

DBBACKUP_STORAGE = _settings.get("backup.storage", "django.core.files.storage.FileSystemStorage")
DBBACKUP_STORAGE_OPTIONS = {"location": _settings.get("backup.location", "/var/backups/aleksis")}
DBBACKUP_CLEANUP_KEEP = _settings.get("backup.database.keep", 10)
DBBACKUP_CLEANUP_KEEP_MEDIA = _settings.get("backup.media.keep", 10)
DBBACKUP_GPG_RECIPIENT = _settings.get("backup.gpg_recipient", None)
DBBACKUP_COMPRESS_DB = _settings.get("backup.database.compress", True)
DBBACKUP_ENCRYPT_DB = _settings.get("backup.database.encrypt", DBBACKUP_GPG_RECIPIENT is not None)
DBBACKUP_COMPRESS_MEDIA = _settings.get("backup.media.compress", True)
DBBACKUP_ENCRYPT_MEDIA = _settings.get("backup.media.encrypt", DBBACKUP_GPG_RECIPIENT is not None)
DBBACKUP_CLEANUP_DB = _settings.get("backup.database.clean", True)
DBBACKUP_CLEANUP_MEDIA = _settings.get("backup.media.clean", True)
DBBACKUP_CONNECTOR_MAPPING = {
    "django_prometheus.db.backends.postgresql": "dbbackup.db.postgresql.PgDumpConnector",
}

if _settings.get("backup.storage.type", "").lower() == "s3":
    DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    DBBACKUP_STORAGE_OPTIONS = {
        key: value for (key, value) in _settings.get("backup.storage.s3").items()
    }

IMPERSONATE = {"USE_HTTP_REFERER": True, "REQUIRE_SUPERUSER": True, "ALLOW_SUPERUSER": True}

DJANGO_TABLES2_TEMPLATE = "django_tables2/materialize.html"

ANONYMIZE_ENABLED = _settings.get("maintenance.anonymisable", True)

LOGIN_URL = "two_factor:login"

if _settings.get("2fa.call.enabled", False):
    if "two_factor.middleware.threadlocals.ThreadLocals" not in MIDDLEWARE:
        MIDDLEWARE.insert(
            MIDDLEWARE.index("django_otp.middleware.OTPMiddleware") + 1,
            "two_factor.middleware.threadlocals.ThreadLocals",
        )
    TWO_FACTOR_CALL_GATEWAY = "two_factor.gateways.twilio.gateway.Twilio"

if _settings.get("2fa.sms.enabled", False):
    if "two_factor.middleware.threadlocals.ThreadLocals" not in MIDDLEWARE:
        MIDDLEWARE.insert(
            MIDDLEWARE.index("django_otp.middleware.OTPMiddleware") + 1,
            "two_factor.middleware.threadlocals.ThreadLocals",
        )
    TWO_FACTOR_SMS_GATEWAY = "two_factor.gateways.twilio.gateway.Twilio"

if _settings.get("twilio.sid", None):
    TWILIO_SID = _settings.get("twilio.sid")
    TWILIO_TOKEN = _settings.get("twilio.token")
    TWILIO_CALLER_ID = _settings.get("twilio.callerid")

CELERY_BROKER_URL = _settings.get("celery.broker", REDIS_URL)
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

if _settings.get("celery.email", False):
    EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

if _settings.get("dev.uwsgi.celery", DEBUG):
    concurrency = _settings.get("celery.uwsgi.concurrency", 2)
    UWSGI.setdefault("attach-daemon", [])
    UWSGI["attach-daemon"].append(f"celery -A aleksis.core worker --concurrency={concurrency}")
    UWSGI["attach-daemon"].append("celery -A aleksis.core beat")

PWA_APP_NAME = lazy_preference("general", "title")
PWA_APP_DESCRIPTION = lazy_preference("general", "description")
PWA_APP_THEME_COLOR = lazy_preference("theme", "primary")
PWA_APP_BACKGROUND_COLOR = "#ffffff"
PWA_APP_DISPLAY = "standalone"
PWA_APP_ORIENTATION = "any"
PWA_APP_ICONS = [
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="android", default=STATIC_URL + "icons/android_192.png"
        ),
        "sizes": "192x192",
    },
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=512, rel="android", default=STATIC_URL + "icons/android_512.png"
        ),
        "sizes": "512x512",
    },
]
PWA_APP_ICONS_APPLE = [
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="apple", default=STATIC_URL + "icons/apple_76.png"
        ),
        "sizes": "76x76",
    },
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="apple", default=STATIC_URL + "icons/apple_114.png"
        ),
        "sizes": "114x114",
    },
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="apple", default=STATIC_URL + "icons/apple_152.png"
        ),
        "sizes": "152x152",
    },
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="apple", default=STATIC_URL + "icons/apple_180.png"
        ),
        "sizes": "180x180",
    },
]
PWA_APP_SPLASH_SCREEN = [
    {
        "src": lazy_get_favicon_url(
            title="pwa_icon", size=192, rel="apple", default=STATIC_URL + "icons/apple_180.png"
        ),
        "media": (
            "(device-width: 320px) and (device-height: 568px) and" "(-webkit-device-pixel-ratio: 2)"
        ),
    }
]


PWA_SERVICE_WORKER_PATH = os.path.join(STATIC_ROOT, "js", "serviceworker.js")

SITE_ID = 1

CKEDITOR_CONFIGS = {
    "default": {
        "toolbar_Basic": [["Source", "-", "Bold", "Italic"]],
        "toolbar_Full": [
            {
                "name": "document",
                "items": ["Source", "-", "Save", "NewPage", "Preview", "Print", "-", "Templates"],
            },
            {
                "name": "clipboard",
                "items": [
                    "Cut",
                    "Copy",
                    "Paste",
                    "PasteText",
                    "PasteFromWord",
                    "-",
                    "Undo",
                    "Redo",
                ],
            },
            {"name": "editing", "items": ["Find", "Replace", "-", "SelectAll"]},
            {
                "name": "insert",
                "items": [
                    "Image",
                    "Table",
                    "HorizontalRule",
                    "Smiley",
                    "SpecialChar",
                    "PageBreak",
                    "Iframe",
                ],
            },
            "/",
            {
                "name": "basicstyles",
                "items": [
                    "Bold",
                    "Italic",
                    "Underline",
                    "Strike",
                    "Subscript",
                    "Superscript",
                    "-",
                    "RemoveFormat",
                ],
            },
            {
                "name": "paragraph",
                "items": [
                    "NumberedList",
                    "BulletedList",
                    "-",
                    "Outdent",
                    "Indent",
                    "-",
                    "Blockquote",
                    "CreateDiv",
                    "-",
                    "JustifyLeft",
                    "JustifyCenter",
                    "JustifyRight",
                    "JustifyBlock",
                    "-",
                    "BidiLtr",
                    "BidiRtl",
                    "Language",
                ],
            },
            {"name": "links", "items": ["Link", "Unlink", "Anchor"]},
            "/",
            {"name": "styles", "items": ["Styles", "Format", "Font", "FontSize"]},
            {"name": "colors", "items": ["TextColor", "BGColor"]},
            {"name": "tools", "items": ["Maximize", "ShowBlocks"]},
            {"name": "about", "items": ["About"]},
            {"name": "customtools", "items": ["Preview", "Maximize",]},
        ],
        "toolbar": "Full",
        "tabSpaces": 4,
        "extraPlugins": ",".join(
            [
                "uploadimage",
                "div",
                "autolink",
                "autoembed",
                "embedsemantic",
                "autogrow",
                # 'devtools',
                "widget",
                "lineutils",
                "clipboard",
                "dialog",
                "dialogui",
                "elementspath",
            ]
        ),
    }
}

# Upload path for CKEditor. Relative to MEDIA_ROOT.
CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"

# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ["p", "b", "i", "u", "em", "strong", "a", "div"]

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ["href", "title", "style"]

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = ["font-family", "font-weight", "text-decoration", "font-variant"]

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "verbose"},},
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s: %(message)s"}},
    "root": {"handlers": ["console"], "level": _settings.get("logging.level", "WARNING"),},
}

# Rules and permissions

GUARDIAN_RAISE_403 = True
ANONYMOUS_USER_NAME = None

SILENCED_SYSTEM_CHECKS.append("guardian.W001")

# Append authentication backends
AUTHENTICATION_BACKENDS.append("rules.permissions.ObjectPermissionBackend")

HAYSTACK_BACKEND_SHORT = _settings.get("search.backend", "simple")

if HAYSTACK_BACKEND_SHORT == "simple":
    HAYSTACK_CONNECTIONS = {
        "default": {"ENGINE": "haystack.backends.simple_backend.SimpleEngine",},
    }
elif HAYSTACK_BACKEND_SHORT == "xapian":
    HAYSTACK_CONNECTIONS = {
        "default": {
            "ENGINE": "xapian_backend.XapianEngine",
            "PATH": _settings.get("search.index", os.path.join(BASE_DIR, "xapian_index")),
        },
    }
elif HAYSTACK_BACKEND_SHORT == "whoosh":
    HAYSTACK_CONNECTIONS = {
        "default": {
            "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
            "PATH": _settings.get("search.index", os.path.join(BASE_DIR, "whoosh_index")),
        },
    }

HAYSTACK_SIGNAL_PROCESSOR = "celery_haystack.signals.CelerySignalProcessor"
CELERY_HAYSTACK_IGNORE_RESULT = True

HAYSTACK_SEARCH_RESULTS_PER_PAGE = 10

DJANGO_EASY_AUDIT_WATCH_REQUEST_EVENTS = False

HEALTH_CHECK = {
    "DISK_USAGE_MAX": _settings.get("health.disk_usage_max_percent", 90),
    "MEMORY_MIN": _settings.get("health.memory_min_mb", 500),
}

DBBACKUP_CHECK_SECONDS = _settings.get("backup.database.check_seconds", 7200)
MEDIABACKUP_CHECK_SECONDS = _settings.get("backup.media.check_seconds", 7200)

PROMETHEUS_EXPORT_MIGRATIONS = False

if _settings.get("storage.type", "").lower() == "s3":
    INSTALLED_APPS.append("storages")

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

    if _settings.get("storage.s3.static.enabled", False):
        STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"
        AWS_STORAGE_BUCKET_NAME_STATIC = _settings.get("storage.s3.static.bucket_name", "")
        AWS_S3_MAX_AGE_SECONDS_CACHED_STATIC = _settings.get(
            "storage.s3.static.max_age_seconds", 24 * 60 * 60
        )

    AWS_REGION = _settings.get("storage.s3.region_name", "")
    AWS_ACCESS_KEY_ID = _settings.get("storage.s3.access_key", "")
    AWS_SECRET_ACCESS_KEY = _settings.get("storage.s3.secret_key", "")
    AWS_SESSION_TOKEN = _settings.get("storage.s3.session_token", "")
    AWS_STORAGE_BUCKET_NAME = _settings.get("storage.s3.bucket_name", "")
    AWS_LOCATION = _settings.get("storage.s3.location", "")
    AWS_S3_ADDRESSING_STYLE = _settings.get("storage.s3.addressing_style", "auto")
    AWS_S3_ENDPOINT_URL = _settings.get("storage.s3.endpoint_url", "")
    AWS_S3_KEY_PREFIX = _settings.get("storage.s3.key_prefix", "")
    AWS_S3_BUCKET_AUTH = _settings.get("storage.s3.bucket_auth", True)
    AWS_S3_MAX_AGE_SECONDS = _settings.get("storage.s3.max_age_seconds", 24 * 60 * 60)
    AWS_S3_PUBLIC_URL = _settings.get("storage.s3.public_url", "")
    AWS_S3_REDUCED_REDUNDANCY = _settings.get("storage.s3.reduced_redundancy", False)
    AWS_S3_CONTENT_DISPOSITION = _settings.get("storage.s3.content_disposition", "")
    AWS_S3_CONTENT_LANGUAGE = _settings.get("storage.s3.content_language", "")
    AWS_S3_METADATA = _settings.get("storage.s3.metadata", {})
    AWS_S3_ENCRYPT_KEY = _settings.get("storage.s3.encrypt_key", False)
    AWS_S3_KMS_ENCRYPTION_KEY_ID = _settings.get("storage.s3.kms_encryption_key_id", "")
    AWS_S3_GZIP = _settings.get("storage.s3.gzip", True)
    AWS_S3_SIGNATURE_VERSION = _settings.get("storage.s3.signature_version", None)
    AWS_S3_FILE_OVERWRITE = _settings.get("storage.s3.file_overwrite", False)
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

SASS_PROCESSOR_STORAGE = DEFAULT_FILE_STORAGE

# Add django-cleanup after all apps to ensure that it gets all signals as last app
INSTALLED_APPS.append("django_cleanup.apps.CleanupConfig")
