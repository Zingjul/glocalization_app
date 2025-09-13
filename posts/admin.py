from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, PostImage, SocialMediaHandle, PendingLocationRequest
from custom_search.models import Continent, Country, State, Town
from person.models import Person
from django.contrib import admin, messages
from django.db.models import Q
from django.db import transaction

class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 150px; height: auto;" />', obj.image.url)
        return ""
    image_preview.short_description = "Preview"


class SocialMediaHandleInline(admin.StackedInline):
    model = SocialMediaHandle
    can_delete = False
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product_name', 'category', 'get_owner_name', 'author', 'status',
        'created_at', 'get_location_info', 'availability'
    )
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('product_name', 'author__username', 'author__email', 'description')
    inlines = [PostImageInline, SocialMediaHandleInline]
    readonly_fields = [
        'author', 'get_owner_name', 'created_at', 'updated_at',
        'get_location_info', 'preview_social_handles'
    ]
    actions = ['approve_selected_posts']

    fieldsets = (
        (None, {
            'fields': (
                'author', 'get_owner_name', 'category', 'product_name', 'status',
                'description', 'availability',
                # keep FK dropdowns + free-text town input
                'post_continent', 'post_country', 'post_state', 'post_town',
                'post_town_input',
                'created_at', 'updated_at', 'get_location_info',
                'preview_social_handles',
            )
        }),
    )

    def get_owner_name(self, obj):
        person = Person.objects.filter(user=obj.author).first()
        return person.business_name if person and person.business_name else obj.author.username
    get_owner_name.short_description = 'Owner'

    def get_location_info(self, obj):
        loc_parts = [
            obj.post_town.name if obj.post_town else None,
            obj.post_state.name if obj.post_state else None,
            obj.post_country.name if obj.post_country else None,
            obj.post_continent.name if obj.post_continent else None,
        ]
        return ', '.join([part for part in loc_parts if part])
    get_location_info.short_description = "Post Location"

    def preview_social_handles(self, obj):
        try:
            handles = obj.social_handles
        except:
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
                html += f"<li><strong>{platform}:</strong> <a href='{url}' target='_blank'>{url}</a></li>"
        html += "</ul>"

        return format_html(html)
    preview_social_handles.short_description = "Social Media Handles"

    @admin.action(description="Mark selected posts as Approved")
    def approve_selected_posts(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} post(s) marked as approved.")

@admin.register(PendingLocationRequest)
class PendingLocationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_post_title',
        'get_typed_town',
        'get_parent_state',
        'is_reviewed',
        'approved',
        'submitted_at',
    )
    list_filter = ('is_reviewed', 'approved', 'submitted_at')
    actions = ["approve_pending_towns", "reject_pending_towns"]

    def get_post_title(self, obj):
        return f"{obj.post.product_name} (Post #{obj.post.id})"
    get_post_title.short_description = "Post"

    def get_typed_town(self, obj):
        return obj.typed_town or "—"
    get_typed_town.short_description = "Typed Town"

    def get_parent_state(self, obj):
        return obj.parent_state or "—"
    get_parent_state.short_description = "Parent State"

    @admin.action(description="Approve selected pending towns")
    def approve_pending_towns(self, request, queryset):
        approved_count = 0
        skipped_count = 0

        for pending in queryset.filter(is_reviewed=False, approved=False):
            typed_town = pending.typed_town
            parent_state = pending.parent_state

            if not typed_town or not parent_state:
                skipped_count += 1
                continue

            normalized_name = typed_town.strip().title()

            # Case-insensitive check
            town = Town.objects.filter(
                Q(state=parent_state) & Q(name__iexact=normalized_name)
            ).first()

            if not town:
                with transaction.atomic():
                    last_town = Town.objects.order_by("-id").first()
                    next_id = (last_town.id + 1) if last_town else 1
                    prefix = normalized_name[:2].lower()
                    code = f"{prefix}{next_id}"

                    town = Town.objects.create(
                        id=next_id,
                        code=code,
                        name=normalized_name,
                        state=parent_state
                    )

            # Link town to post + approve post
            post = pending.post
            post.post_town = town
            post.status = "approved"
            post.save(update_fields=["post_town", "status"])

            # Mark request reviewed + approved
            pending.approved = True
            pending.is_reviewed = True
            pending.save()

            approved_count += 1

        if approved_count:
            self.message_user(
                request,
                f"✅ {approved_count} pending town(s) approved and linked to posts.",
                level=messages.SUCCESS
            )
        if skipped_count:
            self.message_user(
                request,
                f"⚠️ {skipped_count} request(s) skipped (missing typed_town or parent_state).",
                level=messages.WARNING
            )

    @admin.action(description="Reject selected pending towns")
    def reject_pending_towns(self, request, queryset):
        rejected_count = 0

        for pending in queryset.filter(is_reviewed=False):
            post = pending.post
            post.status = "pending"  # stays pending
            post.save(update_fields=["status"])

            pending.is_reviewed = True
            pending.approved = False
            pending.save()

            rejected_count += 1

        self.message_user(
            request,
            f"🚫 {rejected_count} pending town(s) rejected.",
            level=messages.INFO
        )

# --- Inline for Posts under a Category ---
class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    fields = ("product_name", "author", "status", "created_at")
    readonly_fields = ("product_name", "author", "status", "created_at")
    show_change_link = True  # allows clicking through to the Post edit page


# --- Category Admin ---
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    inlines = [PostInline]

# admin.site.register(Category)
