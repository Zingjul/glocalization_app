from django.urls import path
# from . import views
from .views import postfinder_view

urlpatterns = [
    # path('filters/', views.filter_posts, name='filter_posts'),
    path("", postfinder_view, name="postfinder"),
]