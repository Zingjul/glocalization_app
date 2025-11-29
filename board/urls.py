from django.urls import path
from .views import PostBoardListView, SeekerBoardListView, UnifiedBoardView
app_name = "board"
urlpatterns = [
    path("posts/", PostBoardListView.as_view(), name="post_board"),
    path("seekers/", SeekerBoardListView.as_view(), name="seeker_board"),
    path("", UnifiedBoardView.as_view(), name="unified_board"),
]
