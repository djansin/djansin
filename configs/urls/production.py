"""Production URL Configuration.

Environment: production
Purpose: Public endpoints with security hardening
Inherits: .base.urlpatterns
Security: Review access controls before deployment

Usage: Add production-specific patterns below. All access should be logged.
"""

from .base import urlpatterns as base_urlpatterns


urlpatterns = base_urlpatterns + [
    # Production-specific patterns
    # Apply appropriate authentication/authorization
]
