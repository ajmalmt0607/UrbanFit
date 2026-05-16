from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import EmailOTP, TempUser, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "role",
        "is_email_verified",
        "is_staff",
        "is_active",
    )

    list_filter = (
        "role",
        "is_email_verified",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("Role & Verification", {"fields": ("role", "is_email_verified")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )

    readonly_fields = ("created_at", "updated_at", "date_joined", "last_login")

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone_number",
                    "role",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                    "is_active",
                    "is_email_verified",
                ),
            },
        ),
    )


@admin.register(TempUser)
class TempUserAdmin(admin.ModelAdmin):
    list_display = ("email", "first_name", "last_name", "phone_number", "is_verified", "created_at")
    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = ("is_verified",)


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "purpose", "otp", "attempts", "is_verified", "expires_at", "created_at")
    search_fields = ("email",)
    list_filter = ("purpose", "is_verified")