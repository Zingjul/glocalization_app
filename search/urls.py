from django.urls import path
from .views import PostSearch, PersonSearch, SearchResultsView, location_autocomplete

urlpatterns = [
    path("results/", SearchResultsView.as_view(), name="search_results"),
    path("posts/", PostSearch.as_view(), name="post_search"),
    path("people/", PersonSearch.as_view(), name="person_search"),
    path("autocomplete/", location_autocomplete, name="location_autocomplete"),  # 🔥 Auto-suggestions endpoint
]
