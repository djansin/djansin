from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _t

from djansin.kasejyan.models import Email, Phone, User


class EmailInline(admin.StackedInline):
    model = Email
    extra = 0
    max_num = 1
    can_delete = True
    fields = (
        "address",
        "verified_at",
        "verification_code",
        "code_use_attempts",
        "code_expires_at",
    )
    readonly_fields = ("verified_at",)


class PhoneInline(admin.StackedInline):
    model = Phone
    extra = 0
    max_num = 1
    can_delete = True
    fields = (
        "number",
        "verified_at",
        "verification_code",
        "code_use_attempts",
        "code_expires_at",
    )
    readonly_fields = ("verified_at",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email_display",
        "phone_display",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "username",
        "email__address",
        "phone__number",
    )
    ordering = ("-created_at",)
    list_per_page = 25
    readonly_fields = (
        "id",
        "uuid",
        "created_at",
        "updated_at",
        "last_login",
        "password_changed_at",
    )
    inlines = (EmailInline, PhoneInline)

    fieldsets = (
        (
            _t("Credentials"),
            {
                "fields": (
                    "username",
                    "password",
                )
            },
        ),
        (
            _t("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            _t("Important Dates"),
            {
                "fields": (
                    "last_login",
                    "password_changed_at",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    @admin.display(description=_t("Email"), ordering="email__address")
    def email_display(self, obj: User) -> str:
        email = getattr(obj, "email", None)
        return email.address if email else "—"

    @admin.display(description=_t("Phone"), ordering="phone__number")
    def phone_display(self, obj: User) -> str:
        phone = getattr(obj, "phone", None)
        return str(phone.number) if phone else "—"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("email", "phone")
