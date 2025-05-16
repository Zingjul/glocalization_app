from django.urls import path
from .views import PostSearchView, PersonSearchView, SearchResultsView, location_autocomplete
urlpatterns = [
    path("posts/", PostSearchView.as_view(), name="post_search"),
    path("persons/", PersonSearchView.as_view(), name="person_search"),
    path("results/", SearchResultsView.as_view(), name="search_results"),
    path("autocomplete/", location_autocomplete, name="location_autocomplete"),
]