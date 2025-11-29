from django.contrib import admin, messages
from django.utils.html import format_html
from django.db import transaction
from django.db.models import Q
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Post, Category, PendingLocationRequest, SocialMediaHandle
from custom_search.models import Town
from media_app.models import MediaFile

# --- Inline for attached media (Generic relation) ---
class MediaFileInline(GenericTabularInline):
    model = MediaFile
    ct_field = "content_type"
    ct_fk_field = "object_id"
    extra = 0
    readonly_fields = ["file_preview"]

    def file_preview(self, obj):
        if not obj or not getattr(obj, "file", None):
            return ""
        if obj.file_type == "image":
            return format_html(
                '<img src="{}" style="max-width: 150px; height: auto;" />',
                obj.file.url,
            )
        return format_html(
            '<video src="{}" style="max-width: 150px; height: auto;" controls></video>',
            obj.file.url,
        )
    file_preview.short_description = "Preview"

# --- Inline for Social Media Handles ---
class SocialMediaHandleInline(admin.StackedInline):
    model = SocialMediaHandle
    can_delete = False
    extra = 0

# --- Main Post Admin ---
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_name",
        "category",
        "author",
        "status",
        "created_at",
        "expires_at",
        "get_location_info",
        "availability_scope",
    )
    list_filter = ("status", "category", "created_at", "availability_scope")
    search_fields = ("product_name", "author__username", "author__email")
    inlines = [MediaFileInline, SocialMediaHandleInline]
    readonly_fields = [
        "author",
        "created_at",
        "updated_at",
        "get_location_info",
        "preview_social_handles",
        "expires_at",
    ]
    actions = ["approve_selected_posts", "force_expire_posts"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "author",
                    "category",
                    "product_name",
                    "description",
                    "price",
                    "status",
                    "availability_scope",
                    "business_name",
                    "author_phone_number",
                    "author_email",
                    # location fields
                    "post_continent",
                    "post_country",
                    "post_state",
                    "post_town",
                    "post_town_input",
                    "created_at",
                    "updated_at",
                    "expires_at",
                    "get_location_info",
                    "preview_social_handles",
                )
            },
        ),
    )

    def get_location_info(self, obj):
        loc_parts = [
            obj.post_town.name if obj.post_town else None,
            obj.post_state.name if obj.post_state else None,
            obj.post_country.name if obj.post_country else None,
            obj.post_continent.name if obj.post_continent else None,
        ]
        return ", ".join([part for part in loc_parts if part])
    get_location_info.short_description = "Post Location"

    def preview_social_handles(self, obj):
        try:
            handles = obj.social_handles
        except Exception:
            return "-"

        if not handles:
            return "-"

        fields = {
            "LinkedIn": handles.linkedin,
            "Twitter": handles.twitter,
            "YouTube": handles.youtube,
            "Instagram": handles.instagram,
            "Facebook": handles.facebook,
            "WhatsApp": handles.whatsapp,
            "Website": handles.website,
        }

        html = "<ul style='margin:0;padding-left:15px;'>"
        for platform, url in fields.items():
            if url:
                html += (
                    f"<li><strong>{platform}:</strong> "
                    f"<a href='{url}' target='_blank'>{url}</a></li>"
                )
        html += "</ul>"
        return format_html(html)
    preview_social_handles.short_description = "Social Media Handles"

    @admin.action(description="Mark selected posts as Approved")
    def approve_selected_posts(self, request, queryset):
        from notifications.hooks.post_notifications import notify_post_approved

        updated = 0
        for post in queryset.exclude(status="approved"):
            post.status = "approved"
            post.save(update_fields=["status"])
            notify_post_approved(post)
            updated += 1
        self.message_user(request, f"✅ {updated} post(s) marked as approved.")

    @admin.action(description="Force expire selected posts")
    def force_expire_posts(self, request, queryset):
        from django.utils import timezone

        expired = 0
        for post in queryset:
            if post.expires_at > timezone.now():
                post.expires_at = timezone.now()
                post.save(update_fields=["expires_at"])
                expired += 1

        if expired:
            self.message_user(
                request, f"⚠️ {expired} post(s) forced to expire.", level=messages.WARNING
            )

# --- Pending Location Request Admin ---
@admin.register(PendingLocationRequest)
class PendingLocationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_post_title",
        "typed_town",
        "parent_state",
        "is_reviewed",
        "approved",
        "submitted_at",
    )
    list_filter = ("is_reviewed", "approved", "submitted_at")
    actions = ["approve_pending_towns", "reject_pending_towns"]

    def get_post_title(self, obj):
        return f"{obj.post.product_name} (Post #{obj.post.id})"
    get_post_title.short_description = "Post"

    @admin.action(description="Approve selected pending towns")
    def approve_pending_towns(self, request, queryset):
        approved_count, skipped_count = 0, 0

        for pending in queryset.filter(is_reviewed=False, approved=False):
            typed_town = (pending.typed_town or "").strip().title()
            parent_state = pending.parent_state

            if not typed_town or not parent_state:
                skipped_count += 1
                continue

            try:
                with transaction.atomic():
                    town = Town.objects.filter(
                        Q(state=parent_state) & Q(name__iexact=typed_town)
                    ).first()

                    if not town:
                        last_town = Town.objects.order_by("-id").first()
                        next_id = (last_town.id + 1) if last_town else 1
                        prefix = typed_town[:2].lower()
                        code = f"{prefix}{next_id}"

                        town = Town.objects.create(
                            id=next_id,
                            code=code,
                            name=typed_town,
                            state=parent_state,
                        )

                    post = pending.post
                    post.post_town = town
                    post.status = "approved"
                    post.save(update_fields=["post_town", "status"])

                    pending.is_reviewed = True
                    pending.approved = True
                    pending.save()

                    # Optionally notify here if you want

                    approved_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"❌ Error approving request {pending.id}: {e}",
                    level=messages.ERROR,
                )

        if approved_count:
            self.message_user(
                request,
                f"✅ {approved_count} pending town(s) approved and linked to posts.",
                level=messages.SUCCESS,
            )
        if skipped_count:
            self.message_user(
                request,
                f"⚠️ {skipped_count} request(s) skipped (missing typed_town or parent_state).",
                level=messages.WARNING,
            )

    @admin.action(description="Reject selected pending towns")
    def reject_pending_towns(self, request, queryset):
        rejected_count = 0
        for pending in queryset.filter(is_reviewed=False):
            post = pending.post
            post.status = "pending"
            post.save(update_fields=["status"])

            pending.is_reviewed = True
            pending.approved = False
            pending.save()

            rejected_count += 1

        if rejected_count:
            self.message_user(
                request,
                f"🚫 {rejected_count} pending town(s) rejected.",
                level=messages.INFO,
            )

# --- Inline for Posts under a Category ---
class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fields = ("product_name", "author", "status", "created_at")
    readonly_fields = ("product_name", "author", "status", "created_at")
    show_change_link = True

# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [PostInline]