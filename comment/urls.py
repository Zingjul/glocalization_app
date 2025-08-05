from django.urls import path
from .views import (
    CommentListView,
    CommentDetailView,
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView,
)

urlpatterns = [
    # 🔍 List comments for any object
    path(
        "<str:app_label>/<str:model_name>/<int:object_id>/comments/",
        CommentListView.as_view(),
        name="comment_list",
    ),

    # ➕ Create a comment for any object (now using CBV)
    path(
        "<str:app_label>/<str:model_name>/<int:object_id>/comment/create/",
        CommentCreateView.as_view(),
        name="create_comment",
    ),

    # 🗨️ View a single comment
    path(
        "comment/<int:pk>/",
        CommentDetailView.as_view(),
        name="comment_detail",
    ),

    # ✏️ Edit a comment
    path(
        "comment/<int:pk>/edit/",
        CommentUpdateView.as_view(),
        name="edit_comment",
    ),

    # 🗑️ Delete a comment
    path(
        "comment/<int:pk>/delete/",
        CommentDeleteView.as_view(),
        name="delete_comment",
    ),
]
