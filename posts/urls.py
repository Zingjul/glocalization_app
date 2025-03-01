from django.urls import path
from .views import PostView, PostDetailedView, PostUpdateView, PostCreateView, PostDeleteView

urlpatterns=[
    path('recents/', PostView.as_view(), name='post_home'),
    path('recents/details/<int:pk>/', PostDetailedView.as_view(), name='post_detailed'),
    path('recents/edit/<int:pk>/', PostUpdateView.as_view(), name='post_edit'),
    path('recents/new/', PostCreateView.as_view(), name='post_create_new'),
    path('recents/delete/<int:pk>/', PostDeleteView.as_view(), name='post_delete'),
]