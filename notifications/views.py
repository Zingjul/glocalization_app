# notifications/views.py
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


# NOTE: the Follow model lives in accounts app and is referenced via related_name:
# - user.following -> Follow objects where user is follower (has .following -> the followed user)
# - user.followers -> Follow objects where user is being followed (has .follower -> the follower user)


class NotificationListView(generics.ListAPIView):
    """
    List notifications for the authenticated user.

    Query params:
      - filter=relevant   -> returns only notifications that are 'relevant':
                             actor is someone the user follows OR it targets user's content (posts/seekerposts)
      - unread=true       -> only return unread notifications
      - ordering          -> standard DRF ordering if configured (optional)

    The frontend should call this endpoint for the in-app notification feed.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Base queryset: notifications for this user
        qs = Notification.objects.filter(recipient=user)

        # Optional: only unread
        unread_flag = self.request.query_params.get("unread")
        if unread_flag and unread_flag.lower() in ("1", "true", "yes"):
            qs = qs.filter(read=False)

        # Optional: 'relevant' filter (actor is followed by the user OR it targets the user's content)
        if self.request.query_params.get("filter") == "relevant":
            # Get IDs of users the current user follows
            # user.following is a queryset of Follow objects where follower=user.
            # Each Follow has `.following_id` pointing to the followed user id.
            followed_ids = user.following.values_list("following_id", flat=True)

            # Notifications are relevant if:
            # - actor is one of the followed accounts
            # - OR the notification targets the user's content (e.g., a comment on user's post)
            qs = qs.filter(
                Q(actor_id__in=followed_ids) |
                Q(target_content_type__icontains="post", target_object_id__isnull=False) |
                Q(target_content_type__icontains="seekerpost", target_object_id__isnull=False)
            )

        return qs.select_related("actor").order_by("-created_at")


class MarkAllReadView(generics.GenericAPIView):
    """
    Mark all unread notifications for the authenticated user as read.
    POST to this endpoint to mark them all read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        unread_qs = Notification.objects.filter(recipient=user, read=False)
        updated_count = unread_qs.update(read=True)
        return Response({"marked": updated_count}, status=status.HTTP_200_OK)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the current user's NotificationPreference.
    This endpoint will create a NotificationPreference for the user if it doesn't exist.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationPreferenceSerializer

    def get_object(self):
        prefs, _ = NotificationPreference.objects.get_or_create(user=self.request.user)
        return prefs


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def mark_read(request, pk):
    """
    Mark a single notification as read (POST).
    URL: /notifications/<pk>/read/
    """
    notif = get_object_or_404(Notification, id=pk, recipient=request.user)

    if notif.read:
        return Response({"status": "already_read"}, status=status.HTTP_200_OK)

    notif.read = True
    notif.save(update_fields=["read"])
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


# we are adding this to work with the notification listview, thats because the list view at the top returns json and therefore we need another that will get those json information and put out to us in a html or javascript format so that its readerable and useable in the frontend to users
class NotificationPageView(LoginRequiredMixin, TemplateView):
    template_name = "notifications/notification_page.html"
