# media_app/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse

from .models import MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file_preview",
        "file_type",
        "get_owner_display",   # 👈 owner or business
        "caption",
        "is_public",
        "uploaded_at",
        "linked_object",       # 👈 clickable related Post/SeekerPost
    )
    list_filter = ("file_type", "is_public", "uploaded_at", "owner")
    search_fields = (
        "caption",
        "file",
        "owner__username",
        "owner__email",
    )
    readonly_fields = ("uploaded_at", "file_preview")
    actions = ["make_public", "make_private"]

    def get_owner_display(self, obj):
        """
        Show business_name if the attached object has it,
        otherwise show the owner's username.
        """
        related_obj = obj.content_object
        if hasattr(related_obj, "business_name") and related_obj.business_name:
            return related_obj.business_name
        return getattr(obj.owner, "username", "anonymous")
    get_owner_display.short_description = "Owner / Business"

    def linked_object(self, obj):
        """Clickable link to the related Post/SeekerPost/etc."""
        if not obj.content_type or not obj.object_id:
            return "—"

        try:
            related_obj = obj.content_object
            url = reverse(
                f"admin:{obj.content_type.app_label}_{obj.content_type.model}_change",
                args=[obj.object_id],
            )
            # Show something readable for the link text
            display_text = str(related_obj)
            return format_html('<a href="{}">{}</a>', url, display_text)
        except Exception:
            return "—"
    linked_object.short_description = "Attached To"

    def file_preview(self, obj):
        """Render thumbnail/preview of uploaded file."""
        if not obj or not obj.file:
            return "—"

        if obj.file_type == "image":
            return format_html(
                '<img src="{}" style="max-width:120px; height:auto;" />',
                obj.file.url,
            )
        elif obj.file_type == "video":
            return format_html(
                '<video src="{}" style="max-width:150px; height:auto;" controls></video>',
                obj.file.url,
            )
        return format_html("<em>{}</em>", obj.file_type)
    file_preview.short_description = "Preview"

    @admin.action(description="Mark selected media as Public")
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(
            request,
            f"✅ {updated} media file(s) marked as Public.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Mark selected media as Private")
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(
            request,
            f"🔒 {updated} media file(s) marked as Private.",
            level=messages.WARNING,
        )
