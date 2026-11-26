"""URL configuration for the ``aalnan`` app."""

from django.urls import path

from djansin.aalnan.views import (
    NotificationDeleteView,
    NotificationListView,
    NotificationPreferenceView,
    NotificationReadAllView,
    NotificationReadView,
)


app_name = "aalnan"

urlpatterns = [
    path("", NotificationListView.as_view(), name="list"),
    path("<int:pk>/read/", NotificationReadView.as_view(), name="read"),
    path("read-all/", NotificationReadAllView.as_view(), name="read-all"),
    path("<int:pk>/", NotificationDeleteView.as_view(), name="delete"),
    path("preferences/", NotificationPreferenceView.as_view(), name="preferences"),
]
