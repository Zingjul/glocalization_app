from django.shortcuts import render
from django.db.models import Q
from person.models import Person
from posts.models import Post
from .forms import CustomSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
from django.http import JsonResponse
from .models import Country, State, Town

class CustomSearchView(View):
    template_name = 'custom_search/results.html'

    def get(self, request, *args, **kwargs):
        form = CustomSearchForm(request.GET)
        person_results = []
        post_results = []
        query = None
        continent = None
        country = None
        state = None
        town = None

        if form.is_valid():
            query = form.cleaned_data['query']
            continent = form.cleaned_data['continent']
            country = form.cleaned_data['country']
            state = form.cleaned_data['state']
            town = form.cleaned_data['town']

            person_filters = Q()
            if continent:
                person_filters &= Q(continent=continent)
            if country:
                person_filters &= Q(country=country)
            if state:
                person_filters &= Q(state=state)
            if town:
                person_filters &= Q(town=town)
            if query:
                person_filters &= Q(business_name__icontains=query)

            person_results = Person.objects.filter(person_filters)

            if query:
                post_results = Post.objects.filter(
                    Q(category__name__icontains=query) | Q(product_name__icontains=query)
                )

        paginator = Paginator(post_results, 10)
        page = request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context = {
            'form': form,
            'posts': posts,
            'person_results': person_results,
            'query': query,
            'continent': continent,
            'country': country,
            'state': state,
            'town': town,
            'is_paginated': posts.has_other_pages() if posts else False,
            'page_obj': posts,
        }
        return render(request, self.template_name, context)

class GetCountriesView(View):
    def get(self, request, *args, **kwargs):
        continent_id = request.GET.get('continent_id')
        countries = Country.objects.filter(continent_id=continent_id).values('id', 'name')
        return JsonResponse(list(countries), safe=False)

class GetStatesView(View):
    def get(self, request, *args, **kwargs):
        country_id = request.GET.get('country_id')
        states = State.objects.filter(country_id=country_id).values('id', 'name')
        return JsonResponse(list(states), safe=False)

class GetTownsView(View):
    def get(self, request, *args, **kwargs):
        state_id = request.GET.get('state_id')
        towns = Town.objects.filter(state_id=state_id).values('id', 'name')
        return JsonResponse(list(towns), safe=False)