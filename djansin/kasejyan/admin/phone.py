from datetime import timedelta

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from djansin.kasejyan.models import Phone


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    """Admin configuration for the :class:`Phone` contact model.

    Displays verification and block state at a glance, and exposes
    read-only access to the one-time-code lifecycle fields (which are
    managed by the service layer, not by operators).
    """

    list_display = (
        "number",
        "user",
        "is_verified",
        "is_blocked_display",
        "blocked_until",
        "created_at",
    )
    list_filter = (
        "verified_at",
        "blocked_until",
        "code_purpose",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "number",
        "user__username",
    )
    readonly_fields = (
        "id",
        "uuid",
        "verified_at",
        "verification_code",
        "code_purpose",
        "code_use_attempts",
        "code_expires_at",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("user",)
    ordering = ("-created_at",)
    list_per_page = 25
    list_select_related = ("user",)

    fieldsets = (
        (
            _t("Phone Information"),
            {
                "fields": (
                    "number",
                    "user",
                )
            },
        ),
        (
            _t("Verification"),
            {
                "fields": (
                    "verified_at",
                    "verification_code",
                    "code_purpose",
                    "code_use_attempts",
                    "code_expires_at",
                ),
                "description": _t(
                    "Verification fields are managed automatically by the system."
                ),
            },
        ),
        (
            _t("Block State"),
            {
                "fields": ("blocked_until",),
                "description": _t(
                    "Set ``blocked_until`` to a future timestamp to "
                    "temporarily block this contact. The block is "
                    "lifted automatically when the timestamp passes."
                ),
            },
        ),
        (
            _t("Metadata"),
            {
                "fields": (
                    "id",
                    "uuid",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ("block_for_15_minutes", "unblock")

    @admin.display(boolean=True, description=_t("Verified"), ordering="verified_at")
    def is_verified(self, obj: Phone) -> bool:
        return obj.verified_at is not None

    @admin.display(boolean=True, description=_t("Blocked"), ordering="blocked_until")
    def is_blocked_display(self, obj: Phone) -> bool:
        """Whether the contact is currently blocked."""
        return obj.blocked_until is not None and obj.blocked_until > timezone.now()

    @admin.action(description=_t("Block selected phones for 15 minutes"))
    def block_for_15_minutes(self, request, queryset):
        """Temporarily block the selected phones for 15 minutes."""
        blocked_until = timezone.now() + timedelta(minutes=15)
        updated = queryset.update(blocked_until=blocked_until)
        self.message_user(
            request,
            _t("%(count)d phone(s) blocked until %(until)s.")
            % {"count": updated, "until": blocked_until},
        )

    @admin.action(description=_t("Unblock selected phones"))
    def unblock(self, request, queryset):
        """Lift any active block on the selected phones."""
        updated = queryset.update(blocked_until=None)
        self.message_user(
            request,
            _t("%(count)d phone(s) unblocked.") % {"count": updated},
        )
