from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth import login, logout
from django.views.generic import ListView, DetailView, FormView, View
from .forms import CustomUserCreationForm, CustomPasswordResetForm, CustomPasswordChangeForm
from .models import CustomUser

# Signup View (User Registration)
class SignupView(FormView):
    template_name = 'registration/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup_success')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.virtual_id = user.virtual_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('signup_success') + f'?virtual_id={self.virtual_id}'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # Redirect authenticated users to dashboard or another page
        return super().get(request, *args, **kwargs)


# Signup Success Page
def signup_success(request):
    virtual_id = request.GET.get('virtual_id')
    return render(request, 'signup_success.html', {'virtual_id': virtual_id})


# Logout View
class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


# Password Reset View
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'

    def form_valid(self, form):
        try:
            user = CustomUser.objects.get(email=form.cleaned_data["email"])
            if user:
                print(f"Password reset request for {user.email}")
            return super().form_valid(form)
        except CustomUser.DoesNotExist:
            print("No user found with that email.")
            return super().form_invalid(form)


# Password Change View
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('password_change_done')


# **Restoring UserList & UserDetail Views**
class UserList(ListView):
    model = CustomUser
    template_name = "accounts/user_list.html"  # Create this template
    context_object_name = "users"  # Ensures easier template access

class UserDetail(DetailView):
    model = CustomUser
    template_name = "accounts/user_detail.html"  # Create this template
    context_object_name = "user"

    def get_object(self):
        return get_object_or_404(CustomUser, pk=self.kwargs.get("pk"))
