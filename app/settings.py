"""
Django settings for app project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys

from django.utils.log import DEFAULT_LOGGING
import dj_database_url
from loguru import logger
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
        release=os.environ.get("HEROKU_SLUG_COMMIT"),
    )

    with sentry_sdk.configure_scope() as scope:
        scope.set_tag(
            "heroku-release",
            f"{os.environ.get('HEROKU_APP_NAME')}@{os.environ.get('HEROKU_RELEASE_VERSION')}",
        )

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False
if os.environ.get("DEBUG") == "True":
    DEBUG = True


# Logging setup

if os.environ.get("LOG_SQL") == "True":
    LOGGING = DEFAULT_LOGGING
    LOGGING["handlers"]["sql"] = {
        "level": "DEBUG",
        "class": "logging.StreamHandler",
    }
    LOGGING["loggers"]["django.db.backends"] = {
        "level": "DEBUG",
        "handlers": ["sql"],
    }


if DEBUG:
    lvl = "TRACE"
elif "staging" in os.environ.get("HEROKU_APP_NAME", ""):
    lvl = "DEBUG"
else:
    lvl = "INFO"

fmt = (
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Heroku adds its own timestamp to log lines
if "HEROKU_APP_NAME" not in os.environ:
    fmt = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " + fmt

logger.remove()  # Remove default logger
logger.add(sys.stderr, level=lvl, format=fmt, diagnose=DEBUG)
logger.info("Logging setup complete.")

SECRET_KEY = os.environ.get("SECRET_KEY")
if SECRET_KEY is None:
    if DEBUG:
        SECRET_KEY = "bpt^+o56#_j3p*m7$y2ele39ia^iwb*k05^=km1*)m86z!+lmu"
    else:
        raise EnvironmentError("Please specify a SECRET_KEY in your environment")

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", ".herokuapp.com"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admindocs",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tz_detect",
    "django_extensions",
    "okr.apps.OkrConfig",
    "bot_seo.apps.BotSeoConfig",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "tz_detect.middleware.TimezoneMiddleware",
]

ROOT_URLCONF = "app.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "app.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

if os.environ.get("DATABASE_URL") is not None:
    DATABASES = {"default": dj_database_url.config()}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "de-de"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_L10N = True

USE_TZ = True

TZ_DETECT_COUNTRIES = ("DE", "FR", "GB", "US", "CN", "IN", "JP", "BR", "RU")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
