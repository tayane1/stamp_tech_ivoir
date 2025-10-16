"""
Development settings for stamp project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Development-specific settings
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache configuration for development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Additional development apps
if DEBUG:
    INSTALLED_APPS += [
        "django_extensions",
    ]

# Logging for development
LOGGING["loggers"]["django"]["level"] = "DEBUG"
