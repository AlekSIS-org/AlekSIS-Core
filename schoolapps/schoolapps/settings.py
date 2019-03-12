"""
Django settings for schoolapps project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType, GroupOfNamesType, LDAPGroupType
import logging
from .secure_settings import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = '_89lg!56$d^sf$22cz1ja_f)x9z(nc*y-x*@j4!!vzmlgi*53u'
# Provided by secure_settings

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# PDB debugger option
POST_MORTEM = True

ALLOWED_HOSTS = [
    'info.katharineum.de',
    '178.63.239.184',
    'localhost',
    '127.0.0.1'
]

# Application definition

INSTALLED_APPS = [
    'django_pdb',
    'dashboard.apps.DashboardConfig',
    'aub.apps.AubConfig',
    'untisconnect.apps.UntisconnectConfig',
    'timetable.apps.TimetableConfig',
    'menu.apps.MenuConfig',
    'faq.apps.FaqConfig',
    'dbsettings',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'material',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_pdb.middleware.PdbMiddleware',
]

ROOT_URLCONF = 'schoolapps.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'schoolapps.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
# Provided by secure_settings
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'schoolapps',
#         'USER': 'www-data',
#         'PASSWORD': 'grummelPASS1531',
#         'HOST': '',
#         'PORT': ''
#     },
#     'untis': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'untiskath',
#         'USER': 'www-data',
#         'PASSWORD': 'grummelPASS1531',
#         'HOST': '',
#         'PORT': ''
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'de-de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

# EMAIL
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # Only for DEBUG
# Email settings provided by secure_settings

# TIMETABLE
TIMETABLE_WIDTH = 5
TIMETABLE_HEIGHT = 10
LESSONS = [('8:00', '1.'), ('8:45', '2.'), ('9:45', '3.'), ('10:35', '4.'), ('11:35', '5.'),
           ('12:25', '6.'), ('13:15', '7.'), ('14:05', '8.'), ('14:50', '9.')]
WEEK_DAYS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]

########
# LDAP #
########

# Baseline configuration.
AUTH_LDAP_SERVER_URI = "ldap://127.0.0.1"
AUTH_LDAP_USER_SEARCH = LDAPSearch("dc=skole,dc=skolelinux,dc=no",
                                   ldap.SCOPE_SUBTREE, "(&(objectClass=posixAccount)(uid=%(user)s))")
# or perhaps:
# AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=users,dc=example,dc=com"

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("dc=skole,dc=skolelinux,dc=no", ldap.SCOPE_SUBTREE,
                                    "(&(objectClass=posixGroup))")  # (memberUid=%(user)s)
# '(&(objectClass=*)(memberUid=%(user)s)')
# print(ldap.SCOPE_SUBTREE)
# "(objectClass=organizationalUnit)")
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = "dc=skole,dc=skolelinux,dc=no"
# AUTH_LDAP_DENY_GROUP = "cn=disabled,ou=django,ou=groups,dc=example,dc=com"

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    #      "is_active": "cn=teachers,ou=group,ou=Teachers,dc=skole,dc=skolelinux,dc=no",
    "is_staff": "cn=schoolapps-admins,ou=group,dc=skole,dc=skolelinux,dc=no",
    "is_superuser": "cn=schoolapps-admins,ou=group,dc=skole,dc=skolelinux,dc=no",
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
# AUTH_LDAP_FIND_GROUP_PERMS = True
AUTH_LDAP_MIRROR_GROUPS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Media
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
