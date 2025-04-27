from django.urls import path
from .views import PostSearch, PersonSearch, SearchResultsView

urlpatterns = [
    path('posts/', PostSearch.as_view(), name='post-search'),
    path('persons/', PersonSearch.as_view(), name='person-search'),
    path("results/", SearchResultsView.as_view(), name="search_results"),
]