from django.urls import path
from .views import SearchView
from .views import SearchView, pending_location_approvals, approve_location_single
urlpatterns = [
    path("search/", SearchView.as_view(), name="search"),  # Main search view
    path('approve-locations/', pending_location_approvals, name='approve_locations'),
    path('approve-location/<int:person_id>/<str:location_type>/', approve_location_single, name='approve_location_single'),
]
