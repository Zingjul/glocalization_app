from django.urls import path
# from . import views
from .views import seekersfinder_view
app_name = "seekersfinder"
urlpatterns = [
    # path('filters/', views.filter_seeker_posts, name='filter_seekers'),
        path("", seekersfinder_view, name="seekerfinder"),
]