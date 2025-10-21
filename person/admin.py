from django.contrib import admin, messages
from django.db import transaction, IntegrityError
from django.conf import settings
from django.core.mail import send_mail

from .models import Person, Availability, PendingLocationRequest
from custom_search.models import Continent, Country, State, Town
from . import emails

# ✅ notification hooks imported here instead of accounts/admin.py
from notifications.hooks.person_notifications import (
    notify_profile_approval,
    notify_profile_rejection,
    notify_business_name_toggle,
)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "user", "business_name", "use_business_name",
        "continent", "country", "state", "town",
        "continent_input", "country_input", "state_input", "town_input",
        "approval_status", "updated_at",
    )
    list_filter = ("continent", "country", "state", "town", "approval_status")
    search_fields = (
        "user__username", "business_name",
        "continent_input", "country_input", "state_input", "town_input"
    )

    actions = [
        "approve_location_inputs",
        "reject_profile_update",
        "approve_profiles",
        "reject_profiles",
        "toggle_business_name",
    ]

    # -------------------------
    # Existing approval/rejection
    # -------------------------
    @admin.action(description="Approve profile update (verify or create locations)")
    def approve_location_inputs(self, request, queryset):
        approved = 0
        for person in queryset:
            person.approval_status = "approved"
            person.save()

            send_mail(
                subject=emails.APPROVAL_SUBJECT,
                message=emails.APPROVAL_MESSAGE.format(username=person.user.username),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[person.user.email],
                fail_silently=True,
            )
            approved += 1

        self.message_user(
            request,
            f"Approved {approved} profile(s) and verified their location.",
            level=messages.SUCCESS,
        )

    @admin.action(description="Reject profile update (send back to user)")
    def reject_profile_update(self, request, queryset):
        rejected = 0
        for person in queryset:
            person.approval_status = "awaiting_user"
            person.save()

            send_mail(
                subject=emails.REJECTION_SUBJECT,
                message=emails.REJECTION_MESSAGE.format(username=person.user.username),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[person.user.email],
                fail_silently=True,
            )
            rejected += 1

        self.message_user(
            request,
            f"Rejected {rejected} profile update(s). Sent back to users for correction.",
            level=messages.INFO,
        )

    # -------------------------
    # Functions merged from accounts/admin.py
    # -------------------------
    @admin.action(description="Approve selected profiles (set is_verified=True)")
    def approve_profiles(self, request, queryset):
        for person in queryset:
            if not getattr(person, "is_verified", False):
                person.is_verified = True
                person.approval_status = "approved"
                person.save()
                notify_profile_approval(person)
        self.message_user(request, f"{queryset.count()} profile(s) approved")

    @admin.action(description="Reject selected profiles (set is_verified=False)")
    def reject_profiles(self, request, queryset):
        for person in queryset:
            if getattr(person, "is_verified", False):
                person.is_verified = False
                person.approval_status = "rejected"
                person.save()
                notify_profile_rejection(person)
        self.message_user(request, f"{queryset.count()} profile(s) rejected")

    @admin.action(description="Toggle Business/Real Name")
    def toggle_business_name(self, request, queryset):
        for person in queryset:
            person.use_business_name = not person.use_business_name
            person.save()
            notify_business_name_toggle(person)
        self.message_user(
            request,
            f"Toggled business/real name for {queryset.count()} profile(s)"
        )


@admin.register(PendingLocationRequest)
class PendingLocationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id", "person", "typed_town", "parent_state",
        "is_reviewed", "approved", "submitted_at",
    )
    list_filter = ("is_reviewed", "approved", "submitted_at")
    actions = ["approve_pending_towns", "reject_pending_towns"]

    @admin.action(description="Approve selected pending towns")
    def approve_pending_towns(self, request, queryset):
        approved_count, skipped_count = 0, 0

        for pending in queryset.filter(is_reviewed=False, approved=False):
            typed_town = pending.typed_town
            parent_state = pending.parent_state

            if not typed_town or not parent_state:
                skipped_count += 1
                continue

            normalized_name = typed_town.strip().title()

            town = Town.objects.filter(
                state=parent_state, name__iexact=normalized_name
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

            person = pending.person
            person.town = town
            person.approval_status = "approved"
            person.save(update_fields=["town", "approval_status"])

            pending.is_reviewed = True
            pending.approved = True
            pending.save()

            send_mail(
                subject=emails.APPROVAL_SUBJECT,
                message=emails.APPROVAL_MESSAGE.format(username=person.user.username),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[person.user.email],
                fail_silently=True,
            )

            approved_count += 1

        if approved_count:
            self.message_user(
                request, f"Approved {approved_count} pending town(s) and linked to Person(s).",
                level=messages.SUCCESS
            )
        if skipped_count:
            self.message_user(
                request, f"Skipped {skipped_count} request(s) (missing typed_town or parent_state).",
                level=messages.WARNING
            )

    @admin.action(description="Reject selected pending towns")
    def reject_pending_towns(self, request, queryset):
        rejected = 0
        for pending in queryset.filter(is_reviewed=False):
            person = pending.person
            pending.is_reviewed = True
            pending.approved = False
            pending.save()

            person.approval_status = "awaiting_user"
            person.save(update_fields=["approval_status"])

            send_mail(
                subject=emails.REJECTION_SUBJECT,
                message=emails.REJECTION_MESSAGE.format(username=person.user.username),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[person.user.email],
                fail_silently=True,
            )

            rejected += 1

        self.message_user(
            request, f"Rejected {rejected} pending town(s).",
            level=messages.INFO
        )
