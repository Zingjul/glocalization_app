# person/urls.py
from django.urls import path, include
from .views import (
    PersonListView, PersonDetailView,
    PersonDeleteView, toggle_business_name, PersonSetupView
)

urlpatterns = [
    # ------------------- Person Endpoints -------------------
    path("", PersonListView.as_view(), name="person_list"),
    path("<int:pk>/", PersonDetailView.as_view(), name="person_detail"),
    path("toggle_business_name/", toggle_business_name, name="toggle_business_name"),
    path("<int:pk>/delete/", PersonDeleteView.as_view(), name="person_delete"),
    path("profile/setup/", PersonSetupView.as_view(), name="person_setup"),

    # ------------------- Location Endpoints (imported from custom_search) -------------------
    path("api/locations/", include("custom_search.urls")),
]
