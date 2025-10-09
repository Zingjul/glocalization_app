from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.db.models import Q
from .models import Post, Category, SocialMediaHandle
from media_app.models import MediaFile
from .forms import ProductPostForm, ServicePostForm, LaborPostForm, SocialMediaHandleForm
import logging
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from comment.models import Comment
from .models import Post, Continent, Country, State, Town
from comment.forms import CommentForm
from person.models import Person  # Make sure this is imported
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback

logger = logging.getLogger(__name__)

class CategoryListView(ListView):
    model = Category
    template_name = "posts/category_list.html"
    context_object_name = "categories"

class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        Return approved posts visible to the current user according to the strict scope rules:
          - global -> everyone
          - continent -> match user's continent (only)
          - country -> match user's continent + country (only)
          - state -> match user's continent + country + state (only)
          - town -> match user's continent + country + state + town

        If request GET includes explicit location params (continent/country/state/town),
        treat that as a search override: include global posts + posts that match the provided
        location and the corresponding availability_scope.
        """
        user = self.request.user
        # <-- adjust to 'person' if your profile related_name is user.person -->
        profile = getattr(user, "profile", None)

        # start from approved posts only
        qs = Post.objects.filter(status="approved")

        # If explicit search filters provided, treat as search override (include global)
        continent_q = self.request.GET.get("continent")
        country_q = self.request.GET.get("country")
        state_q = self.request.GET.get("state")
        town_q = self.request.GET.get("town")

        if continent_q or country_q or state_q or town_q:
            filters = Q()
            # Always include global posts in search results
            filters |= Q(availability_scope="global")

            if town_q:
                filters |= Q(availability_scope="town", post_town__name__iexact=town_q)
            if state_q:
                filters |= Q(availability_scope="state", post_state__name__iexact=state_q)
            if country_q:
                filters |= Q(availability_scope="country", post_country__name__iexact=country_q)
            if continent_q:
                filters |= Q(availability_scope="continent", post_continent__name__iexact=continent_q)

            return qs.filter(filters).order_by("-created_at")

        # NEW LOGIC: If profile is not approved, show all approved posts
        if profile and profile.approval_status != "approved":
            return qs.order_by("-created_at")

        # Default feed: enforce strict visibility based on user's profile location
        if profile:
            filters = Q()

            # 1) global always visible
            filters |= Q(availability_scope="global")

            # 2) continent posts — visible if user's continent matches (regardless of other fields)
            if getattr(profile, "continent", None):
                filters |= Q(availability_scope="continent", post_continent=profile.continent)

            # 3) country posts — visible if continent + country match
            if getattr(profile, "country", None) and getattr(profile, "continent", None):
                filters |= Q(
                    availability_scope="country",
                    post_continent=profile.continent,
                    post_country=profile.country,
                )

            # 4) state posts — visible if continent + country + state match
            if getattr(profile, "state", None) and getattr(profile, "country", None) and getattr(profile, "continent", None):
                filters |= Q(
                    availability_scope="state",
                    post_continent=profile.continent,
                    post_country=profile.country,
                    post_state=profile.state,
                )

            # 5) town posts — visible only if all 4 levels match
            if getattr(profile, "town", None) and getattr(profile, "state", None) and getattr(profile, "country", None) and getattr(profile, "continent", None):
                filters |= Q(
                    availability_scope="town",
                    post_continent=profile.continent,
                    post_country=profile.country,
                    post_state=profile.state,
                    post_town=profile.town,
                )

            return qs.filter(filters).order_by("-created_at")

        # User has no profile/location info -> only show global posts
        return qs.order_by("-created_at")

class PostDetailView(DetailView):
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

        # ✅ add the unified variable
        context['post_object'] = self.object

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

        # ✅ add the unified variable
        context['post_object'] = self.object

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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

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
        
        # 🏷️ Category attachment
        form.instance.category = get_object_or_404(Category, name__iexact="Product")

        # 💾 Save the post
        response = super().form_valid(form)

        # 📸 Save uploaded media (images/videos)
        for file in self.request.FILES.getlist("media_files[]"):
            MediaFile.objects.create(
                content_object=self.object,
                file=file,
                file_type="video" if file.content_type.startswith("video") else "image"
            )
            

        # 💬 Save social media handle
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(
            self.request,
            "Product post submitted successfully and is under review!"
        )
        return response

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create posts.")
            return redirect("profile_detail")  # or another appropriate page
        return super().dispatch(request, *args, **kwargs)
class ServicePostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = ServicePostForm
    template_name = 'posts/post_form_service.html'
    success_url = reverse_lazy('post_home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

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
                # 🏷️ Category attachment
        form.instance.category = get_object_or_404(Category, name__iexact="Service")

        # 💾 Save the post
        response = super().form_valid(form)
 
        # 📸 Save uploaded media (images/videos)
        for file in self.request.FILES.getlist("media_files[]"):
            MediaFile.objects.create(
                content_object=self.object,
                file=file,
                file_type="video" if file.content_type.startswith("video") else "image"
            )
            

        # 💬 Save social media handles
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(
            self.request, 
            "Service post submitted successfully and is under review!"
        )
        return response
    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create posts.")
            return redirect("profile_detail")  # or another appropriate page
        return super().dispatch(request, *args, **kwargs)

class LaborPostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = LaborPostForm
    template_name = 'posts/post_form_labor.html'
    success_url = reverse_lazy('post_home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

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
                # 🏷️ Category attachment
        form.instance.category = get_object_or_404(Category, name__iexact="Labor")

        # 💾 Save the post
        response = super().form_valid(form)

        # 📸 Save uploaded media (images/videos)
        for file in self.request.FILES.getlist("media_files[]"):
            MediaFile.objects.create(
                content_object=self.object,
                file=file,
                file_type="video" if file.content_type.startswith("video") else "image"
            )
            

        # 💬 Save social media handle
        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(
            self.request,
            "Labor post submitted successfully and is under review!"
        )
        return response
    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create posts.")
            return redirect("profile_detail")  # or another appropriate page
        return super().dispatch(request, *args, **kwargs)
class PostEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    success_url = reverse_lazy('post_home')

    def test_func(self):
        return self.request.user == self.get_object().author
    def form_valid(self, form):
        # Save the updated post first
        self.object = form.save()

        # 🗑️ Clear out old media (images & videos)
        self.object.media_files.all().delete()

        # 📸 Save uploaded media (images/videos)
        for file in self.request.FILES.getlist("media_files[]"):
            MediaFile.objects.create(
                content_object=self.object,
                file=file,
                file_type="video" if file.content_type.startswith("video") else "image"
            )
            

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

        # ✅ add the unified variable
        context['post_object'] = self.object
                
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace media only if new ones were uploaded
        new_files = self.request.FILES.getlist("media_files[]")
        if new_files:
            self.object.media_files.all().delete()
            for file in new_files:
                MediaFile.objects.create(
                    content_object=self.object,
                    file=file,
                    file_type="video" if file.content_type.startswith("video") else "image"
                )
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

        # ✅ add the unified variable
        context['post_object'] = self.object
                
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace media only if new ones were uploaded
        new_files = self.request.FILES.getlist("media_files[]")
        if new_files:
            self.object.media_files.all().delete()
            for file in new_files:
                MediaFile.objects.create(
                    content_object=self.object,
                    file=file,
                    file_type="video" if file.content_type.startswith("video") else "image"
                )
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

        # ✅ add the unified variable
        context['post_object'] = self.object
                
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SocialMediaHandleForm(self.request.POST, instance=self.object.social_handles)
        if social_form.is_valid():
            social_form.save()

        # 🔁 Replace media only if new ones were uploaded
        new_files = self.request.FILES.getlist("media_files[]")
        if new_files:
            self.object.media_files.all().delete()
            for file in new_files:
                MediaFile.objects.create(
                    content_object=self.object,
                    file=file,
                    file_type="video" if file.content_type.startswith("video") else "image"
                )
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

# ----------------------------
# Location API Endpoints
# ----------------------------
@require_GET
def continents_api(request):
    from custom_search.models import Continent
    continents = Continent.objects.all().order_by("name")

    # Include Unspecified (id=0) first if it exists
    unspecified = Continent.objects.filter(id=0)
    continents = (unspecified | continents).distinct()

    data = [{"id": c.id, "name": c.name} for c in continents]
    return JsonResponse(data, safe=False)


@require_GET
def countries_api(request):
    from custom_search.models import Country
    continent_id = request.GET.get("continent_id")

    countries = Country.objects.none()
    if continent_id:
        countries = Country.objects.filter(continent_id=continent_id)

    unspecified = Country.objects.filter(id=0)
    countries = (unspecified | countries).distinct().order_by("name")

    data = [{"id": c.id, "name": c.name} for c in countries]
    return JsonResponse(data, safe=False)


@require_GET
def states_api(request):
    from custom_search.models import State
    country_id = request.GET.get("country_id")

    states = State.objects.none()
    if country_id:
        states = State.objects.filter(country_id=country_id)

    unspecified = State.objects.filter(id=0)
    states = (unspecified | states).distinct().order_by("name")

    data = [{"id": s.id, "name": s.name} for s in states]
    return JsonResponse(data, safe=False)


@require_GET
def towns_api(request):
    from custom_search.models import Town
    state_id = request.GET.get("state_id")

    towns = Town.objects.none()
    if state_id:
        towns = Town.objects.filter(state_id=state_id)

    unspecified = Town.objects.filter(id=0)
    towns = (unspecified | towns).distinct().order_by("name")

    data = [{"id": t.id, "name": t.name} for t in towns]
    return JsonResponse(data, safe=False)

