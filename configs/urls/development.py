"""Development URL Configuration.

Environment: development
Purpose: Full debugging and development tools
Inherits: .base.urlpatterns
Security: Review access controls before deployment

Usage: Add development-specific patterns below. All access should be logged.
"""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .base import urlpatterns as base_urlpatterns


urlpatterns = base_urlpatterns + [
    # OpenAPI & Swagger Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    # Profiling & Debugging Tools
    path("__debug__/", include("debug_toolbar.urls")),
    path("silk/", include("silk.urls", namespace="silk")),
]
