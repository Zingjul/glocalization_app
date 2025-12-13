# accounts/urls.py

from django.urls import path
from .views import (
    PerformLogoutView,
    SignupView,
    signup_success,
    CustomLoginView,
    ConfirmLogoutView,
    LoggedOutView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
    CustomPasswordChangeView,
    UserList,
    UserDetail,
    UserDeleteView,
    SuccessfulLoginView,
    FollowersListView,
    FollowingListView,
    toggle_follow,
    check_follow_status,
    get_follow_counts,
)

# NO app_name here since you don't use namespaces

urlpatterns = [
    # Auth routes
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup-success/', signup_success, name='signup_success'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/confirm/', ConfirmLogoutView.as_view(), name='confirm_logout'),
    path('logout/', PerformLogoutView.as_view(), name='logout'),
    path('logged-out/', LoggedOutView.as_view(), name='logged_out'),
    path('login_true/', SuccessfulLoginView.as_view(), name='login_successful'),

    # Password reset flow
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Password change
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

    # User management
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    path('delete-account/', UserDeleteView.as_view(), name='delete_account'),
    
    # Follow system
    path('follow/<int:user_id>/', toggle_follow, name='toggle_follow'),
    path('follow/status/<int:user_id>/', check_follow_status, name='check_follow_status'),
    path('follow/counts/<int:user_id>/', get_follow_counts, name='get_follow_counts'),
    
    # Followers/Following lists
    path('followers/<int:user_id>/', FollowersListView.as_view(), name='followers_list'),
    path('following/<int:user_id>/', FollowingListView.as_view(), name='following_list'),
]