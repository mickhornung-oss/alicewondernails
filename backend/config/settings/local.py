from .base import *  # noqa
import os

DEBUG = True

# Local Development: HTTP allowed (nicht secure)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Local Development: HSTS disabled (only for HTTPS)
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Local Development: ALLOWED_HOSTS permissiv
if 'DJANGO_ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = env('DJANGO_ALLOWED_HOSTS')
else:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000', 'testserver']

# Local Development: Add devtools for seed commands and management utilities
INSTALLED_APPS = INSTALLED_APPS + [
    'apps.devtools',  # Development tools (seed data, management commands)
]
