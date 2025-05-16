from django.urls import path
from .views import PostListView, PostDetailView, PostCreateView, CategoryListView, location_autocomplete,  PostUpdateView, PostDeleteView

urlpatterns = [
    path("", PostListView.as_view(), name="post_home"),   #this is actually the form list
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("search/autocomplete/", location_autocomplete, name="location_autocomplete"),  # 🔥 Auto-suggestions endpoint
    path('post/<int:pk>/edit/', PostUpdateView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
]
