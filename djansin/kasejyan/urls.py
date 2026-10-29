"""URL Configuration for Kasejyan App.

This module defines URL patterns that map incoming web requests to the
appropriate view functions or classes. It organizes all app-specific
routes in one central location for maintainability.

URL Pattern Components:
    - Route: URL string pattern (can include converters)
    - View: Function or class that handles the request
    - Name: Unique identifier for reverse URL lookups
    - Namespace: 'app_name' variable for URL namespacing

Pattern Types:
    - Static routes: path('about/', views.about)
    - Dynamic routes: path('article/<int:pk>/', views.detail)
    - Nested includes: path('api/', include(api_urls))

Note:
    - Always define app_name for URL namespacing
    - Use path() for simple routes, re_path() for regex when needed
    - Name all URLs for reverse() lookups in templates/views
    - Group related patterns for readability
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from djansin.kasejyan import views


# Namespace for URL reversing
app_name = "kasejyan"

# Handles ViewSet routing automatically
router = DefaultRouter()


# router.register("resource-name", views.YourViewSet, basename="basename")  # Register ViewSets

urlpatterns = router.urls
