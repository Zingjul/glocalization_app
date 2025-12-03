# board/views.py
from django.views.generic import TemplateView
from django.core.paginator import Paginator
from .models import Board
from posts.models import Post  # adjust path if different
from seekers.models import SeekerPost

class UnifiedBoardView(TemplateView):
    template_name = "board/unified_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = []

        # ✅ Handle PostBoard
        try:
            post_board = Board.objects.get(name="PostBoard")
            qs = post_board.posts.all().order_by("-created_at")
            # Filter only approved posts if 'status' field exists
            if hasattr(post_board.posts.model, "status"):
                qs = qs.filter(status="approved")

            for obj in qs:
                items.append({
                    "board": post_board,
                    "obj": obj,
                    "type": "post",
                })
        except Board.DoesNotExist:
            pass

        # ✅ Handle SeekersBoard
        try:
            seeker_board = Board.objects.get(name="SeekersBoard")
            qs = seeker_board.seeker_posts.all().order_by("-created_at")
            # Filter only approved seeker posts if 'status' field exists
            if hasattr(seeker_board.seeker_posts.model, "status"):
                qs = qs.filter(status="approved")

            for obj in qs:
                items.append({
                    "board": seeker_board,
                    "obj": obj,
                    "type": "seekerpost",
                })
        except Board.DoesNotExist:
            pass

        # Sort unified board items by creation time (most recent first)
        items.sort(key=lambda x: x["obj"].created_at if x["obj"] else 0, reverse=True)
        context["items"] = items
        return context


# optional views
class PostBoardListView(TemplateView):
    template_name = "board/post_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = Board.objects.get(name="PostBoard")
        context["posts"] = board.posts.filter(status="approved").order_by("-created_at")
        return context


class SeekerBoardListView(TemplateView):
    template_name = "board/seeker_board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = Board.objects.get(name="SeekersBoard")
        context["posts"] = board.seeker_posts.filter(status="approved").order_by("-created_at")
        return context