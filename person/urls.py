from django.urls import path
from .views import (
    PersonCreateView, PersonListView, PersonDetailView, PersonUpdateView, PersonDeleteView, toggle_business_name,
)

urlpatterns = [
    path("create/", PersonCreateView.as_view(), name="person_create"), 
    path("", PersonListView.as_view(), name="person_list"),  # List of users
    path("<int:pk>/", PersonDetailView.as_view(), name="person_detail"),  # Profile details
    path("<int:pk>/edit/", PersonUpdateView.as_view(), name="person_edit"),  # Profile update
    path("toggle_business_name/", toggle_business_name, name="toggle_business_name"),  # Business name visibility toggle
    path("<int:pk>/delete/", PersonDeleteView.as_view(), name="person_delete"),
]
