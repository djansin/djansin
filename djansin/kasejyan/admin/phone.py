from django.contrib import admin
from django.utils.translation import gettext_lazy as _t

from djansin.kasejyan.models import Phone


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "user",
        "is_verified",
        "verified_at",
        "created_at",
    )
    list_filter = (
        "verified_at",
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
                    "code_use_attempts",
                    "code_expires_at",
                ),
                "description": _t(
                    "Verification fields are managed automatically by the system."
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

    @admin.display(boolean=True, description=_t("Verified"), ordering="verified_at")
    def is_verified(self, obj: Phone) -> bool:
        return obj.verified_at is not None

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
