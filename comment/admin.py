from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "author_link",     # ✅ clickable author
        "short_text",
        "target_type",
        "target_title",    # ✅ clickable to public site
        "linked_object",   # ✅ clickable inside admin
        "created_at",
        "is_edited",
        "is_spam",
    )
    list_filter = ("is_edited", "is_spam", "created_at")
    search_fields = ("author__username", "text")
    readonly_fields = (
        "author",
        "text",
        "content_type",
        "object_id",
        "parent",
        "created_at",
        "updated_at",
        "is_edited",
        "is_spam",
    )
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        """❌ Prevent adding new comments from admin."""
        return False

    def has_change_permission(self, request, obj=None):
        """❌ Prevent editing comments in admin."""
        return False

    def short_text(self, obj):
        """Show a preview of the comment text in the list view."""
        return (obj.text[:50] + "...") if len(obj.text) > 50 else obj.text
    short_text.short_description = "Comment"

    def author_link(self, obj):
        """Make the author clickable to their admin profile."""
        if not obj.author:
            return "-"
        app_label = obj.author._meta.app_label
        model_name = obj.author._meta.model_name
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.author.id])
        return format_html('<a href="{}">{}</a>', url, obj.author.username)
    author_link.short_description = "Author"

    def target_type(self, obj):
        """Differentiate between Post and SeekerPost (with category)."""
        model_name = obj.content_type.model
        if model_name == "post":
            return "Post"
        elif model_name == "seekerpost":
            seeker_obj = obj.content_object
            if hasattr(seeker_obj, "category") and seeker_obj.category:
                return f"SeekerPost ({seeker_obj.category.name})"
            return "SeekerPost"
        return model_name.capitalize()
    target_type.short_description = "Target Type"

    def target_title(self, obj):
        """Show the title/name of the related Post/SeekerPost as a clickable link (to website)."""
        target = obj.content_object
        if not target:
            return "-"
        # Determine the display title
        for field in ["product_name", "service_name", "labor_title", "title", "name"]:
            if hasattr(target, field) and getattr(target, field):
                title = getattr(target, field)
                break
        else:
            title = f"Object #{target.id}"

        # Try linking to its public URL if available
        if hasattr(target, "get_absolute_url"):
            return format_html('<a href="{}" target="_blank">{}</a>', target.get_absolute_url(), title)

        return title
    target_title.short_description = "Target Title"

    def linked_object(self, obj):
        """Clickable link to the related object's admin page."""
        target = obj.content_object
        if not target:
            return obj.object_id  # fallback plain text
        app_label = obj.content_type.app_label
        model_name = obj.content_type.model
        url = reverse(f"admin:{app_label}_{model_name}_change", args=[obj.object_id])
        return format_html('<a href="{}">{}</a>', url, obj.object_id)
    linked_object.short_description = "Object ID"
