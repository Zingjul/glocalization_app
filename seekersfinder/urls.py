from django.urls import path
from . import views
app_name = "seekersfinder"
urlpatterns = [
    path('filters/', views.filter_seeker_posts, name='filter_seekers'),
]