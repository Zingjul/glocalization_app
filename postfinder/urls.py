from django.urls import path
from .views import postfinder_view

urlpatterns = [
    # Free-text search (results.html)
    path("search/", postfinder_view, name="postfinder_search"),
]
