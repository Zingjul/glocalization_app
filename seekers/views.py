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

from .models import (
    SeekerPost,
    SeekerCategory,
    SeekerSocialMediaHandle,
    SeekerImage,  # ✅ correct model name
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
        user = self.request.user
        profile = getattr(user, 'person', None)
        queryset = SeekerPost.objects.filter(status='approved')

        continent = self.request.GET.get('continent')
        country = self.request.GET.get('country')
        state = self.request.GET.get('state')
        town = self.request.GET.get('town')

        if continent or country or state or town:
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

        return queryset.order_by('-created_at')


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

# def seeker_home(request):
#     visible_posts = get_seeker_posts_visible_to_user(request.user)
#     return render(request, 'seekers/seeker_list.html', {'posts': visible_posts})


class SeekerProductPostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ProductSeekerForm
    template_name = 'seekers/seeker_create_product.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )
        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Product")

        response = super().form_valid(form)

        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(post=self.object, image=image)

        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Product seeker post submitted successfully and is under review!")
        return response


class SeekerServicePostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ServiceSeekerForm
    template_name = 'seekers/seeker_create_service.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )
        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Service")

        response = super().form_valid(form)

        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(post=self.object, image=image)

        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Service seeker post submitted successfully and is under review!")
        return response


class SeekerLaborPostCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = LaborSeekerForm
    template_name = 'seekers/seeker_create_labor.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['social_form'] = SeekerSocialMediaHandleForm(
            self.request.POST or None,
            self.request.FILES or None
        )
        return context

    def form_valid(self, form):
        user = self.request.user
        social_form = SeekerSocialMediaHandleForm(self.request.POST, self.request.FILES)

        if not social_form.is_valid():
            return self.form_invalid(form)

        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        form.instance.author = user
        form.instance.status = "pending"
        form.instance.category = get_object_or_404(SeekerCategory, name__iexact="Labor")

        response = super().form_valid(form)

        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(post=self.object, image=image)

        social_handle = social_form.save(commit=False)
        social_handle.post = self.object
        social_handle.save()

        messages.success(self.request, "Labor seeker post submitted successfully and is under review!")
        return response


class SeekerPostEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SeekerPost
    success_url = reverse_lazy('seekers:seeker_list')

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        self.object = form.save()
        self.object.seeker_images.all().delete()

        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(post=self.object, image=image)

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
        return context

    def form_valid(self, form):
        self.object = form.save()
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        if social_form.is_valid():
            social_form.save()

        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.seeker_images.all().delete()
            for image in new_images:
                if image:
                    SeekerImage.objects.create(post=self.object, image=image)

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
        return context

    def form_valid(self, form):
        self.object = form.save()
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        if social_form.is_valid():
            social_form.save()

        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.seeker_images.all().delete()
            for image in new_images:
                if image:
                    SeekerImage.objects.create(post=self.object, image=image)

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
        return context

    def form_valid(self, form):
        self.object = form.save()
        social_form = SeekerSocialMediaHandleForm(self.request.POST, instance=self.object.seeker_social_handles)
        if social_form.is_valid():
            social_form.save()

        new_images = [self.request.FILES.get(f'image{i}') for i in range(1, 7)]
        if any(new_images):
            self.object.seeker_images.all().delete()
            for image in new_images:
                if image:
                    SeekerImage.objects.create(post=self.object, image=image)

        return super().form_valid(form)


class SeekerPendingPostsByUserView(LoginRequiredMixin, ListView):
    model = SeekerPost
    template_name = "seekers/pending_posts_by_user.html"
    context_object_name = "pending_posts"

    def get_queryset(self):
        return SeekerPost.objects.filter(author=self.request.user, status='pending').order_by('-created_at')


def get_seeker_posts_visible_to_user(user):
    location = user.profile
    logger.info(f"User Town: {location.town} ({location.town.name})")

    return SeekerPost.objects.filter(
        Q(availability_scope='global') |
        (Q(availability_scope='continent') & (Q(post_continent=location.continent) | Q(post_continent_input__iexact=location.continent.name))) |
        (Q(availability_scope='country') & (Q(post_country=location.country) | Q(post_country_input__iexact=location.country.name))) |
        (Q(availability_scope='state') & (Q(post_state=location.state) | Q(post_state_input__iexact=location.state.name))) |
        (Q(availability_scope='town') & (Q(post_town=location.town) | Q(post_town_input__iexact=location.town.name)))
    ).distinct()


@require_GET
def seeker_location_autocomplete(request):
    location_type = request.GET.get("type", "").lower()
    query = request.GET.get("q", "")

    model_map = {
        "continent": SeekerContinent,
        "country": SeekerCountry,
        "state": SeekerState,
        "town": SeekerTown,
    }

    model = model_map.get(location_type)
    if not model:
        return JsonResponse({"results": []})

    results = model.objects.filter(name__icontains=query).values_list("name", flat=True)[:10]
    return JsonResponse({"results": list(results)})
