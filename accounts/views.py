from django.contrib.auth.views import (
    LoginView, PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView,
    PasswordChangeView
)
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, logout
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import F
from .models import Follow, CustomUser
from .forms import (
    CustomUserCreationForm,
    CustomLoginForm,
    CustomPasswordResetForm,
    CustomPasswordChangeForm,
    ConfirmPasswordForm,
)
from django.http import JsonResponse
from custom_search.models import Country

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
    virtual_id = request.GET.get('virtual_id', '')
    return render(request, 'accounts/signup_success.html', {
        'virtual_id': virtual_id
    })

# Login View
class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = 'registration/login.html'


# Logout Confirmation Page
class ConfirmLogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'registration/confirm_logout.html'


# Actual Logout Handler (POST only, with message)
class PerformLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('logged_out')  # This should match the template you want to show

    def get(self, request, *args, **kwargs):
        # Optional: prevent logout on GET
        return redirect('confirm_logout')
# Final Logged Out Page
class LoggedOutView(TemplateView):
    template_name = 'registration/logged_out.html'

class SuccessfulLoginView(TemplateView):
    template_name = 'accounts/login_successful_message.html'
    
# 🔐 Password Reset Views with Custom Templates and Form
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


# Password Change View
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change_form.html'
    success_url = reverse_lazy('password_change_done')


# Admin-only User Views
class UserList(ListView):
    model = CustomUser
    template_name = 'accounts/user_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        # Exclude current user if you don’t want them in the list
        return CustomUser.objects.exclude(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preload follows
        following_ids = set(
            Follow.objects.filter(follower=self.request.user).values_list("following_id", flat=True)
        )

        profiles = context["profiles"]
        for profile in profiles:
            profile.follower_count = Follow.objects.filter(following=profile).count()
            profile.is_followed = profile.id in following_ids

        context["profiles"] = profiles
        return context


class UserDetail(DetailView):
    model = CustomUser
    template_name = 'person/person_detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_obj = self.object

        # Make it consistent with PersonDetailView
        is_followed = Follow.objects.filter(
            follower=self.request.user,
            following=user_obj
        ).exists()

        context["profile"] = getattr(user_obj, "profile", None)  # so template works
        context["is_followed"] = is_followed
        return context


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

        
@login_required
def toggle_follow(request, user_id):
    profile = getattr(request.user, "profile", None)
    if not profile or profile.approval_status != "approved":
        messages.error(request, "Your profile must be approved before you can follow or unfollow users.")
        return redirect(request.META.get("HTTP_REFERER", "person_list"))
    target_user = get_object_or_404(CustomUser, id=user_id)

    if target_user == request.user:
        messages.error(request, "You cannot follow yourself.")
        return redirect(request.META.get("HTTP_REFERER", "person_list"))

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=target_user,
    )

    if not created:
        follow.delete()  # unfollow

    return redirect(request.META.get("HTTP_REFERER", "person_list"))


from django.views.generic import ListView
from django.contrib.auth import get_user_model
from .models import Follow

CustomUser = get_user_model()

# this views is defined to specially display a list of the "followers" or "followings" of an account
class FollowersListView(ListView):
    """List all followers of a given user."""
    model = CustomUser
    template_name = "person/followers_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return CustomUser.objects.filter(
            id__in=Follow.objects.filter(following_id=user_id).values_list("follower_id", flat=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "followers"
        context["target_user"] = CustomUser.objects.get(id=self.kwargs["user_id"])
        return context


class FollowingListView(ListView):
    """List all accounts that a given user is following."""
    model = CustomUser
    template_name = "person/following_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        return CustomUser.objects.filter(
            id__in=Follow.objects.filter(follower_id=user_id).values_list("following_id", flat=True)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_type"] = "following"
        context["target_user"] = CustomUser.objects.get(id=self.kwargs["user_id"])
        return context
