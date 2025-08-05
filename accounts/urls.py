# accounts/urls.py

from django.urls import path
from .views import PerformLogoutView, SignupView, signup_success, CustomLoginView, ConfirmLogoutView, LoggedOutView, CustomPasswordResetView, CustomPasswordResetDoneView, CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, CustomPasswordChangeView, UserList, UserDetail, UserDeleteView, SuccessfulLoginView

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
]
