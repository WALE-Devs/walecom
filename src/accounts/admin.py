from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """
    Custom admin interface for CustomUser model.
    """

    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "email_verified",
        "date_joined",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "email_verified",
        "phone_verified",
        "newsletter_subscribed",
        "preferred_language",
        "preferred_currency",
        "date_joined",
    )

    search_fields = ("email", "first_name", "last_name", "phone_number")

    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "date_of_birth")}),
        (
            "Contact Information",
            {"fields": ("phone_number", "phone_verified", "email_verified")},
        ),
        (
            "Preferences",
            {
                "fields": (
                    "newsletter_subscribed",
                    "preferred_language",
                    "preferred_currency",
                )
            },
        ),
        (
            "Permissions",
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
        ("Important Dates", {"fields": ("last_login", "date_joined", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )

    readonly_fields = ("date_joined", "updated_at", "last_login")
