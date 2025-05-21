from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import ListView
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

from .models import Continent, Country, State, Town
from person.models import Person
from posts.models import Post
from .forms import CustomSearchForm

class SearchView(ListView):
    template_name = "custom_search/search_results.html"
    context_object_name = "results"

    def get_queryset(self):
        """Returns empty base queryset — actual results go to context instead."""
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = CustomSearchForm(self.request.GET)
        results = {
            'form': form,
            'people': [],
            'posts': [],
            'countries': [],
            'states': [],
            'towns': []
        }

        if form.is_valid():
            query = form.cleaned_data.get("query")
            continent = form.cleaned_data.get("continent")
            country = form.cleaned_data.get("country")
            state = form.cleaned_data.get("state")
            town = form.cleaned_data.get("town")

            if query:
                results['people'] = Person.objects.filter(business_name__icontains=query)
                results['posts'] = Post.objects.filter(product_name__icontains=query)

            if continent:
                results['countries'] = Country.objects.filter(continent=continent)
            if country:
                results['states'] = State.objects.filter(country=country)
            if state:
                results['towns'] = Town.objects.filter(state=state)

        context.update(results)
        return context

def is_moderator(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_moderator)
def pending_location_approvals(request):
    pending = Person.objects.filter(
        continent_input__isnull=False, continent__isnull=True
    ) | Person.objects.filter(
        country_input__isnull=False, country__isnull=True
    ) | Person.objects.filter(
        state_input__isnull=False, state__isnull=True
    ) | Person.objects.filter(
        town_input__isnull=False, town__isnull=True
    )

    return render(request, 'custom_search/location_approvals.html', {'pending_people': pending})

@user_passes_test(is_moderator)
def approve_location_single(request, person_id, location_type):
    person = get_object_or_404(Person, pk=person_id)
    value = getattr(person, f"{location_type}_input")

    model_map = {
        'continent': Continent,
        'country': Country,
        'state': State,
        'town': Town,
    }

    if location_type in model_map and value:
        obj, _ = model_map[location_type].objects.get_or_create(name=value)
        setattr(person, location_type, obj)
        setattr(person, f"{location_type}_input", None)
        person.save()
        messages.success(request, f"{location_type.capitalize()} '{value}' approved and added.")

    return HttpResponseRedirect(reverse('approve_locations'))
