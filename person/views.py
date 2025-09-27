import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect, JsonResponse
from accounts.models import Follow
from .forms import PersonForm
from .models import Person, PendingLocationRequest
from accounts.models import CustomUser
from custom_search.models import Continent, Country, State, Town   # ✅ only from here

logger = logging.getLogger(__name__)

class PersonSetupView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Create or update the logged-in user's Person profile."""

    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def get_object(self, queryset=None):
        """Always return the logged-in user's profile."""
        return self.request.user.profile

    def get_success_url(self):
        """Redirect to profile detail after setup/update."""
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        """Only allow the owner to edit, and not while pending."""
        person = self.get_object()
        return person.user == self.request.user and person.approval_status != "pending"

    def handle_no_permission(self):
        messages.warning(
            self.request,
            "Your profile is under review and cannot be edited until approved."
        )
        return redirect("person_detail", pk=self.get_object().pk)

    def form_valid(self, form):
        """Handle town logic and pending approvals."""
        from custom_search.models import Town

        person = form.save(commit=False)
        person.user = self.request.user

        selected_town_id = self.request.POST.get("town")
        typed_town_name = self.request.POST.get("town_input", "").strip()

        # Ensure fallback "Unspecified" town exists
        unspecified_town = Town.objects.filter(id=0).first()
        if not unspecified_town:
            form.add_error("town", "System error: Unspecified town not found.")
            return self.form_invalid(form)

        if selected_town_id and selected_town_id != "0":
            try:
                person.town = Town.objects.get(id=selected_town_id)
            except Town.DoesNotExist:
                form.add_error("town", "Selected town does not exist.")
                return self.form_invalid(form)

        elif typed_town_name:
            # Fallback assignment for typed towns
            person.town = unspecified_town
            person.approval_status = "pending"
            person.save()

            PendingLocationRequest.objects.update_or_create(
                person=person,
                defaults={
                    "typed_town": typed_town_name,
                    "parent_state": form.cleaned_data.get("state"),
                    "is_reviewed": False,
                    "approved": False,
                },
            )

            messages.success(
                self.request,
                "Profile updated successfully! 🎉 Your town is pending admin approval."
            )
            return super().form_valid(form)
        person.approval_status = "pending"
        person.save()
        messages.success(self.request, "Profile updated successfully! 🎉")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add location dropdowns and profile status to context."""
        context = super().get_context_data(**kwargs)
        context.update({
            "continents": Continent.objects.all(),
            "countries": Country.objects.all(),
            "states": State.objects.all(),
            "towns": Town.objects.all(),
            "location_fields": ["continent", "country", "state", "town"],
            "location_input_fields": ["continent_input", "country_input", "state_input", "town_input"],
            "has_pending_location": hasattr(self.object, "pending_location_request"),
            "approval_status": self.object.approval_status,
        })
        return context

class PersonListView(LoginRequiredMixin, ListView):
    """List all registered and approved Person profiles."""

    model = Person
    template_name = "person/person_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        # Only return profiles with approval_status = "approved"
        qs = Person.objects.filter(
            approval_status="approved"
        ).exclude(user=self.request.user)  # 🚫 exclude the logged-in user
        logger.debug("Retrieved %s approved profiles (excluding current user)", qs.count())
        return qs


class PersonDetailView(DetailView):
    """Display details of a Person profile."""
    model = Person
    template_name = "person/person_detail.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.object
        context["profile"] = profile  # Explicit alias for clarity

        # Check if current logged-in user already follows this profile.user
        is_followed = Follow.objects.filter(
            follower=self.request.user,
            following=profile.user
        ).exists()

        context["is_followed"] = is_followed
        return context

class PersonDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a user account (CustomUser + Person)."""

    model = CustomUser
    template_name = "person/person_confirm_delete.html"
    success_url = reverse_lazy("home")

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        logger.warning("Deleting user %s and logging them out", user.pk)
        logout(request)  # Ensure session cleanup
        messages.success(request, "Your account has been deleted. Goodbye! 👋")
        return super().delete(request, *args, **kwargs)

@login_required
def toggle_business_name(request):
    """Toggle whether to display the business name instead of personal name."""
    try:
        profile = request.user.profile
    except Person.DoesNotExist:
        messages.error(request, "Profile not found. Please create one first.")
        return redirect("person_create")

    profile.use_business_name = not profile.use_business_name
    profile.save()
    state = "now visible" if profile.use_business_name else "hidden"
    messages.success(request, f"Business name is {state} on your profile.")
    logger.info("User %s toggled business name visibility to %s", request.user.pk, state)
    return redirect("person_detail", pk=profile.pk)
