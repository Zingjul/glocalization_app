from django.shortcuts import render
from django.db.models import Q
from person.models import Person
from posts.models import Post
from .forms import CustomSearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View

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
                post_results = Post.objects.filter(category__name__icontains=query)

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