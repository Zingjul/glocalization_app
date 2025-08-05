from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from .models import SeekerPost, SeekerImage, SeekerResponse
from .forms import ProductSeekerForm, ServiceSeekerForm, LaborSeekerForm
from custom_search.models import Continent, Country, State, Town
from comment.models import Comment
from comment.forms import CommentForm
from person.models import Person  # Make sure this is imported
import logging
from django.views import View
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback

logger = logging.getLogger(__name__)


class SeekerPostListView(LoginRequiredMixin, ListView):
    model = SeekerPost
    template_name = "seekers/seeker_list.html"
    context_object_name = "posts"

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'person', None)
        queryset = SeekerPost.objects.filter(is_fulfilled=False)

        continent = self.request.GET.get('continent')
        country = self.request.GET.get('country')
        state = self.request.GET.get('state')
        town = self.request.GET.get('town')
        keyword = self.request.GET.get('q', "").strip()

        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword)
            )

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

class SeekerPostCreateView(LoginRequiredMixin, TemplateView):
    model= SeekerPost
    template_name = "seekers/seeker_create.html"

class SeekerPostDetailView(LoginRequiredMixin, DetailView):
    model = SeekerPost
    template_name = "seekers/seeker_detail.html"
    context_object_name = "post"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        content_type = ContentType.objects.get_for_model(post)

        comments = Comment.objects.filter(
            content_type=content_type,
            object_id=post.id,
            parent__isnull=True
        ).select_related("author", "parent").prefetch_related(
            "replies",
            "replies__author",
            "replies__parent"
        ).order_by("-created_at")

        context.update({
            "comments": comments,
            "comment_form": CommentForm(),
        })

        return context

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ProductSeekerForm
    template_name = 'seekers/seeker_create_product.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def form_valid(self, form):
        user = self.request.user  # ✅ Define user safely before using
        form.instance.author = user
        form.instance.request_type = "product"

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # 🧭 Availability scope detection
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(seeker_post=self.object, image=image)

        messages.success(self.request, "Product request submitted successfully!")
        return response

class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = ServiceSeekerForm
    template_name = 'seekers/seeker_create_service.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def form_valid(self, form):
        user = self.request.user  # ✅ Define user before accessing profile
        form.instance.author = user
        form.instance.request_type = "service"

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # 🧭 Scope detection logic
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(seeker_post=self.object, image=image)

        messages.success(self.request, "Service request submitted successfully!")
        return response

class LaborCreateView(LoginRequiredMixin, CreateView):
    model = SeekerPost
    form_class = LaborSeekerForm
    template_name = 'seekers/seeker_create_labor.html'
    success_url = reverse_lazy('seekers:seeker_list')

    def form_valid(self, form):
        user = self.request.user  # ✅ Securely define user
        form.instance.author = user
        form.instance.request_type = "labor"

        # ⛓️ Inject business_name from Person profile
        profile = getattr(user, 'profile', None)
        if profile and profile.business_name:
            form.instance.business_name = profile.business_name

        # 🧭 Scope detection logic
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        # explicitly making sure location fields are saved based on user input 
        assign_location_fields(form)

        response = super().form_valid(form)

        # 📸 Save uploaded images
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(seeker_post=self.object, image=image)

        messages.success(self.request, "Labor request submitted successfully!")
        return response

class SeekerEditBaseView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SeekerPost
    success_url = reverse_lazy('seekers:seeker_list')

    def test_func(self):
        return self.request.user == self.get_object().author

    def form_valid(self, form):
        self.object = form.save()

        # 🗑️ Clear previous images
        self.object.images.all().delete()

        # ✅ Save new images if any
        for i in range(1, 7):
            image = self.request.FILES.get(f'image{i}')
            if image:
                SeekerImage.objects.create(seeker_post=self.object, image=image)

        return super().form_valid(form)


class SeekerEditProductView(SeekerEditBaseView):
    form_class = ProductSeekerForm
    template_name = 'seekers/seeker_edit_product.html'


class SeekerEditServiceView(SeekerEditBaseView):
    form_class = ServiceSeekerForm
    template_name = 'seekers/seeker_edit_service.html'


class SeekerEditLaborView(SeekerEditBaseView):
    form_class = LaborSeekerForm
    template_name = 'seekers/seeker_edit_labor.html'

# seekers/views.py

class SeekerPostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = SeekerPost
    template_name = "seekers/seeker_edit.html"  # Generic template (or override per type)
    success_url = reverse_lazy("seekers:seeker_list")

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_form_class(self):
        seeker_type = self.get_object().request_type
        if seeker_type == "product":
            return ProductSeekerForm
        elif seeker_type == "service":
            return ServiceSeekerForm
        elif seeker_type == "labor":
            return LaborSeekerForm
        return ProductSeekerForm  # Fallback

    def get_template_names(self):
        seeker_type = self.get_object().request_type
        if seeker_type == "product":
            return ["seekers/seeker_edit_product.html"]
        elif seeker_type == "service":
            return ["seekers/seeker_edit_service.html"]
        elif seeker_type == "labor":
            return ["seekers/seeker_edit_labor.html"]
        return ["seekers/seeker_edit.html"]

    def form_valid(self, form):
        self.object = form.save()

        # 🔄 Recalculate availability scope based on location inputs
        if form.instance.post_town:
            form.instance.availability_scope = "town"
        elif form.instance.post_state:
            form.instance.availability_scope = "state"
        elif form.instance.post_country:
            form.instance.availability_scope = "country"
        elif form.instance.post_continent:
            form.instance.availability_scope = "continent"

        form.save()

        # 🗑️ Remove old images
        self.object.images.all().delete()

        # ✅ Add new ones
        for i in range(1, 7):
            image = self.request.FILES.get(f"image{i}")
            if image:
                SeekerImage.objects.create(seeker_post=self.object, image=image)

        messages.success(self.request, "Your seeker post was successfully updated.")
        return super().form_valid(form)

class PendingSeekersByUserView(LoginRequiredMixin, ListView):
    model = SeekerPost
    template_name = "seekers/pending_seekers_by_user.html"
    context_object_name = "pending_posts"

    def get_queryset(self):
        return SeekerPost.objects.filter(author=self.request.user, is_fulfilled=False).order_by('-created_at')


def get_seeker_visible_to_user(user):
    location = user.profile
    logger.info(f"User Town: {location.town} ({location.town.name})")

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


def seeker_home(request):
    visible_posts = get_seeker_visible_to_user(request.user)
    return render(request, 'seekers/seeker_list.html', {'posts': visible_posts})

class SeekerRespondView(LoginRequiredMixin, View):
    def post(self, request, pk):
        seeker_post = get_object_or_404(SeekerPost, pk=pk)

        # Prevent duplicate responses (optional safeguard)
        already_sent = SeekerResponse.objects.filter(
            seeker_post=seeker_post,
            sender=request.user
        ).exists()

        if already_sent:
            messages.info(request, "You’ve already responded to this post.")
        else:
            SeekerResponse.objects.create(
                seeker_post=seeker_post,
                sender=request.user,
                receiver=seeker_post.author
            )
            messages.success(request, "Your contact info has been sent to the post owner.")

        return redirect(seeker_post.get_absolute_url())


class SeekerPostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = SeekerPost
    template_name = "seekers/seeker_confirm_delete.html"
    success_url = reverse_lazy("seekers:seeker_list")

    def test_func(self):
        return self.request.user == self.get_object().author

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Your seeker post has been deleted.")
        return super().delete(request, *args, **kwargs)

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
