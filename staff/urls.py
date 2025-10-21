from django.urls import path
from . import views

app_name = "staff"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pending-posts/', views.pending_posts, name='pending_posts'),
    path('flagged-comments/', views.flagged_comments, name='flagged_comments'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('support/', views.support_inbox, name='support_inbox'),
]
