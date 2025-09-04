# person/urls.py
from django.urls import path, include
from .views import (
    PersonCreateView, PersonListView, PersonDetailView,
    PersonUpdateView, PersonDeleteView, toggle_business_name,
)

urlpatterns = [
    # ------------------- Person Endpoints -------------------
    path("create/", PersonCreateView.as_view(), name="person_create"), 
    path("", PersonListView.as_view(), name="person_list"),
    path("<int:pk>/", PersonDetailView.as_view(), name="person_detail"),
    path("<int:pk>/edit/", PersonUpdateView.as_view(), name="person_edit"),
    path("toggle_business_name/", toggle_business_name, name="toggle_business_name"),
    path("<int:pk>/delete/", PersonDeleteView.as_view(), name="person_delete"),

    # ------------------- Location Endpoints (imported from custom_search) -------------------
    path("api/locations/", include("custom_search.urls")),
]
