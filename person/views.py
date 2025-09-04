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

from .forms import PersonForm
from .models import Person, PendingLocationRequest
from accounts.models import CustomUser
from custom_search.models import Continent, Country, State, Town   # ✅ only from here

logger = logging.getLogger(__name__)
class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "profile"):
            return redirect("person_detail", pk=request.user.profile.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        from custom_search.models import Town

        person = form.save(commit=False)
        person.user = self.request.user

        selected_town_id = self.request.POST.get("town")
        typed_town_name = self.request.POST.get("town_input", "").strip()

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
            # Assign fallback 'Unspecified' town
            person.town = unspecified_town
            person.approval_status = "pending"
            person.save()

            # Store pending location request
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
                "Profile created successfully! 🎉 Your town is pending admin approval."
            )
            return super().form_valid(form)

        else:
            form.add_error("town", "Please select a town or type one in.")
            return self.form_invalid(form)

        person.approval_status = "pending"
        person.save()

        messages.success(self.request, "Profile created successfully! 🎉 Pending approval.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "continents": Continent.objects.all(),
            "countries": Country.objects.all(),
            "states": State.objects.all(),
            "towns": Town.objects.all(),
            "location_fields": ["continent", "country", "state", "town"],
            "location_input_fields": ["continent_input", "country_input", "state_input", "town_input"],
            "has_pending_location": False,
            "approval_status": None,
        })
        return context


class PersonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        person = self.get_object()
        return person.user == self.request.user and person.approval_status != "pending"

    def handle_no_permission(self):
        messages.warning(
            self.request,
            "Your profile is under review and cannot be edited until approved."
        )
        return redirect("person_detail", pk=self.get_object().pk)

    def form_valid(self, form):
        from custom_search.models import Town

        person = form.save(commit=False)
        person.user = self.request.user

        selected_town_id = self.request.POST.get("town")
        typed_town_name = self.request.POST.get("town_input", "").strip()

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
            # Fallback assignment
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

        person.save()
        messages.success(self.request, "Profile updated successfully! 🎉")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
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
    """List all registered Person profiles."""

    model = Person
    template_name = "person/person_list.html"
    context_object_name = "profiles"

    def get_queryset(self):
        qs = Person.objects.all()
        logger.debug("Retrieved %s profiles", qs.count())
        return qs


class PersonDetailView(DetailView):
    """Display details of a Person profile."""

    model = Person
    template_name = "person/person_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object  # Explicit alias for template clarity
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
