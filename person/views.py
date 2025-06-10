from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Person
from .forms import PersonForm
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import UserPassesTestMixin


class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    template_name = "person/person_form.html"
    form_class = PersonForm

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "profile"):
            return redirect("person_detail", pk=request.user.profile.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})
     
# List all registered user profiles
class PersonListView(LoginRequiredMixin, ListView):
    model = Person
    template_name = "person/person_list.html"
    context_object_name = "profiles"  # 👈 This ensures the correct variable name is passed

    def get_queryset(self):
        return Person.objects.all()  # Retrieves all registered profiles

# Detail view for an individual profile
class PersonDetailView(DetailView):
    model = Person
    template_name = "person/person_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.object  # 👈 So your template can use {{ profile }}
        return context
# Update profile view (User can edit their own profile)
class PersonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def test_func(self):
        return self.get_object().user == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["location_fields"] = ["continent", "country", "state", "town"]
        context["location_input_fields"] = ["continent_input", "country_input", "state_input", "town_input"]
        context["has_pending_location"] = any([
            self.object.continent_input,
            self.object.country_input,
            self.object.state_input,
            self.object.town_input,
        ])
        return context
# Delete account view (User can delete their own account)
class PersonDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "person/person_confirm_delete.html"
    success_url = reverse_lazy("home")  # Redirect after deletion

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        logout(request)  # Logs out the user before deleting the account
        return super().delete(request, *args, **kwargs)

# Toggle Business Name Visibility
@login_required
def toggle_business_name(request):
    try:
        profile = request.user.profile
    except Person.DoesNotExist:
        return redirect("person_create")

    profile.use_business_name = not profile.use_business_name
    profile.save()
    return redirect("person_detail", pk=profile.pk)