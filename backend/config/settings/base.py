import os
from pathlib import Path
import environ

ROOT_DIR = Path(__file__).resolve().parents[3]
env = environ.Env(
    DJANGO_SECRET_KEY=(str, 'change-me'),
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    DJANGO_LOG_LEVEL=(str, 'INFO'),
    POSTGRES_DB=(str, 'alice_wonder_nails'),
    POSTGRES_USER=(str, 'alice_local'),
    POSTGRES_PASSWORD=(str, 'change-me'),
    POSTGRES_HOST=(str, 'localhost'),
    POSTGRES_PORT=(int, 5432),
    EMAIL_BACKEND=(str, 'django.core.mail.backends.console.EmailBackend'),
    EMAIL_HOST=(str, ''),
    EMAIL_PORT=(int, 587),
    EMAIL_HOST_USER=(str, ''),
    EMAIL_HOST_PASSWORD=(str, ''),
    EMAIL_USE_TLS=(bool, True),
    DEFAULT_FROM_EMAIL=(str, 'noreply@example.local'),
)

env.read_env(ROOT_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')
DEBUG = env('DJANGO_DEBUG')
ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')
LOG_LEVEL = env('DJANGO_LOG_LEVEL')

EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = env('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'apps.accounts',
    'apps.core',
    'apps.api',
    'apps.customers',
    'apps.business',
    'apps.catalog',
    'apps.pricing',
    'apps.cart',
    'apps.orders',
    'apps.legal',
    'apps.consent',
    'apps.auditlog',
    'apps.shipping',
    'apps.payments',
    'apps.checkout',
]

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': env('POSTGRES_HOST'),
        'PORT': env('POSTGRES_PORT'),
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
    },
}

# Security: Foundation Hardening (Basis für alle Umgebungen)
# Clickjacking Protection
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True

# Session & CSRF Cookies (lokal für HTTP, production.py verschärft)
SESSION_COOKIE_HTTPONLY = True  # JS kann Session-Cookie nicht lesen (mandatory)
CSRF_COOKIE_HTTPONLY = False     # Frontend braucht CSRF-Token (für Shop-Flows)
SESSION_COOKIE_SAMESITE = 'Lax'  # Lokal/Dev permissiv (production.py kann überschreiben)
CSRF_COOKIE_SAMESITE = 'Lax'     # Lokal/Dev permissiv (production.py kann überschreiben)

# CSRF Trusted Origins (production.py muss aus ENV gesetzt werden)
CSRF_TRUSTED_ORIGINS = []
