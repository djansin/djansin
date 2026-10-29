"""Testing URL Configuration.

Environment: testing
Purpose: Automated test execution
Inherits: .base.urlpatterns
Security: Review access controls before deployment

Usage: Add testing-specific patterns below. All access should be logged.
"""

from .base import urlpatterns as base_urlpatterns


urlpatterns = base_urlpatterns + [
    # Testing-specific patterns
    # Apply appropriate authentication/authorization
]
