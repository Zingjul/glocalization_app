from django.urls import path
from .views import PostSearch, PersonSearch

urlpatterns = [
    path('posts/', PostSearch.as_view(), name='post-search'),
    path('persons/', PersonSearch.as_view(), name='person-search'),
]