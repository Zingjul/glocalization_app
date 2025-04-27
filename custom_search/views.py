from django.shortcuts import render
from django.views.generic import ListView
from .models import Continent, Country, State, Town
from person.models import Person
from posts.models import Post
from .forms import CustomSearchForm

class SearchView(ListView):
    template_name = "custom_search/search_results.html"
    context_object_name = "results"

    def get_queryset(self):
        """Filters search results based on user input"""
        form = CustomSearchForm(self.request.GET)
        queryset = None
        
        if form.is_valid():
            query = form.cleaned_data.get("query")
            continent = form.cleaned_data.get("continent")
            country = form.cleaned_data.get("country")
            state = form.cleaned_data.get("state")
            town = form.cleaned_data.get("town")

            # Basic text search across posts and persons
            if query:
                queryset = list(Person.objects.filter(business_name__icontains=query)) + \
                           list(Post.objects.filter(product_name__icontains=query))
            
            # Filtering based on locations
            if continent:
                queryset = list(Country.objects.filter(continent=continent)) + queryset if queryset else list(Country.objects.filter(continent=continent))
            if country:
                queryset = list(State.objects.filter(country=country)) + queryset if queryset else list(State.objects.filter(country=country))
            if state:
                queryset = list(Town.objects.filter(state=state)) + queryset if queryset else list(Town.objects.filter(state=state))

        return queryset or []

    def get_context_data(self, **kwargs):
        """Adds the search form to the context"""
        context = super().get_context_data(**kwargs)
        context["form"] = CustomSearchForm(self.request.GET)
        return context
