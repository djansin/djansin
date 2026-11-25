from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from djansin.kasejyan.models import Email


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    """Admin configuration for the :class:`Email` contact model.

    Displays verification and block state at a glance, and exposes
    read-only access to the one-time-code lifecycle fields (which are
    managed by the service layer, not by operators).
    """

    list_display = (
        "address",
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
        "address",
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
            _t("Email Information"),
            {
                "fields": (
                    "address",
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
    def is_verified(self, obj: Email) -> bool:
        return obj.verified_at is not None

    @admin.display(boolean=True, description=_t("Blocked"), ordering="blocked_until")
    def is_blocked_display(self, obj: Email) -> bool:
        """Whether the contact is currently blocked."""
        return obj.blocked_until is not None and obj.blocked_until > timezone.now()

    @admin.action(description=_t("Block selected emails for 15 minutes"))
    def block_for_15_minutes(self, request, queryset):
        """Temporarily block the selected emails for 15 minutes."""
        blocked_until = timezone.now() + timezone.timedelta(minutes=15)
        updated = queryset.update(blocked_until=blocked_until)
        self.message_user(
            request,
            _t("%(count)d email(s) blocked until %(until)s.")
            % {"count": updated, "until": blocked_until},
        )

    @admin.action(description=_t("Unblock selected emails"))
    def unblock(self, request, queryset):
        """Lift any active block on the selected emails."""
        updated = queryset.update(blocked_until=None)
        self.message_user(
            request,
            _t("%(count)d email(s) unblocked.") % {"count": updated},
        )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
