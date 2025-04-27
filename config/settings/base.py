# ruff: noqa: ERA001, E501
"""Base settings to build other settings files upon."""
import os
from pathlib import Path

import environs

from main.games.enums import GameRoundStage, GameState

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = BASE_DIR / 'main'

# Create env object
env = environs.Env()

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG')

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env.str('DJANGO_SECRET_KEY')

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# https://docs.djangoproject.com/en/dev/ref/settings/#time-zone
TIME_ZONE = 'UTC'

# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# https://docs.djangoproject.com/en/dev/ref/settings/#site-id

SITE_ID = 1

# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True


# DATABASES
# ------------------------------------------------------------------------------

# Ensure /data exists
os.makedirs(BASE_DIR / 'data', exist_ok=True)

# https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'data' / 'db.sqlite3',
    }
}
DATABASES['default']['ATOMIC_REQUESTS'] = False

# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-DEFAULT_AUTO_FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# REDIS
# ------------------------------------------------------------------------------
REDIS_URL = env.str('REDIS_URL')


# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': REDIS_URL,
    },
}


# SESSIONS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'


# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'

# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'

# https://docs.djangoproject.com/en/dev/ref/settings/#asgi-application
ASGI_APPLICATION = 'config.asgi.application'


# CHANNELS
# ------------------------------------------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        },
    },
}


# APPS
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
]
THIRD_PARTY_APPS = [
    'django_jinja',
    'django_htmx',
    # Add third-party apps here
]
LOCAL_APPS = [
    'main',
    'main.games',
    # Add local apps here
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'main.games.middleware.EnsureSessionMiddleware',
]


# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / 'staticfiles')

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    'config.finders.CustomAppDirectoriesFinder',
]
STATICFILES_IGNORE = ['css/input.css']  # Path relative to STATICFILES_DIRS


# MEDIA
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(BASE_DIR / 'media')

# https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = ''

# Fix permission errors for files uploaded to NAS
FILE_UPLOAD_PERMISSIONS = None


# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django_jinja.jinja2.Jinja2',
        'DIRS': [APPS_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            # https://niwi.nz/django-jinja/latest/#_context_processors_support
            'context_processors': [],
            'globals': {
                'django_htmx_script': 'django_htmx.jinja.django_htmx_script',
                'GameRoundStage': GameRoundStage,
                'GameState': GameState,
            },
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]


# FIXTURES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (str(APPS_DIR / 'fixtures'),)


# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-httponly
SESSION_COOKIE_HTTPONLY = True

# https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-httponly
CSRF_COOKIE_HTTPONLY = True

# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = 'DENY'

# https://docs.djangoproject.com/en/5.0/ref/settings/#csrf-trusted-origins
CSRF_TRUSTED_ORIGINS = []


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {'level': 'DEBUG', 'handlers': ['console']},
}


# APIs
# ------------------------------------------------------------------------------
OPENAI_API_KEY = env.str('OPENAI_API_KEY')
OPENAI_BASE_URL = env.str('OPENAI_BASE_URL')
OPENAI_VISION_MODEL = env.str('OPENAI_VISION_MODEL')
