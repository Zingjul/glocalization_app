# board/views.py
from django.views.generic import ListView
from .models import Board
from django.views.generic import TemplateView
from django.contrib.contenttypes.models import ContentType

class PostBoardListView(ListView):
    """
    Display all approved Post entries that appear on the public board.
    """
    model = Board
    template_name = "board/post_board.html"
    context_object_name = "posts"
    paginate_by = 20  # optional

    def get_queryset(self):
        return Board.objects.filter(
            content_type__model="post"
        ).order_by("-created_at")


class SeekerBoardListView(ListView):
    """
    Display all approved SeekerPost entries that appear on the public board.
    """
    model = Board
    template_name = "board/seeker_board.html"
    context_object_name = "posts"
    paginate_by = 20  # optional

    def get_queryset(self):
        return Board.objects.filter(
            content_type__model="seekerpost"
        ).order_by("-created_at")

class UnifiedBoardView(TemplateView):
    template_name = "board/unified_board.html"
    paginate_by = 20  # optional if you implement pagination manually

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Fetch all board entries (newest first)
        qs = Board.objects.all().order_by("-created_at")

        items = []
        for entry in qs:
            # resolve the actual linked object; using content_object
            obj = getattr(entry, "content_object", None)
            obj_type = None
            if entry.content_type:
                obj_type = entry.content_type.model  # 'post' or 'seekerpost', etc.

            # Safety: if obj is deleted or missing, still include the board row
            items.append({
                "board": entry,
                "obj": obj,
                "type": obj_type,
            })

        context["items"] = items
        return context