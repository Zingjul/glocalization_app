from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Post, Category, SocialMediaHandle, PostImage
from .forms import ProductPostForm, ServicePostForm, LaborPostForm, SocialMediaHandleForm
from .forms import SocialMediaHandleForm
import logging
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
from comment.forms import CommentForm
from person.models import Person  # Make sure this is imported
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback

logger = logging.getLogger(__name__)


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
            if town:
                filters |= Q(post_town__name=town, availability_scope='town')
            if state:
                filters |= Q(post_state__name=state, availability_scope='state')
            if country:
                filters |= Q(post_country__name=country, availability_scope='country')
            if continent:
                filters |= Q(post_continent__name=continent, availability_scope='continent')
            return queryset.filter(filters).order_by('-created_at')

        # Otherwise, filter by user's profile location
        if profile:
            filters = Q()
            if profile.town:
                filters |= Q(post_town=profile.town, availability_scope='town')
            if profile.state:
                filters |= Q(post_state=profile.state, availability_scope='state')
            if profile.country:
                filters |= Q(post_country=profile.country, availability_scope='country')
            if profile.continent:
                filters |= Q(post_continent=profile.continent, availability_scope='continent')
            return queryset.filter(filters).order_by('-created_at')

        # Fallback: show all approved posts if user has no location info
        return queryset.order_by('-created_at')

class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        content_type = ContentType.objects.get_for_model(post)

        # Fetch top-level comments and prefetch their nested replies and reply authors
        comments = Comment.objects.filter(
            content_type=content_type,
            object_id=post.id,
            parent__isnull=True
        ).select_related("author", "parent").prefetch_related(
            "replies",            # Direct replies
            "replies__author",    # Authors of those replies
            "replies__parent"     # In case of nested replies
        ).order_by("-created_at")

        context.update({
            "comments": comments,
            "comment_form": CommentForm(),
        })

        return context
class PostCreateView(LoginRequiredMixin, TemplateView):
    model = Post
    template_name = "posts/posts_create.html"

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
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None, self.request.FILES or None)
        return context
        
    def form_valid(self, form):
        user = self.request.user
        social_form = SocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # ✅ Ensure the author is assigned
        form.instance.author = user
        form.instance.status = "pending"

        # ✅ Set availability_scope dynamically based on location fields
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # 🧭 Attach product category to this post
        form.instance.category = get_object_or_404(Category, name__iexact="Product")

        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        # ✅ Save the main Post
        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                PostImage.objects.create(post=self.object, image=image)
       
        # 📎 Save social media handles
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Product post submitted successfully and is under review!")
        return response
class ServicePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = ServicePostForm
    template_name = 'posts/post_form_service.html'
    success_url = reverse_lazy('post_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None, self.request.FILES or None)
        return context
        
    def form_valid(self, form):
        user = self.request.user
        social_form = SocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # ✅ Set base attributes
        form.instance.author = user
        form.instance.status = "pending"

        # 🧭 Scope assignment
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # 🏷️ Attach post category
        form.instance.category = get_object_or_404(Category, name__iexact="Service")


        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        # Save post
        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                PostImage.objects.create(post=self.object, image=image)
       
        # 💬 Save social media handles
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Service post submitted successfully and is under review!")
        return response
        
class LaborPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = LaborPostForm
    template_name = 'posts/post_form_labor.html'
    success_url = reverse_lazy('post_home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(self.request.POST or None, self.request.FILES or None)
        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SocialMediaHandleForm(self.request.POST, self.request.FILES)
        
        if not social_form.is_valid():
            return self.form_invalid(form)

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # ✅ Assign author and status
        form.instance.author = user
        form.instance.status = "pending"

        # 🧭 Scope detection
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # 🏷️ Category attachment
        form.instance.category = get_object_or_404(Category, name__iexact="Labor")

        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        # 💾 Save the post
        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                PostImage.objects.create(post=self.object, image=image)
        
        # 💬 Save social media handle
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Labor post submitted successfully and is under review!")
        return response
        
class PostEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    success_url = reverse_lazy('post_home')

    def test_func(self):
        return self.request.user == self.get_object().author
    def form_valid(self, form):
        # Save the updated post first
        self.object = form.save()

        # 🗑️ Clear out old images
        self.object.images.all().delete()

        # ✅ Then add any newly uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                PostImage.objects.create(post=self.object, image=image)

        return super().form_valid(form)


class PostEditProductView(PostEditBaseView):
    model = Post
    form_class = ProductPostForm
    template_name = 'posts/post_edit_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        else:
            context['social_form'] = SocialMediaHandleForm(instance=self.object.social_handles)
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace images only if new ones were uploaded
        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.images.all().delete()
            for image in new_images:
                if image:
                    PostImage.objects.create(post=self.object, image=image)

        return super().form_valid(form)

class PostEditServiceView(PostEditBaseView):
    model = Post
    form_class = ServicePostForm
    template_name = 'posts/post_edit_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        else:
            context['social_form'] = SocialMediaHandleForm(instance=self.object.social_handles)
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace images only if new ones were uploaded
        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.images.all().delete()
            for image in new_images:
                if image:
                    PostImage.objects.create(post=self.object, image=image)

        return super().form_valid(form)


class PostEditLaborView(PostEditBaseView):
    model = Post
    form_class = LaborPostForm
    template_name = 'posts/post_edit_labor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        else:
            context['social_form'] = SocialMediaHandleForm(instance=self.object.social_handles)
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace images only if new ones were uploaded
        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.images.all().delete()
            for image in new_images:
                if image:
                    PostImage.objects.create(post=self.object, image=image)

        return super().form_valid(form)

class PendingPostsByUserView(LoginRequiredMixin, ListView):
    model = Post
    template_name = "posts/pending_posts_by_user.html"  # Create this template
    context_object_name = "pending_posts"

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user, status='pending').order_by('-created_at')


def get_posts_visible_to_user(user):
    location = user.profile
    logger.info(f"User Town: {location.town} ({location.town.name})")

    return Post.objects.filter(
        Q(availability_scope='global') |

        (
            Q(availability_scope='continent') &
            (
                Q(post_continent=location.continent) |
                Q(post_continent_input__iexact=location.continent.name)
            )
        ) |

        (
            Q(availability_scope='country') &
            (
                Q(post_country=location.country) |
                Q(post_country_input__iexact=location.country.name)
            )
        ) |

        (
            Q(availability_scope='state') &
            (
                Q(post_state=location.state) |
                Q(post_state_input__iexact=location.state.name)
            )
        ) |

        (
            Q(availability_scope='town') &
            (
                Q(post_town=location.town) |
                Q(post_town_input__iexact=location.town.name)
            )
        )
    ).distinct()
def home(request):
    visible_posts = get_posts_visible_to_user(request.user)
    return render(request, 'posts/post_list.html', {'posts': visible_posts})
    
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