from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    CategoryListView,
    location_autocomplete,
    PostUpdateView,
    PostDeleteView,
    ProductPostCreateView, 
    ServicePostCreateView, 
    LaborPostCreateView,  
    PostEditProductView,
    PostEditServiceView,
    PostEditLaborView, 
    PendingPostsByUserView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", PostListView.as_view(), name="post_home"),  # Main post list
    path("<int:pk>/", PostDetailView.as_view(), name="post_detail"),
    path("create/", PostCreateView.as_view(), name="post_create"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("search/autocomplete/", location_autocomplete, name="location_autocomplete"),  # Autocomplete API endpoint
    path("search/", PostListView.as_view(), name="post_search"),  # ✅ Add search functionality
    path("post/<int:pk>/edit/", PostUpdateView.as_view(), name="post_edit"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path('create/product/', ProductPostCreateView.as_view(), name='create_product'),
    path('create/service/', ServicePostCreateView.as_view(), name='create_service'),
    path('create/labor/', LaborPostCreateView.as_view(), name='create_labor'),
    path('edit/product/<int:pk>/', PostEditProductView.as_view(), name='post_edit_product'),
    path('edit/service/<int:pk>/', PostEditServiceView.as_view(), name='post_edit_service'),
    path('edit/labor/<int:pk>/', PostEditLaborView.as_view(), name='post_edit_labor'),
    path('my-pending-posts/', PendingPostsByUserView.as_view(), name='my_pending_posts'),
]
