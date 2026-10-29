"""Production Environment Settings.

Environment: production
Inherits: .base
Overrides: Base settings as needed for 'production' operations

Key Responsibilities:
    1. Environment-specific configuration overrides
    2. Security settings appropriate for 'production'
    3. Service endpoints and credentials for 'production'

Configuration Method:
    - Set DJANGO_SETTINGS_MODULE="configs.settings.production"
    - Use environment variables for sensitive data
    - Extend/override only what's necessary from base settings

Note: This file is auto-generated. Manual edits may be overwritten.
"""

from .base import *  # pylint: disable=unused-wildcard-import, wildcard-import  # noqa

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

SECURE_SSL_REDIRECT = True
