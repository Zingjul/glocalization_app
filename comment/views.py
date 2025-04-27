from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Comment
from .forms import CommentForm

# List all comments for a specific post
class CommentListView(ListView):
    model = Comment
    template_name = "comments/comment_list.html"
    context_object_name = "comments"

    def get_queryset(self):
        """Filter comments by post ID"""
        post_id = self.kwargs.get("post_id")
        return Comment.objects.filter(post_id=post_id).order_by("-created_at")

# Comment Detail View (Displays a single comment)
class CommentDetailView(DetailView):
    model = Comment
    template_name = "comments/comment_detail.html"
    context_object_name = "comment"

# Create a new comment
@login_required
def create_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)  # Fetch the post
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect("comment_list", post_id=post.id)
    else:
        form = CommentForm()
    return render(request, "comments/comment_form.html", {"form": form, "post": post})

# Update an existing comment
class CommentUpdateView(UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "comments/comment_form.html"

    def get_success_url(self):
        return reverse_lazy("comment_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        comment = form.save(commit=False)
        if comment.author != self.request.user:
            return redirect("comment_list", post_id=comment.post.id)
        return super().form_valid(form)

# Delete a comment
class CommentDeleteView(DeleteView):
    model = Comment
    template_name = "comments/comment_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("comment_list", kwargs={"post_id": self.object.post.id})

    def get(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author != request.user:
            return redirect("comment_list", post_id=comment.post.id)
        return super().get(request, *args, **kwargs)
