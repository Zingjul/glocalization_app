from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from .models import Post, Category
from .forms import PostForm
from custom_search.models import Continent, Country, State, Town

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
        profile = getattr(request.user, "profile", None)

        if not profile:
            messages.warning(request, "You need to create your profile before posting a product.")
            return redirect("person_create")  # ✅ Redirect to profile creation instead

        if not (profile.continent and profile.country and profile.state and profile.town and profile.business_name):
            messages.warning(request, "Complete your profile before posting.")
            return redirect("person_edit", pk=profile.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user

        # 🔥 Handle location fields separately
        if form.cleaned_data["use_default_location"]:
            profile = self.request.user.profile
            form.instance.continent = profile.continent
            form.instance.country = profile.country
            form.instance.state = profile.state
            form.instance.town = profile.town
        else:
            form.instance.continent = form.cleaned_data.get("continent")
            form.instance.country = form.cleaned_data.get("country")
            form.instance.state = form.cleaned_data.get("state")
            form.instance.town = form.cleaned_data.get("town")

        return super().form_valid(form)

class CategoryListView(ListView):
    model = Category
    template_name = "posts/category_list.html"
    context_object_name = "categories"

# 🔥 Auto-Suggestions API for Location Fields
def location_autocomplete(request):
    field = request.GET.get("field")
    query = request.GET.get("query", "").strip()
    
    if not field or field not in ["continent", "country", "state", "town"]:
        return JsonResponse({"suggestions": [], "error": "Invalid field parameter."})

    # Provide common location suggestions when input is empty
    default_suggestions = {
        "continent": ["Africa", "Asia", "Europe", "North America", "South America", "Oceania"],
        "country": ["United States", "United Kingdom", "Nigeria", "India", "Canada"],
        "state": ["California", "Lagos", "New York", "Texas", "Abuja"],
        "town": ["London", "New York City", "Lagos", "Mumbai", "Toronto"]
    }

    if not query:
        return JsonResponse({"suggestions": default_suggestions.get(field, [])})

    model_mapping = {
        "continent": Continent,
        "country": Country,
        "state": State,
        "town": Town
    }

    try:
        results = model_mapping[field].objects.filter(name__icontains=query).order_by("name")[:10]
        suggestions = list(results.values_list("name", flat=True))
        return JsonResponse({"suggestions": suggestions})
    except Exception as e:
        return JsonResponse({"suggestions": [], "error": str(e)})


class PostUpdateView(UpdateView):
    model = Post
    fields = ['category', 'product_name', 'description', 'price']  # include the fields you want editable
    template_name = 'posts/post_form.html'
    success_url = reverse_lazy('posts:list')  # Change to your posts list URL name

class PostDeleteView(DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:list')