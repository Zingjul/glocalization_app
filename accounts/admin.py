from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Follow


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
        "follower_count",
        "following_count",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")

    # Organize fields on the user detail page
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("phone_number", "virtual_id")}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("phone_number",)}),
    )

    readonly_fields = ("virtual_id",)

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    # -------- Custom follower/following counts --------
    def follower_count(self, obj):
        """Number of users following this account (clickable)."""
        url = (
            reverse("admin:accounts_follow_changelist")
            + "?"
            + urlencode({"following__id": obj.id})
        )
        count = Follow.objects.filter(following=obj).count()
        return format_html('<a href="{}">{} Followers</a>', url, count)

    follower_count.short_description = "Followers"

    def following_count(self, obj):
        """Number of users this account is following (clickable)."""
        url = (
            reverse("admin:accounts_follow_changelist")
            + "?"
            + urlencode({"follower__id": obj.id})
        )
        count = Follow.objects.filter(follower=obj).count()
        return format_html('<a href="{}">{} Following</a>', url, count)

    following_count.short_description = "Following"


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Admin panel for following relationships.
    Mostly read-only, since follows are created by users.
    """
    list_display = ("id", "follower_link", "following_link", "created_at")
    search_fields = ("follower__username", "following__username")
    list_filter = ("created_at",)
    readonly_fields = ("follower", "following", "created_at")

    def follower_link(self, obj):
        url = reverse("admin:accounts_customuser_change", args=[obj.follower.id])
        return format_html('<a href="{}">{}</a>', url, obj.follower.username)

    follower_link.short_description = "Follower"

    def following_link(self, obj):
        url = reverse("admin:accounts_customuser_change", args=[obj.following.id])
        return format_html('<a href="{}">{}</a>', url, obj.following.username)

    following_link.short_description = "Following"
