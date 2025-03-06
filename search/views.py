# search/views.py

from django.shortcuts import render
from django.db.models import Q
from posts.models import Post
from person.models import Person
from .forms import SearchForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def search(request):
    form = SearchForm(request.GET)
    post_results = []
    person_results = []
    query = None

    if form.is_valid():
        query = form.cleaned_data['query']

        # Search Post model
        post_results = Post.objects.filter(
            Q(category__name__icontains=query) | Q(product_name__icontains=query)
        )

        # Search Person model
        person_results = Person.objects.filter(business_name__icontains=query)

    paginator = Paginator(post_results, 10)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'search/results.html', {
        'form': form,
        'posts': posts,
        'person_results': person_results,
        'query': query,
        'is_paginated': posts.has_other_pages() if posts else False,
        'page_obj': posts,
    })