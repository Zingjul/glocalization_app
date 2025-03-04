from django.urls import path
from .views import CustomSearchView

urlpatterns = [
    path('', CustomSearchView.as_view(), name='custom_search'),
]