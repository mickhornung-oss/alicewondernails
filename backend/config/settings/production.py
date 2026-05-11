from .base import *  # noqa
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
env = environ.Env()
env.read_env(ROOT_DIR / '.env')

DEBUG = False

# === Production Security Hardening ===

# 1. SECRET_KEY: Must be long, random, and NOT auto-generated
PROD_SECRET_KEY = env('DJANGO_SECRET_KEY', default=None)
if not PROD_SECRET_KEY:
    raise ValueError(
        "DJANGO_SECRET_KEY environment variable MUST be set in production. "
        "Generate a strong key using: "
        "python -c 'from django.core.management.utils import get_random_secret_key; "
        "print(get_random_secret_key())'"
    )
if PROD_SECRET_KEY.startswith('django-insecure-') or len(PROD_SECRET_KEY) < 50:
    raise ValueError(
        "DJANGO_SECRET_KEY in production must be 50+ characters and NOT prefixed with "
        "'django-insecure-'. Generate a new key with: "
        "python -c 'from django.core.management.utils import get_random_secret_key; "
        "print(get_random_secret_key())'"
    )
SECRET_KEY = PROD_SECRET_KEY

# 2. ALLOWED_HOSTS: Must be explicitly set, no wildcards
allowed_hosts_str = env('DJANGO_ALLOWED_HOSTS', default=None)
if not allowed_hosts_str:
    raise ValueError(
        "DJANGO_ALLOWED_HOSTS environment variable MUST be set in production. "
        "Format: 'example.com,www.example.com' (comma-separated, no spaces)"
    )
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_str.split(',') if h.strip()]
if not ALLOWED_HOSTS:
    raise ValueError(
        "DJANGO_ALLOWED_HOSTS must contain at least one valid hostname."
    )

# 3. SSL/HTTPS: Mandatory in production
SECURE_SSL_REDIRECT = True

# 4. Session & CSRF Cookies: Secure only (HTTPS)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 5. CSRF Trusted Origins (for frontend on different domain)
csrf_origins_str = env('DJANGO_CSRF_TRUSTED_ORIGINS', default='')
if csrf_origins_str:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins_str.split(',') if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []

# 6. HSTS (HTTP Strict Transport Security)
# Conservative defaults: only increase after full HTTPS/domain/subdomain testing
SECURE_HSTS_SECONDS = int(env('DJANGO_SECURE_HSTS_SECONDS', default='3600'))  # 1 hour default
SECURE_HSTS_INCLUDE_SUBDOMAINS = env('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env('DJANGO_SECURE_HSTS_PRELOAD', default=False)
