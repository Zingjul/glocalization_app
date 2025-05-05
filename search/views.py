from django.db.models import Q
from django.views.generic import ListView
from django.http import JsonResponse
from rest_framework import generics, permissions, filters
from posts.models import Post
from person.models import Person
from custom_search.models import Continent, Country, State, Town
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class PostSearch(generics.ListAPIView):
    queryset = Post.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["category__name", "product_name", "description"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get("query", None)
        continent = self.request.query_params.get("continent", None)
        country = self.request.query_params.get("country", None)
        state = self.request.query_params.get("state", None)
        town = self.request.query_params.get("town", None)

        if query is None:
            raise ValidationError({"query": ["This field is required."]})

        # Base queryset
        queryset = super().get_queryset().filter(
            Q(category__name__icontains=query) | Q(product_name__icontains=query) | Q(description__icontains=query)
        )

        # Filter by location (if provided)
        if continent:
            queryset = queryset.filter(continent__name__icontains=continent)
        if country:
            queryset = queryset.filter(country__name__icontains=country)
        if state:
            queryset = queryset.filter(state__name__icontains=state)
        if town:
            queryset = queryset.filter(town__name__icontains=town)

        return queryset

class PersonSearch(generics.ListAPIView):
    queryset = Person.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ["business_name"]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get("query", None)
        if query is None:
            raise ValidationError({"query": ["This field is required."]})
        return super().get_queryset().filter(business_name__icontains=query)

class SearchResultsView(ListView):
    model = Post
    template_name = "search/search_results.html"
    context_object_name = "posts"

    def get_queryset(self):
        query = self.request.GET.get("query", "")
        continent = self.request.GET.get("continent", "")
        country = self.request.GET.get("country", "")
        state = self.request.GET.get("state", "")
        town = self.request.GET.get("town", "")

        posts = Post.objects.filter(
            Q(category__name__icontains=query) |
            Q(product_name__icontains=query) |
            Q(description__icontains=query)
        )

        if continent:
            posts = posts.filter(continent__name__icontains=continent)
        if country:
            posts = posts.filter(country__name__icontains=country)
        if state:
            posts = posts.filter(state__name__icontains=state)
        if town:
            posts = posts.filter(town__name__icontains=town)

        return posts

# 🔥 Auto-Suggestions API for Location Fields
def location_autocomplete(request):
    field = request.GET.get("field")
    query = request.GET.get("query", "").strip()
    
    if not field or not query:
        return JsonResponse({"suggestions": []})

    model_mapping = {
        "continent": Continent,
        "country": Country,
        "state": State,
        "town": Town
    }

    if field not in model_mapping:
        return JsonResponse({"suggestions": []})

    results = model_mapping[field].objects.filter(name__icontains=query)[:10]
    suggestions = list(results.values_list("name", flat=True))
    
    return JsonResponse({"suggestions": suggestions})
