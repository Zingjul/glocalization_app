from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, PostImage, SocialMediaHandle
from custom_search.models import PendingLocationRequest, Country, State
from person.models import Person


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
    search_fields = ('product_name', 'author__username', 'author__email')
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
                'post_continent', 'post_country', 'post_state', 'post_town',
                'post_continent_input', 'post_country_input',
                'post_state_input', 'post_town_input',
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
            obj.post_town.name if obj.post_town else obj.post_town_input,
            obj.post_state.name if obj.post_state else obj.post_state_input,
            obj.post_country.name if obj.post_country else obj.post_country_input,
            obj.post_continent.name if obj.post_continent else obj.post_continent_input,
        ]
        return ', '.join(part for part in loc_parts if part)
    get_location_info.short_description = "Post Location"

    def preview_social_handles(self, obj):
        handles = SocialMediaHandle.objects.filter(post=obj)
        if not handles.exists():
            return "-"
        html = "<ul>"
        for handle in handles:
            html += f"<li><strong>{handle.platform}:</strong> {handle.handle}</li>"
        html += "</ul>"
        return format_html(html)
    preview_social_handles.short_description = "Social Media Handles"

    @admin.action(description="Mark selected posts as Approved")
    def approve_selected_posts(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} post(s) marked as approved.")


@admin.register(PendingLocationRequest)
class PendingLocationRequestAdmin(admin.ModelAdmin):
    list_display = [
        "user", "typed_continent", "typed_country", "typed_state", "typed_town",
        "is_reviewed", "approved", "submitted_at"
    ]
    list_filter = ["is_reviewed", "approved"]
    search_fields = ["user__username", "typed_state", "typed_country", "typed_town"]
    actions = ["approve_location"]

    @admin.action(description="Approve and create official location entries")
    def approve_location(self, request, queryset):
        for pending in queryset:
            if pending.typed_state and pending.typed_country:
                country_obj = Country.objects.filter(name__iexact=pending.typed_country).first()
                if not country_obj:
                    self.message_user(request, f"❌ Country '{pending.typed_country}' not found for {pending.user}", level="error")
                    continue

                # Generate state code
                country_code = country_obj.code.upper()
                raw = pending.typed_state.strip().replace(" ", "").replace("-", "")
                state_code = f"{country_code}-{raw.upper()[:6]}"

                # Avoid duplicates
                if State.objects.filter(name__iexact=pending.typed_state, country=country_obj).exists():
                    self.message_user(request, f"⚠️ State '{pending.typed_state}' already exists under '{pending.typed_country}'", level="warning")
                else:
                    State.objects.create(name=pending.typed_state, country=country_obj, code=state_code)
                    self.message_user(request, f"✅ Created state '{pending.typed_state}' with code '{state_code}'")

                pending.is_reviewed = True
                pending.approved = True
                pending.save()

        self.message_user(request, f"🎯 Reviewed and processed {queryset.count()} pending location request(s).")


admin.site.register(Category)
