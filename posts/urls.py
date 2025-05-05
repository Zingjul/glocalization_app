from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, CategoryListView, location_autocomplete

urlpatterns = [
    path("", PostListView.as_view(), name="post_list"),
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("search/autocomplete/", location_autocomplete, name="location_autocomplete"),  # 🔥 Auto-suggestions endpoint
]
