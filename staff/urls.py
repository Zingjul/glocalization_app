# staff/urls.py
from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path("login/", views.staff_login_view, name="login"),
    path("logout/", views.staff_logout_view, name="logout"),
    path("", views.dashboard_view, name="dashboard"),

    # 🔹 Pending Posts Moderation
    path("posts/pending/", views.pending_posts_view, name="pending_posts"),
    path("posts/<int:pk>/", views.post_detail_view, name="post_detail"),
    path("posts/<int:pk>/approve/", views.approve_post, name="approve_post"),
    path("posts/<int:pk>/reject/", views.reject_post, name="reject_post"),

    # seekers moderation
    path("seekers/pending/", views.pending_seeker_posts_view, name="pending_seeker_posts"),
    path("seekers/<int:pk>/", views.seeker_post_detail_view, name="seeker_post_detail"),
    path("seekers/<int:pk>/approve/", views.approve_seeker_post, name="approve_seeker_post"),
    path("seekers/<int:pk>/reject/", views.reject_seeker_post, name="reject_seeker_post"),

    # comments moderation
    path("comments/spam/", views.spam_comments_view, name="spam_comments"),
    path("comments/<int:pk>/", views.comment_detail_view, name="comment_detail"),
    path("comments/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("comments/<int:pk>/restore/", views.restore_comment, name="restore_comment"),

    # location moderation
    path("locations/pending/", views.pending_locations_view, name="pending_locations"),
    path("locations/pending/<int:pk>/approve/", views.approve_location, name="approve_location"),
    path("locations/pending/<int:pk>/reject/", views.reject_location, name="reject_location"),

    # user management
    path("users/", views.manage_users, name="manage_users"),
    path("users/<int:pk>/toggle-status/", views.toggle_user_status, name="toggle_user_status"),

    # staff board
    path("board/", views.staff_board, name="staff_board"),

    # audit log
    path("audit-log/", views.audit_log, name="audit_log"),
    
    # subscriptions 
    path("pending-subscriptions/", views.pending_subscriptions_view, name="pending_subscriptions"),
    path("approve-subscription/<int:pk>/", views.approve_subscription, name="approve_subscription"),
    path("reject-subscription/<int:pk>/", views.reject_subscription, name="reject_subscription"),

    # Person Profile approval
    path("pending-profiles/", views.pending_profiles_view, name="pending_profiles"),
    path("approve-profile/<int:pk>/", views.approve_profile, name="approve_profile"),
    path("reject-profile/<int:pk>/", views.reject_profile, name="reject_profile"),

]

