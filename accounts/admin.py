from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    # Columns shown in user list
    list_display = (
        "username",
        "email",
        "phone_number",
        "virtual_id",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")

    # Organize fields on the user detail page
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "virtual_id")}),
    )

    # Fields shown when creating a new user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone_number",)}),  # exclude virtual_id since it auto-generates
    )

    # Make virtual_id readonly
    readonly_fields = ("virtual_id",)

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)
