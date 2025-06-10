from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    CategoryListView,
    location_autocomplete,
    PostUpdateView,
    PostDeleteView,
    ProductPostCreateView, ServicePostCreateView, LaborPostCreateView,  location_autocomplete, PostEditBaseView,
    PostEditProductView,
    PostEditServiceView,
    PostEditLaborView, PendingPostsByUserView
)

urlpatterns = [
    path("", PostListView.as_view(), name="post_home"),  # This shows the list of posts (main page)
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("search/autocomplete/", location_autocomplete, name="location_autocomplete"),  # autocomplete API endpoint
    path("post/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path('create/product/', ProductPostCreateView.as_view(), name='create_product'),
    path('create/service/', ServicePostCreateView.as_view(), name='create_service'),
    path('create/labor/', LaborPostCreateView.as_view(), name='create_labor'),
    path("autocomplete/", location_autocomplete, name="location_autocomplete"),  # ✅ Add this route

    path('edit/product/<int:pk>/', PostEditProductView.as_view(), name='post_edit_product'),
    path('edit/service/<int:pk>/', PostEditServiceView.as_view(), name='post_edit_service'),
    path('edit/labor/<int:pk>/', PostEditLaborView.as_view(), name='post_edit_labor'),
    path('my-pending-posts/', PendingPostsByUserView.as_view(), name='my_pending_posts'),
]
