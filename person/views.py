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

class PersonCreateView(LoginRequiredMixin, CreateView):
    model = Person
    template_name = "person/person_form.html"
    fields = ["business_name", "person_profile_picture", "about", "website", "use_business_name", "continent", "country", "state", "town"]

    def form_valid(self, form):
        """ Ensure profile is correctly linked to user. """
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        """ Redirect user to their profile after creation. """
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})  # 🔥 Redirects properly
        
# List all registered user profiles
class PersonListView(ListView):
    model = Person
    template_name = "person/person_list.html"

# Detail view for an individual profile
class PersonDetailView(DetailView):
    model = Person
    template_name = "person/person_detail.html"

# Update profile view (User can edit their own profile)
class PersonUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_form.html"

    def get_success_url(self):
        return reverse_lazy("person_detail", kwargs={"pk": self.object.pk})

    def get(self, request, *args, **kwargs):
        profile = self.get_object()
        if profile.user != request.user:  # Prevent others from editing another user's profile
            return redirect("person_list")
        return super().get(request, *args, **kwargs)

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
    profile = request.user.profile
    profile.use_business_name = not profile.use_business_name
    profile.save()
    return redirect("person_detail", pk=profile.pk)
