from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Post, Category, SocialMediaHandle, PostImage
from .forms import PostForm, ProductPostForm, ServicePostForm, LaborPostForm, SocialMediaHandleForm

class CategoryListView(ListView):
    model = Category
    template_name = "posts/category_list.html"
    context_object_name = "categories"


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'person', None)
        queryset = Post.objects.filter(status='approved')

        # Check for custom search (optional override)
        continent = self.request.GET.get('continent')
        country = self.request.GET.get('country')
        state = self.request.GET.get('state')
        town = self.request.GET.get('town')

        if continent or country or state or town:
            # Use search query if present
            filters = Q()
            if continent:
                filters &= Q(post_continent__name=continent)
            if country:
                filters &= Q(post_country__name=country)
            if state:
                filters &= Q(post_state__name=state)
            if town:
                filters &= Q(post_town__name=town)
            return queryset.filter(filters).order_by('-created_at')

        # Otherwise, filter by user's profile location
        if profile and profile.continent and profile.country and profile.state and profile.town:
            return queryset.filter(
                Q(post_continent=profile.continent, post_country=profile.country, post_state=profile.state, post_town=profile.town) |
                Q(post_continent=profile.continent, post_country=profile.country, post_state=profile.state, post_town__isnull=True) |
                Q(post_continent=profile.continent, post_country=profile.country, post_state__isnull=True, post_town__isnull=True) |
                Q(post_continent=profile.continent, post_country__isnull=True, post_state__isnull=True, post_town__isnull=True)
            ).order_by('-created_at')

        elif profile and profile.continent and profile.country and profile.state:
            return queryset.filter(
                Q(post_continent=profile.continent, post_country=profile.country, post_state=profile.state) |
                Q(post_continent=profile.continent, post_country=profile.country, post_state__isnull=True) |
                Q(post_continent=profile.continent, post_country__isnull=True, post_state__isnull=True)
            ).order_by('-created_at')

        elif profile and profile.continent and profile.country:
            return queryset.filter(
                Q(post_continent=profile.continent, post_country=profile.country) |
                Q(post_continent=profile.continent, post_country__isnull=True)
            ).order_by('-created_at')

        elif profile and profile.continent:
            return queryset.filter(
                Q(post_continent=profile.continent)
            ).order_by('-created_at')

        # Fallback: show all approved posts if user has no location info
        return queryset.order_by('-created_at')

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = "posts/post_form_generic.html"
    success_url = reverse_lazy("post_home")

    def get_form_class(self):
        category = (self.request.GET.get("category") or self.request.POST.get("category") or "").lower()
        if category == "product":
            return ProductPostForm
        elif category == "service":
            return ServicePostForm
        elif category == "labor":
            return LaborPostForm
        return PostForm

    def get_template_names(self):
        category = (self.request.GET.get("category") or self.request.POST.get("category") or "").lower()
        if category == "product":
            return ["posts/post_form_product.html"]
        elif category == "service":
            return ["posts/post_form_service.html"]
        elif category == "labor":
            return ["posts/post_form_labor.html"]
        return ["posts/post_form_generic.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context["social_form"] = SocialMediaHandleForm(self.request.POST)
        else:
            context["social_form"] = SocialMediaHandleForm()
        return context

    def form_valid(self, form):
        # Bind and validate the social form
        social_form = SocialMediaHandleForm(self.request.POST)
        if not social_form.is_valid():
            return self.form_invalid(form)

        # Set author and approval fields
        form.instance.author = self.request.user
        form.instance.is_approved = False

        # Attach category to the post
        category_param = (self.request.GET.get("category") or self.request.POST.get("category") or "").strip().lower()
        form.instance.category = get_object_or_404(Category, name__iexact=category_param)

        # Save the main Post instance
        response = super().form_valid(form)

        # Save the social media handle
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        # Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f"image{i}")
            if image:
                PostImage.objects.create(post=self.object, image=image)

        # Success message
        messages.success(self.request, "Post submitted successfully and is under review!")
        return response


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post

    def get_form_class(self):
        category = self.object.category.name.lower()
        if category == "product":
            return ProductPostForm
        elif category == "service":
            return ServicePostForm
        elif category == "labor":
            return LaborPostForm
        return PostForm

    def get_template_names(self):
        category = self.object.category.name.lower()
        if category == "product":
            return ["posts/post_edit_product.html"]
        elif category == "service":
            return ["posts/post_edit_service.html"]
        elif category == "labor":
            return ["posts/post_edit_labor.html"]
        return ["posts/post_edit_generic.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        social_form = SocialMediaHandleForm(instance=getattr(post, "social_handles", None))
        context["social_form"] = social_form
        context["post"] = post
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        social_form = SocialMediaHandleForm(request.POST, instance=getattr(self.object, "social_handles", None))
        if form.is_valid() and social_form.is_valid():
            self.object = form.save()
            social_handle = social_form.save(commit=False)
            social_handle.post = self.object
            social_handle.save()
            messages.success(self.request, "Post updated successfully.")
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, social_form=social_form)
            )
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('post_home')

class ProductPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = ProductPostForm
    template_name = 'posts/post_form_product.html'
    success_url = reverse_lazy('post_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        social_form = SocialMediaHandleForm(self.request.POST)
        if social_form.is_valid():
            form.instance.user = self.request.user
            form.instance.is_approved = False
            form.instance.category = get_object_or_404(Category, name__iexact="Product")
            response = super().form_valid(form)
            SocialMediaHandle.objects.create(post=self.object, **social_form.cleaned_data)
            messages.success(self.request, "Product post submitted successfully and under review!")
            return response
        return self.form_invalid(form)


class ServicePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = ServicePostForm
    template_name = 'posts/post_form_service.html'
    success_url = reverse_lazy('post_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        social_form = SocialMediaHandleForm(self.request.POST)
        if social_form.is_valid():
            form.instance.user = self.request.user
            form.instance.is_approved = False
            form.instance.category = get_object_or_404(Category, name__iexact="Service")
            response = super().form_valid(form)
            SocialMediaHandle.objects.create(post=self.object, **social_form.cleaned_data)
            messages.success(self.request, "Service post submitted successfully and under review!")
            return response
        return self.form_invalid(form)


class LaborPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = LaborPostForm
    template_name = 'posts/post_form_labor.html'
    success_url = reverse_lazy('post_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None)
        return context

    def form_valid(self, form):
        social_form = SocialMediaHandleForm(self.request.POST)
        if social_form.is_valid():
            form.instance.user = self.request.user
            form.instance.is_approved = False
            form.instance.category = get_object_or_404(Category, name__iexact="Labor")
            response = super().form_valid(form)
            SocialMediaHandle.objects.create(post=self.object, **social_form.cleaned_data)
            messages.success(self.request, "Labor post submitted successfully and under review!")
            return response
        return self.form_invalid(form)

class PostEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    success_url = reverse_lazy('post_home')

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostEditProductView(PostEditBaseView):
    form_class = ProductPostForm
    template_name = 'posts/post_edit_product.html'


class PostEditServiceView(PostEditBaseView):
    form_class = ServicePostForm
    template_name = 'posts/post_edit_service.html'


class PostEditLaborView(PostEditBaseView):
    form_class = LaborPostForm
    template_name = 'posts/post_edit_labor.html'


class PendingPostsByUserView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/pending_posts_by_user.html"  # Create this template
    context_object_name = "pending_posts"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, status='pending').order_by('-created_at')
        
@require_GET
def location_autocomplete(request):
    from custom_search.models import Continent, Country, State, Town

    location_type = request.GET.get("type", "").lower()
    query = request.GET.get("q", "")

    model_map = {
        "continent": Continent,
        "country": Country,
        "state": State,
        "town": Town,
    }

    model = model_map.get(location_type)
    if not model:
        return JsonResponse({"results": []})

    results = model.objects.filter(name__icontains=query).values_list("name", flat=True)[:10]
    return JsonResponse({"results": list(results)})
