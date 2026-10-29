"""Development Environment Settings.

Environment: development
Inherits: .base
Overrides: Base settings as needed for 'development' operations

Key Responsibilities:
    1. Environment-specific configuration overrides
    2. Security settings appropriate for 'development'
    3. Service endpoints and credentials for 'development'

Configuration Method:
    - Set DJANGO_SETTINGS_MODULE="configs.settings.development"
    - Use environment variables for sensitive data
    - Extend/override only what's necessary from base settings

Note: This file is auto-generated. Manual edits may be overwritten.
"""

import socket

from .base import *  # pylint: disable=unused-wildcard-import, wildcard-import  # noqa


DEVELOP_APPS = [
    "django_extensions",
    "drf_spectacular",
    "debug_toolbar",
    "silk",
]

INSTALLED_APPS = INSTALLED_APPS + DEVELOP_APPS

# -----------------------------------------------------------------------------
# Middleware Configuration
# Silk middleware should be as early as possible.
# Debug Toolbar middleware must come before response modifying middlewares.
# -----------------------------------------------------------------------------
MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
] + MIDDLEWARE

# -----------------------------------------------------------------------------
# Django Debug Toolbar Settings
# -----------------------------------------------------------------------------
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Support Docker container environments for Debug Toolbar
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
except socket.gaierror:
    pass

# -----------------------------------------------------------------------------
# Django Silk Settings
# -----------------------------------------------------------------------------
SILKY_PYTHON_PROFILER = True
SILKY_ANALYZE_QUERIES = True

ENVIRONMENT = env.str("ENVIRONMENT", "production")

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:9000",
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:9000",
]

URL_CONFIG = {
    "development": "configs.urls.development",
    "testing": "configs.urls.testing",
}

ROOT_URLCONF = URL_CONFIG.get(ENVIRONMENT, "configs.urls.development")

REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
