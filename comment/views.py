from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse
from comment.models import Comment
from comment.forms import CommentForm

# 📝 List comments for a generic object
class CommentListView(ListView):
    model = Comment
    template_name = "comment/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        self.app_label = self.kwargs["app_label"]
        self.model_name = self.kwargs["model_name"]
        self.object_id = self.kwargs["object_id"]

        self.content_type = get_object_or_404(
            ContentType, app_label=self.app_label, model=self.model_name
        )

        return Comment.objects.filter(
            content_type=self.content_type,
            object_id=self.object_id,
            parent__isnull=True
        ).select_related("author").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        model_class = self.content_type.model_class()
        target_object = get_object_or_404(model_class, id=self.object_id)

        context.update({
            "form": CommentForm(),
            "app_label": self.app_label,
            "model_name": self.model_name,
            "object_id": self.object_id,
            "target_object": target_object,
        })
        return context

# ➕ Create comment via standalone route
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.app_label = kwargs["app_label"]
        self.model_name = kwargs["model_name"]
        self.object_id = kwargs["object_id"]
        self.content_type = get_object_or_404(ContentType, app_label=self.app_label, model=self.model_name)
        self.model_class = self.content_type.model_class()
        self.content_object = get_object_or_404(self.model_class, id=self.object_id)
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            from django.contrib import messages
            messages.error(request, "Your profile must be approved before you can comment.")
            from django.shortcuts import redirect
            return redirect(self.content_object.get_absolute_url())

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.content_type = self.content_type
        form.instance.object_id = self.object_id
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["target_object"] = self.content_object
        return context

    def get_success_url(self):
        return self.content_object.get_absolute_url()

# 🔍 View a single comment
class CommentDetailView(DetailView):
    model = Comment
    template_name = "comment/comment_detail.html"
    context_object_name = "comment"

# ✏️ Update comment
class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comment/comment_form.html"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()

# 🗑️ Delete comment
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "comment/comment_confirm_delete.html"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return self.object.content_object.get_absolute_url()
