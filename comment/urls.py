from django.urls import path
from .views import (
    CommentListView, CommentDetailView, create_comment,
    CommentUpdateView, CommentDeleteView
)

urlpatterns = [
    path("post/<int:post_id>/comments/", CommentListView.as_view(), name="comment_list"),
    path("comment/<int:pk>/", CommentDetailView.as_view(), name="comment_detail"),
    path("post/<int:post_id>/comment/create/", create_comment, name="create_comment"),
    path("comment/<int:pk>/edit/", CommentUpdateView.as_view(), name="edit_comment"),
    path("comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"),
]
