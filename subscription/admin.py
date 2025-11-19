from django.contrib import admin
from django.utils.html import format_html
from .models import SubscriptionPlan, UserSubscription


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("level", "price", "duration_days")
    ordering = ("price",)


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "plan",
        "is_active",
        "payment_status_badge",
        "start_date",
        "end_date",
    )
    list_filter = ("is_active", "plan", "payment_reported")
    actions = ["mark_as_active", "mark_as_verified"]

    def payment_status_badge(self, obj):
        """Shows a red or green badge depending on payment status."""
        if obj.payment_reported and not obj.is_active:
            return format_html('<span style="color: white; background-color: red; padding: 3px 8px; border-radius: 5px;">Pending</span>')
        elif obj.is_active:
            return format_html('<span style="color: white; background-color: green; padding: 3px 8px; border-radius: 5px;">Active</span>')
        return format_html('<span style="color: #555; background-color: #eee; padding: 3px 8px; border-radius: 5px;">Idle</span>')

    payment_status_badge.short_description = "Payment Status"

    @admin.action(description="✅ Mark selected subscriptions as active (payment confirmed)")
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True, payment_reported=False)
        self.message_user(request, f"{updated} subscription(s) activated successfully.")

def pending_payment_count(request):
    return {
        "subscription_pending_count": UserSubscription.objects.filter(payment_reported=True, is_active=False).count()
    }

admin.site.each_context = lambda request, context=admin.site.each_context: {
    **context(request),
    **pending_payment_count(request),
}