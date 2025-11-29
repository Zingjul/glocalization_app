from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.http import urlencode

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Follow

from person.utils.phone_codes import PHONE_CODES

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "username",
        "email",
        "country_prefix_display",
        "phone_number",
        "virtual_id",
        "follower_count_display",
        "following_count_display",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active")

    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("country_code", "phone_number", "virtual_id")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("country_code", "phone_number")}),
    )

    readonly_fields = ("virtual_id",)

    search_fields = ("username", "email", "phone_number")
    ordering = ("username",)

    def country_prefix_display(self, obj):
        """
        Display the ISO2 + phone prefix using PHONE_CODES dict.
        Example: "NG +234" or just "NG" if prefix is missing.
        """
        iso = str(obj.country_code).upper() if obj.country_code else ""
        prefix = PHONE_CODES.get(iso)
        if iso and prefix:
            return f"{iso} {prefix}"
        if iso:
            return iso
        return "-"

    country_prefix_display.short_description = "Country Prefix"

    def follower_count_display(self, obj):
        """
        Clickable link to followers list in admin.
        """
        url = (
            reverse("admin:accounts_follow_changelist")
            + "?"
            + urlencode({"following__id": obj.id})
        )
        count = Follow.objects.filter(following=obj).count()
        return format_html('<a href="{}">{} Followers</a>', url, count)

    follower_count_display.short_description = "Followers"

    def following_count_display(self, obj):
        """
        Clickable link to following list in admin.
        """
        url = (
            reverse("admin:accounts_follow_changelist")
            + "?"
            + urlencode({"follower__id": obj.id})
        )
        count = Follow.objects.filter(follower=obj).count()
        return format_html('<a href="{}">{} Following</a>', url, count)

    following_count_display.short_description = "Following"

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
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