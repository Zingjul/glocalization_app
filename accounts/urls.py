from django.urls import path
from .views import SignupView, signup_success, LogoutView, LogoutSuccessful

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('signup/success/', signup_success, name='signup_success'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('logout_successful/', LogoutSuccessful.as_view(), name='logged_out'),
]