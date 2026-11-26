"""Admin configuration for the ``aalnan`` app."""

from django.contrib import admin

from djansin.aalnan.models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "type", "title", "is_read", "created_at")
    list_filter = ("type", "is_read", "created_at")
    search_fields = ("user__username", "title", "body")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 50
    list_select_related = ("user",)


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user", "in_app_enabled", "email_enabled", "sms_enabled")
    search_fields = ("user__username",)
    list_select_related = ("user",)
