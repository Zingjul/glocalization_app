# person/urls.py
from django.urls import path, include
from .views import (
    PersonListView, PersonDetailView,
    PersonDeleteView, toggle_business_name, PersonSetupView,
        gallery_view, gallery_upload, gallery_delete, 
    gallery_update_caption, gallery_toggle_visibility
)

urlpatterns = [
    # ------------------- Person Endpoints -------------------
    path("", PersonListView.as_view(), name="person_list"),
    path("<int:pk>/", PersonDetailView.as_view(), name="person_detail"),
    path("toggle_business_name/", toggle_business_name, name="toggle_business_name"),
    path("<int:pk>/delete/", PersonDeleteView.as_view(), name="person_delete"),
    path("profile/setup/", PersonSetupView.as_view(), name="person_setup"),

    # ------------------- Gallery Endpoints -------------------
    path("gallery/", gallery_view, name="gallery_view"),
    path("gallery/upload/", gallery_upload, name="gallery_upload"),
    path("gallery/delete/<int:pk>/", gallery_delete, name="gallery_delete"),
    path("gallery/caption/<int:pk>/", gallery_update_caption, name="gallery_update_caption"),
    path("gallery/visibility/<int:pk>/", gallery_toggle_visibility, name="gallery_toggle_visibility"),
    # ------------------- Location Endpoints (imported from custom_search) -------------------
    path("api/locations/", include("custom_search.urls")),
]
