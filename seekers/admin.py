# seekers/admin.py
from django.contrib import admin, messages
from django.utils.html import format_html
from django.db.models import Q
from django.db import transaction
from django.contrib.contenttypes.admin import GenericTabularInline
from django.utils import timezone

from .models import (
    SeekerPost, SeekerCategory,
    PendingSeekerLocationRequest, SeekerResponse, SeekerSocialMediaHandle
)
from custom_search.models import Town
from person.models import Person
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
class SeekerSocialMediaHandleInline(admin.StackedInline):
    model = SeekerSocialMediaHandle
    can_delete = False
    extra = 0


# --- Main Seeker Post Admin ---
@admin.register(SeekerPost)
class SeekerPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "get_owner_name",
        "author",
        "status",
        "created_at",
        "expires_at",
        "get_location_info",
        "availability_scope",
    )
    list_filter = ("status", "category", "created_at", "availability_scope")
    search_fields = ("title", "author__username", "author__email")
    inlines = [MediaFileInline, SeekerSocialMediaHandleInline]
    readonly_fields = [
        "author",
        "get_owner_name",
        "created_at",
        "updated_at",
        "expires_at",
        "get_location_info",
        "preview_social_handles",
    ]
    actions = ["approve_selected_seekers", "expire_selected_seekers"]

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "author",
                    "get_owner_name",
                    "category",
                    "title",
                    "status",
                    "description",
                    "availability_scope",
                    "budget",
                    "preferred_fulfillment_time",
                    "is_fulfilled",
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
                    "get_location_info",
                    "preview_social_handles",
                )
            },
        ),
    )

    def get_owner_name(self, obj):
        person = Person.objects.filter(user=obj.author).first()
        return (
            person.business_name
            if person and person.business_name
            else obj.author.username
        )
    get_owner_name.short_description = "Owner"

    def get_location_info(self, obj):
        loc_parts = [
            obj.post_town.name if obj.post_town else None,
            obj.post_state.name if obj.post_state else None,
            obj.post_country.name if obj.post_country else None,
            obj.post_continent.name if obj.post_continent else None,
        ]
        return ", ".join([part for part in loc_parts if part])
    get_location_info.short_description = "Seeker Location"

    def preview_social_handles(self, obj):
        try:
            handles = obj.seeker_social_handles
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

    @admin.action(description="Mark selected seeker posts as Approved")
    def approve_selected_seekers(self, request, queryset):
        updated = queryset.update(status="approved")
        self.message_user(request, f"✅ {updated} seeker post(s) marked as approved.")

    @admin.action(description="Force expire selected seeker posts now")
    def expire_selected_seekers(self, request, queryset):
        updated = 0
        now = timezone.now()
        for seeker_post in queryset:
            seeker_post.expires_at = now
            seeker_post.save(update_fields=["expires_at"])
            updated += 1

        if updated:
            self.message_user(
                request,
                f"⚠️ Expired {updated} seeker post(s) manually.",
                level=messages.WARNING,
            )


# --- Pending Seeker Location Admin ---
@admin.register(PendingSeekerLocationRequest)
class PendingSeekerLocationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_post_title",
        "get_typed_town",
        "get_parent_state",
        "is_reviewed",
        "approved",
        "submitted_at",
    )
    list_filter = ("is_reviewed", "approved", "submitted_at")
    actions = ["approve_pending_towns", "reject_pending_towns"]

    def get_post_title(self, obj):
        return f"{obj.post.title} (Seeker #{obj.post.id})"
    get_post_title.short_description = "Seeker Post"

    def get_typed_town(self, obj):
        return obj.typed_town or "—"
    get_typed_town.short_description = "Typed Town"

    def get_parent_state(self, obj):
        return obj.parent_state or "—"
    get_parent_state.short_description = "Parent State"

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

                    seeker_post = pending.post
                    seeker_post.post_town = town
                    seeker_post.status = "approved"
                    seeker_post.save(update_fields=["post_town", "status"])

                    pending.is_reviewed = True
                    pending.approved = True
                    pending.save()

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
                f"✅ {approved_count} pending town(s) approved and linked to seekers.",
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
            seeker_post = pending.post
            seeker_post.status = "pending"
            seeker_post.save(update_fields=["status"])

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
class SeekerPostInline(admin.TabularInline):
    model = SeekerPost
    extra = 0
    fields = ("title", "author", "status", "created_at")
    readonly_fields = ("title", "author", "status", "created_at")
    show_change_link = True


# --- Category Admin ---
@admin.register(SeekerCategory)
class SeekerCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [SeekerPostInline]


# --- Response Admin ---
@admin.register(SeekerResponse)
class SeekerResponseAdmin(admin.ModelAdmin):
    list_display = ("id", "seeker_post_title", "sender_username", "receiver_username", "created_at")
    search_fields = (
        "seeker_post__title",
        "sender__username", "sender__email",
        "receiver__username", "receiver__email",
    )
    list_filter = ("created_at",)

    def seeker_post_title(self, obj):
        return obj.seeker_post.title
    seeker_post_title.admin_order_field = "seeker_post"
    seeker_post_title.short_description = "Seeker Post"

    def sender_username(self, obj):
        return obj.sender.username
    sender_username.admin_order_field = "sender"
    sender_username.short_description = "Sender"

    def receiver_username(self, obj):
        return obj.receiver.username
    receiver_username.admin_order_field = "receiver"
    receiver_username.short_description = "Receiver"
