from django.urls import path
from .views import UserProfileDetailedView, UserProfileUpdateView, UserProfileCreateView, UserProfileDeleteView, toggle_business_name

app_name = 'person' # Add app_name for namespacing

urlpatterns = [
    path('profile/info/', UserProfileDetailedView.as_view(), name='person_detailed_profile'),
    path('profile/edit/', UserProfileUpdateView.as_view(), name='person_profile_edit'),
    path('profile/new', UserProfileCreateView.as_view(), name='create_new_person_profile'),
    path('profile/delete/', UserProfileDeleteView.as_view(), name='person_profile_delete'),
    path('profile/toggle_business_name/', toggle_business_name, name='toggle_business_name'),
]