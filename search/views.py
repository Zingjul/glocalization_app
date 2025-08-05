from django.db.models import Q
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponseBadRequest
from posts.models import Post
from person.models import Person
from custom_search.models import Continent, Country, State, Town

# View to handle post search
class PostSearchView(ListView):
    model = Post
    context_object_name = "posts"
    template_name = "search/post_search_results.html"  # You can change this to your preferred template

    def get_queryset(self):
        query = self.request.GET.get("query")
        continent = self.request.GET.get("continent")
        country = self.request.GET.get("country")
        state = self.request.GET.get("state")
        town = self.request.GET.get("town")

        if not query:
            return Post.objects.none()

        queryset = Post.objects.filter(
            Q(category__name__icontains=query) |
            Q(product_name__icontains=query) |
            Q(description__icontains=query)
        )

        if continent:
            queryset = queryset.filter(continent__name__icontains=continent)
        if country:
            queryset = queryset.filter(country__name__icontains=country)
        if state:
            queryset = queryset.filter(state__name__icontains=state)
        if town:
            queryset = queryset.filter(town__name__icontains=town)

        return queryset

# View to handle person search
class PersonSearchView(ListView):
    model = Person
    context_object_name = "persons"
    template_name = "search/person_search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("query")
        if not query:
            return Person.objects.none()
        return Person.objects.filter(business_name__icontains=query)

# Template view for posts if needed separately
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

# 🔥 Auto-Suggestions API for Location Fields (pure Django)
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
