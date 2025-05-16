from django.urls import path
from .views import (
    SignupView, signup_success, CustomLoginView,
    ConfirmLogoutView, PerformLogoutView, LoggedOutView,
    CustomPasswordResetView, CustomPasswordChangeView,
    UserList, UserDetail, UserDeleteView
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup-success/', signup_success, name='signup_success'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', ConfirmLogoutView.as_view(), name='logout'),
    path('logout/perform/', PerformLogoutView.as_view(), name='perform_logout'),
    path('logged-out/', LoggedOutView.as_view(), name='logged_out'),

    # Password/Change
    path('password-reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),

    # Users
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    path('delete/', UserDeleteView.as_view(), name='delete_account'),
]
    