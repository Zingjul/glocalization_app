# -------------------------
# file: notifications/urls.py
# -------------------------
from django.urls import path
from .views import NotificationListView, MarkAllReadView, mark_read, NotificationPageView

app_name = "notifications" 

urlpatterns = [
    path("api/", NotificationListView.as_view(), name="notifications-list"),        #json api
    path("", NotificationPageView.as_view(), name="notifications-page"),        #html page
    path("mark-all-read/", MarkAllReadView.as_view(), name="notifications-mark-all-read"),
    # path("prefs/", NotificationPreferenceView.as_view(), name="notifications-prefs"),
    path("<int:pk>/read/", mark_read, name="notifications-mark-read"),
]
