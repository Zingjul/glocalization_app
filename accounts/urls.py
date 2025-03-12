from django.urls import path
from .views import SignupView, signup_success, LogoutView, CustomPasswordResetView, CustomPasswordChangeView, UserList, UserDetail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/success/', signup_success, name='signup_success'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('password_change/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    # API Views
    path('users/', UserList.as_view(), name='user-list'), # Added name
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'), # Added name
]