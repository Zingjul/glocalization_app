# notifications/hooks/person_notifications.py
from notifications.models import Notification
from accounts.models import Follow  # ✅ Centralized Follow model

def notify_profile_approval(person):
    """
    Notify the user when their profile update is approved.
    Followers are not notified — this is private.
    """
    Notification.objects.create(
        recipient=person.user,
        verb="Your profile update has been approved",
        target_object_id=person.pk,
        target_content_type="person"
    )

def notify_profile_rejection(person):
    """
    Notify the user when their profile update is rejected.
    """
    Notification.objects.create(
        recipient=person.user,
        verb="Your profile update was rejected. Please review and resubmit.",
        target_object_id=person.pk,
        target_content_type="person"
    )

def notify_pending_town(person, typed_town):
    """
    Notify the user when their typed town is pending review.
    """
    Notification.objects.create(
        recipient=person.user,
        verb=f"Thank you kind user, your town '{typed_town}' will be confirmed and approved shortly.",
        target_object_id=person.pk,
        target_content_type="person"
    )

def notify_town_approval(person, typed_town):
    """
    Notify the user when their town request is approved.
    """
    Notification.objects.create(
        recipient=person.user,
        verb=f"Congratulation your town '{typed_town}' has been approved and linked to your profile",
        target_object_id=person.pk,
        target_content_type="person"
    )

def notify_town_rejection(person, typed_town):
    """
    Notify the user when their town request is rejected.
    """
    Notification.objects.create(
        recipient=person.user,
        verb=f"Unfortunately, '{typed_town}' was rejected. This might be due to mispellings or the technical unable to confirm your location, you are welcome to try again.",
        target_object_id=person.pk,
        target_content_type="person"
    )

def notify_business_name_toggle(person):
    """
    Notify the user when they toggle between Real Name and Business Name.
    """
    display = "Business Name" if person.use_business_name else "Real Name"
    Notification.objects.create(
        recipient=person.user,
        verb=f"You are now displaying your {display} on posts.",
        target_object_id=person.pk,
        target_content_type="person"
    )
