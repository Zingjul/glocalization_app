from django.urls import path
from .views import ContinentList, ContinentDetail, CountryList, CountryDetail, StateList, StateDetail, TownList, TownDetail

urlpatterns = [
    path('continents/', ContinentList.as_view(), name='continent-list'),
    path('continents/<int:pk>/', ContinentDetail.as_view(), name='continent-detail'),
    path('countries/', CountryList.as_view(), name='country-list'),
    path('countries/<int:pk>/', CountryDetail.as_view(), name='country-detail'),
    path('states/', StateList.as_view(), name='state-list'),
    path('states/<int:pk>/', StateDetail.as_view(), name='state-detail'),
    path('towns/', TownList.as_view(), name='town-list'),
    path('towns/<int:pk>/', TownDetail.as_view(), name='town-detail'),
]