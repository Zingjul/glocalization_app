from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.views import View
import logging
from media_app.models import MediaFile
from .models import (
    SeekerPost,
    SeekerCategory,
    SeekerSocialMediaHandle,
)
from .forms import (
    ProductSeekerForm,
    ServiceSeekerForm,
    LaborSeekerForm,
    SeekerSocialMediaHandleForm,
)
from custom_search.models import (
    Continent as SeekerContinent,
    Country as SeekerCountry,
    State as SeekerState,
    Town as SeekerTown,
)
from comment.models import Comment
from comment.forms import CommentForm
from person.models import Person  # assumes same as posts app
from seekers.utils.location_assignment import assign_location_fields
from seekers.utils.location_scope_guard import apply_location_scope_fallback

logger = logging.getLogger(__name__)

class SeekerCommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(SeekerPost, pk=pk)
        content_type = ContentType.objects.get_for_model(post)
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.content_type = content_type
            comment.object_id = post.id
            parent_id = request.POST.get("parent_id")
            if parent_id:
                comment.parent_id = parent_id
            comment.save()
            messages.success(request, "Your comment was added successfully.")
        else:
            messages.error(request, "There was a problem with your comment.")

        return redirect(post.get_absolute_url())

class SeekerCategoryListView(ListView):
    model = SeekerCategory
    template_name = "seekers/category_list.html"
    context_object_name = "categories"

class SeekerPostListView(LoginRequiredMixin, ListView):
    model = SeekerPost
    template_name = "seekers/seeker_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        """
        Return approved seeker posts visible to the current user according to strict scope rules:
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
        profile = getattr(user, "profile", None)

        qs = SeekerPost.objects.filter(status="approved")

        # --- 1️⃣ If profile exists but not approved → show ALL approved posts ---
        if profile and getattr(profile, "approval_status", None) != "approved":
            return qs.order_by("-created_at")

        # NEW LOGIC: If profile is not approved, show all approved posts
        if profile and profile.approval_status != "approved":
            return qs.order_by("-created_at")

        # --- Search override: use GET params if present ---
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

        # --- Default feed: filter by user's profile location ---
        if profile:
            filters = Q()

            # 1) global always visible
            filters |= Q(availability_scope="global")

            # 2) continent scope
            if getattr(profile, "continent", None):
                filters |= Q(availability_scope="continent", post_continent=profile.continent)

            # 3) country scope
            if getattr(profile, "continent", None) and getattr(profile, "country", None):
                filters |= Q(
                    availability_scope="country",
                    post_continent=profile.continent,
                    post_country=profile.country,
                )

            # 4) state scope
            if getattr(profile, "continent", None) and getattr(profile, "country", None) and getattr(profile, "state", None):
                filters |= Q(
                    availability_scope="state",
                    post_continent=profile.continent,
                    post_country=profile.country,
                    post_state=profile.state,
                )

            # 5) town scope
            if getattr(profile, "continent", None) and getattr(profile, "country", None) and getattr(profile, "state", None) and getattr(profile, "town", None):
                filters |= Q(
                    availability_scope="town",
                    post_continent=profile.continent,
                    post_country=profile.country,
                    post_state=profile.state,
                    post_town=profile.town,
                )

        # --- Fallback: user has no profile/location info -> only global posts ---
        return qs.order_by("-created_at")

class SeekerPostDetailView(LoginRequiredMixin, DetailView):
    model = SeekerPost
    template_name = "seekers/seeker_detail.html"
    context_object_name = "seekerpost"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # ✅ Get comments for this seeker post
        content_type = ContentType.objects.get_for_model(post)
        comments = (
            Comment.objects.filter(
                content_type=content_type,
                object_id=post.id,
                parent__isnull=True
            )
            .select_related("author", "parent")
            .prefetch_related("replies", "replies__author", "replies__parent")
            .order_by("-created_at")
        )

        # ✅ Pass context required by comment templates
        context.update({
            "comments": comments,
            "comment_form": CommentForm(),
            "target_object": post,
            "app_label": post._meta.app_label,      # "seekers"
            "model_name": post._meta.model_name,    # "seekerpost"
        })
        # ✅ add the unified variable
        context['post_object'] = self.object
        
        return context

class SeekerPostCreateView(LoginRequiredMixin, TemplateView):
    model = SeekerPost
    template_name = "seekers/seeker_create.html"


class SeekerPostUpdateView(LoginRequiredMixin, UpdateView):
    model = SeekerPost

    def get_form_class(self):
        category = self.object.category.name.lower()
        if category == "product":
            return ProductSeekerForm
        elif category == "service":
            return ServiceSeekerForm
        elif category == "labor":
            return LaborSeekerForm

    def get_template_names(self):
        category = self.object.category.name.lower()
        if category == "product":
            return ["seekers/seeker_edit_product.html"]
        elif category == "service":
            return ["seekers/seeker_edit_service.html"]
        elif category == "labor":
            return ["seekers/seeker_edit_labor.html"]
        return ["seekers/post_edit_generic.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        social_form = SeekerSocialMediaHandleForm(instance=getattr(post, "social_handles", None))
        context["social_form"] = social_form
        context["post"] = post

        # ✅ add the unified variable
        context['post_object'] = self.object

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        social_form = SeekerSocialMediaHandleForm(request.POST, instance=getattr(self.object, "social_handles", None))
        if form.is_valid() and social_form.is_valid():
            self.object = form.save()
            social_handle = social_form.save(commit=False)
            social_handle.post = self.object
            social_handle.save()
            messages.success(self.request, "Seeker post updated successfully.")
            return redirect(self.object.get_absolute_url())
        else:
            return self.render_to_response(
                self.get_context_data(form=form, social_form=social_form)
            )

class SeekerPostDeleteView(LoginRequiredMixin, DeleteView):
    model = SeekerPost
    template_name = 'seekers/seeker_confirm_delete.html'
    success_url = reverse_lazy('seekers:seeker_list')

class SeekerProductPostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ProductSeekerForm
    template_name = 'seekers/seeker_create_product.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and not form.instance.business_name:
            form.instance.business_name = profile.business_name
        
        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Product")

        # 💾 Save the post itself first
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

        messages.success(self.request, "Product seeker post submitted successfully and is under review!")
        return response

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create seeker posts.")
            return redirect("profile_detail")  # Or another info page
        return super().dispatch(request, *args, **kwargs)

class SeekerServicePostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ServiceSeekerForm
    template_name = 'seekers/seeker_create_service.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and not form.instance.business_name:
            form.instance.business_name = profile.business_name
        
        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Service")

        # 💾 Save the post itself first
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

        messages.success(self.request, "Service seeker post submitted successfully and is under review!")
        return response

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create seeker posts.")
            return redirect("profile_detail")  # Or another info page
        return super().dispatch(request, *args, **kwargs)

class SeekerLaborPostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = LaborSeekerForm
    template_name = 'seekers/seeker_create_labor.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user   # ✅ Pass user into form
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )

        # ✅ add the unified variable
        context['post_object'] = self.object

        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and not form.instance.business_name:
            form.instance.business_name = profile.business_name
        
        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Labor")

        # 💾 Save the post itself first
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

        messages.success(self.request, "Labor seeker post submitted successfully and is under review!")
        return response

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not profile or profile.approval_status != "approved":
            messages.error(request, "Your profile must be approved before you can create seeker posts.")
            return redirect("profile_detail")  # Or another info page
        return super().dispatch(request, *args, **kwargs)

class SeekerPostEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SeekerPost
    success_url = reverse_lazy('seekers:seeker_list')

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        self.object = form.save()

        # Delete existing media files
        self.object.media_files.all().delete()

        # Save new uploaded files (images/videos)
        for file in self.request.FILES.getlist("media_files[]"):
            MediaFile.objects.create(
                content_object=self.object,
                file=file,
                file_type="video" if file.content_type.startswith("video") else "image"
            )

        return super().form_valid(form)


class SeekerPostEditProductView(SeekerPostEditBaseView):
    model = SeekerPost
    form_class = ProductSeekerForm
    template_name = 'seekers/seeker_edit_product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        else:
            context['social_form'] = SeekerSocialMediaHandleForm(instance=self.object.seeker_social_handles)

        # ✅ add the unified variable
        context['post_object'] = self.object
        
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
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

class SeekerPostEditServiceView(SeekerPostEditBaseView):
    model = SeekerPost
    form_class = ServiceSeekerForm
    template_name = 'seekers/seeker_edit_service.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        else:
            context['social_form'] = SeekerSocialMediaHandleForm(instance=self.object.seeker_social_handles)

        # ✅ add the unified variable
        context['post_object'] = self.object
        
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
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

class SeekerPostEditLaborView(SeekerPostEditBaseView):
    model = SeekerPost
    form_class = LaborSeekerForm
    template_name = 'seekers/seeker_edit_labor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['social_form'] = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        else:
            context['social_form'] = SeekerSocialMediaHandleForm(instance=self.object.seeker_social_handles)

        # ✅ add the unified variable
        context['post_object'] = self.object
        
        return context

    def form_valid(self, form):
        self.object = form.save()

        # ✅ Save social media form
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
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

class SeekerPendingPostsByUserView(LoginRequiredMixin, ListView):
    model = SeekerPost
    template_name = "seekers/pending_posts_by_user.html"
    context_object_name = "pending_posts"

    def get_queryset(self):
        return SeekerPost.objects.filter(
            author=self.request.user,   # ✅ use author, not profile
            status="pending"
        ).order_by("-id")


def get_seeker_posts_visible_to_user(user):
    location = getattr(user, "profile", None)
    if not location:
        return SeekerPost.objects.none()
    return SeekerPost.objects.filter(
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
    visible_posts = get_seeker_posts_visible_to_user(request.user)
    return render(request, 'seekers/seeker_list.html', {'posts': visible_posts})

@require_GET
def seeker_location_autocomplete(request):
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
