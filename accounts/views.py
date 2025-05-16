from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordChangeView
)
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, logout
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from .forms import (
    CustomUserCreationForm,
    CustomLoginForm,
    CustomPasswordResetForm,
    CustomPasswordChangeForm,
    ConfirmPasswordForm,
)

CustomUser = get_user_model()


# Signup View (User Registration)
class SignupView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_success')

    def form_valid(self, form):
        user = form.save()
        print("✔️ User created:", user.email, "| Virtual ID:", user.virtual_id)
        self.virtual_id = user.virtual_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('signup_success') + f'?virtual_id={self.virtual_id}'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().get(request, *args, **kwargs)


def signup_success(request):
    return render(request, 'accounts/signup_success.html')


# Login View
class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'


# Logout Confirmation Page
class ConfirmLogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/confirm_logout.html'


# Actual Logout Handler (POST only, with message)
class PerformLogoutView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('logged_out')


# Final Logged Out Page
class LoggedOutView(TemplateView):
    template_name = 'registration/logged_out.html'


# Password Reset View
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'


# Password Change View
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('password_change_done')


# Admin-only User Views
class UserList(ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'


class UserDetail(DetailView):
    model = CustomUser
    template_name = 'accounts/user_detail.html'
    context_object_name = 'user_obj'


# Delete User Account with Password Confirmation
class UserDeleteView(LoginRequiredMixin, FormView):
    template_name = 'accounts/user_confirm_delete.html'
    form_class = ConfirmPasswordForm
    success_url = reverse_lazy('login')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        logout(self.request)
        user.delete()
        return super().form_valid(form)
