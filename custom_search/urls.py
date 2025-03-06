from django.urls import path
from .views import CustomSearchView, GetCountriesView, GetStatesView, GetTownsView

urlpatterns = [
    path('', CustomSearchView.as_view(), name='custom_search'),
    path('get_countries/', GetCountriesView.as_view(), name='get_countries'),
    path('get_states/', GetStatesView.as_view(), name='get_states'),
    path('get_towns/', GetTownsView.as_view(), name='get_towns'),
]