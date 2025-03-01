from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Person
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from .forms import PersonForm

class UserProfileDetailedView(LoginRequiredMixin, DetailView):
    model = Person
    template_name = "person/person_detailed_profile.html"
    context_object_name = "person"

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user)

class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_profile_edit.html"
    context_object_name = "form"

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user)

    def get_success_url(self):
        return reverse('person:person_detailed_profile')

class UserProfileCreateView(LoginRequiredMixin, CreateView):
    model = Person
    form_class = PersonForm
    template_name = "person/person_profile_create_new.html"
    context_object_name = "form"

    def form_valid(self, form):
        person = form.save(commit=False)
        person.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('person:person_detailed_profile')

class UserProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = Person
    template_name = 'person/person_profile_delete.html'
    success_url = reverse_lazy('login')

    def get_object(self):
        return get_object_or_404(Person, user=self.request.user)

@login_required
def toggle_business_name(request):
    profile = get_object_or_404(Person, user=request.user)
    profile.use_business_name = not profile.use_business_name
    profile.save()
    return redirect('person:person_detailed_profile')