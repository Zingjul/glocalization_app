from django.urls import path
from .views import ContinentList, ContinentDetail, CountryList, CountryDetail, StateList, StateDetail, TownList, TownDetail, PersonSearch, PostSearch, CountryFilter, StateFilter, TownFilter

urlpatterns = [
    path('continents/', ContinentList.as_view(), name='continent-list'),
    path('continents/<int:pk>/', ContinentDetail.as_view(), name='continent-detail'),
    path('countries/', CountryList.as_view(), name='country-list'),
    path('countries/<int:pk>/', CountryDetail.as_view(), name='country-detail'),
    path('states/', StateList.as_view(), name='state-list'),
    path('states/<int:pk>/', StateDetail.as_view(), name='state-detail'),
    path('towns/', TownList.as_view(), name='town-list'),
    path('towns/<int:pk>/', TownDetail.as_view(), name='town-detail'),
    path('person_search/', PersonSearch.as_view(), name='person_search'),
    path('post_search/', PostSearch.as_view(), name='post_search'),
    path('country_filter/', CountryFilter.as_view(), name='country_filter'),
    path('state_filter/', StateFilter.as_view(), name='state_filter'),
    path('town_filter/', TownFilter.as_view(), name='town_filter'),
]