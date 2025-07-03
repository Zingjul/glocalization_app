from django.contrib import admin
from django.utils.html import format_html
from .models import SeekerPost, SeekerCategory, SeekerImage
from person.models import Person

class SeekerImageInline(admin.TabularInline):
    model = SeekerImage
    extra = 0
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 150px; height: auto;" />', obj.image.url)
        return ""
    image_preview.short_description = "Preview"

@admin.register(SeekerPost)
class SeekerPostAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'get_owner_name', 'author', 'request_type',
        'availability_scope', 'status', 'is_fulfilled', 'created_at', 'get_location_info'
    )
    list_filter = ('status', 'is_fulfilled', 'request_type', 'availability_scope', 'category', 'created_at')
    search_fields = ('title', 'author__username', 'author__email', 'description')
    inlines = [SeekerImageInline]
    readonly_fields = ['author', 'get_owner_name', 'created_at', 'get_location_info']
    actions = ['approve_selected_requests', 'mark_as_fulfilled']

    fieldsets = (
        (None, {
            'fields': (
                'author', 'get_owner_name', 'category', 'request_type', 'title',
                'description', 'budget', 'preferred_fulfillment_time',
                'availability_scope', 'status',
                'post_continent', 'post_country', 'post_state', 'post_town',
                'post_continent_input', 'post_country_input',
                'post_state_input', 'post_town_input',
                'is_fulfilled', 'created_at', 'get_location_info',
            )
        }),
    )

    def get_owner_name(self, obj):
        person = Person.objects.filter(user=obj.author).first()
        return person.business_name if person and person.business_name else obj.author.username
    get_owner_name.short_description = 'Requester'

    def get_location_info(self, obj):
        loc_parts = [
            obj.post_town.name if obj.post_town else obj.post_town_input,
            obj.post_state.name if obj.post_state else obj.post_state_input,
            obj.post_country.name if obj.post_country else obj.post_country_input,
            obj.post_continent.name if obj.post_continent else obj.post_continent_input,
        ]
        return ', '.join(part for part in loc_parts if part)
    get_location_info.short_description = "Requested Location"

    @admin.action(description="Mark selected requests as Fulfilled")
    def mark_as_fulfilled(self, request, queryset):
        updated = queryset.update(is_fulfilled=True)
        self.message_user(request, f"{updated} seeker post(s) marked as fulfilled.")

    @admin.action(description="Approve selected requests")
    def approve_selected_requests(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} seeker post(s) marked as approved.")

admin.site.register(SeekerCategory)
