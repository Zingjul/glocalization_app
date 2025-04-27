from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Post, Category
from .forms import PostForm

class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"

class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"
    success_url = reverse_lazy("post_list")

    def dispatch(self, request, *args, **kwargs):
        """ Ensure user has a profile before accessing the post form. """
        profile = getattr(request.user, "profile", None)  # ✅ Avoid crashes if profile is missing

        if not profile:
            messages.warning(request, "You need to create your profile before posting a product.")
            return redirect("person_edit", pk=request.user.pk)  # ✅ Redirect users to create their profile

        if not (profile.continent and profile.country and profile.state and profile.town and profile.business_name):
            messages.warning(request, "Complete your profile before posting.")
            return redirect("person_edit", pk=profile.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user

        # 🔥 Prevent overwriting custom location selection
        if form.cleaned_data["use_default_location"]:
            profile = self.request.user.profile
            form.instance.continent = profile.continent
            form.instance.country = profile.country
            form.instance.state = profile.state
            form.instance.town = profile.town
        
        return super().form_valid(form)

class CategoryListView(ListView):
    model = Category
    template_name = "posts/category_list.html"
    context_object_name = "categories"
