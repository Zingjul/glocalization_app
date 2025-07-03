from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import SeekerPost, SeekerImage
from .forms import SeekerPostForm, SeekerImageFormSet
from custom_search.forms import CustomSearchForm
from custom_search.models import Continent, Country, State, Town
from comment.forms import CommentForm
from comment.models import Comment
from django.contrib.contenttypes.models import ContentType

# 🔎 Seeker post search with filtering (by scope + keyword)
def filter_seeker_posts(request):
    form = CustomSearchForm(request.GET or None)
    posts = SeekerPost.objects.none()
    scope = request.GET.get("scope", "global").lower().strip()
    keyword = ""
    selected_continent = selected_country = selected_state = selected_town = None
    typed_continent = typed_country = typed_state = typed_town = ""

    if form.is_valid():
        selected_continent = form.cleaned_data.get("continent")
        selected_country = form.cleaned_data.get("country")
        selected_state = form.cleaned_data.get("state")
        selected_town = form.cleaned_data.get("town")
        keyword = form.cleaned_data.get("query", "").strip()

    typed_continent = request.GET.get("continent_text", "").strip()
    typed_country = request.GET.get("country_text", "").strip()
    typed_state = request.GET.get("state_text", "").strip()
    typed_town = request.GET.get("town_text", "").strip()

    if scope == "global":
        posts = SeekerPost.objects.all()
        if keyword:
            posts = posts.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        else:
            posts = SeekerPost.objects.none()

    elif scope == "continent":
        continent_obj = selected_continent or Continent.objects.filter(name__iexact=typed_continent).first()
        if continent_obj:
            countries = Country.objects.filter(continent=continent_obj)
            states = State.objects.filter(country__in=countries)
            towns = Town.objects.filter(state__in=states)

            posts = SeekerPost.objects.filter(
                Q(availability_scope="continent", post_continent_input__iexact=continent_obj.name) |
                Q(availability_scope="country", post_country_input__in=[c.name for c in countries]) |
                Q(availability_scope="state", post_state_input__in=[s.name for s in states]) |
                Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
            )
        else:
            posts = SeekerPost.objects.none()

    elif scope == "country":
        country_obj = selected_country or Country.objects.filter(name__iexact=typed_country).first()
        if country_obj:
            states = State.objects.filter(country=country_obj)
            towns = Town.objects.filter(state__in=states)

            posts = SeekerPost.objects.filter(
                Q(availability_scope="country", post_country_input__iexact=country_obj.name) |
                Q(availability_scope="state", post_state_input__in=[s.name for s in states]) |
                Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
            )
        else:
            posts = SeekerPost.objects.none()

    elif scope == "state":
        state_obj = selected_state or State.objects.filter(name__iexact=typed_state).first()
        if state_obj:
            towns = Town.objects.filter(state=state_obj)

            posts = SeekerPost.objects.filter(
                Q(availability_scope="state", post_state_input__iexact=state_obj.name) |
                Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
            )
        else:
            posts = SeekerPost.objects.none()

    elif scope == "town":
        town_obj = selected_town or Town.objects.filter(name__iexact=typed_town).first()
        if town_obj:
            posts = SeekerPost.objects.filter(
                Q(availability_scope="town", post_town_input__iexact=town_obj.name) |
                Q(availability_scope="state", post_state_input__iexact=town_obj.state.name) |
                Q(availability_scope="country", post_country_input__iexact=town_obj.state.country.name)
            )
        else:
            posts = SeekerPost.objects.none()

    # Apply keyword filter again (across all scopes)
    if keyword:
        posts = posts.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    # Construct search path
    search_path = []
    if scope in ["continent", "country", "state", "town"]:
        continent_obj = selected_continent or Continent.objects.filter(name__iexact=typed_continent).first()
        if continent_obj:
            search_path.append(continent_obj.name)
    if scope in ["country", "state", "town"]:
        country_obj = selected_country or Country.objects.filter(name__iexact=typed_country).first()
        if country_obj:
            search_path.append(country_obj.name)
    if scope in ["state", "town"]:
        state_obj = selected_state or State.objects.filter(name__iexact=typed_state).first()
        if state_obj:
            search_path.append(state_obj.name)
    if scope == "town":
        town_obj = selected_town or Town.objects.filter(name__iexact=typed_town).first()
        if town_obj:
            search_path.append(town_obj.name)

    return render(request, "seekers/seeker_list.html", {
        "form": form,
        "posts": posts,
        "search_path": search_path
    })

# ➕ Create a seeker post (with optional images)
@login_required
def seeker_create(request):
    if request.method == "POST":
        form = SeekerPostForm(request.POST)
        if form.is_valid():
            seeker_post = form.save(commit=False)
            seeker_post.author = request.user
            seeker_post.save()

            # Save up to six uploaded images
            for i in range(1, 7):
                image_file = request.FILES.get(f'image{i}')
                if image_file:
                    SeekerImage.objects.create(seeker_post=seeker_post, image=image_file)

            return redirect("seekers:seeker_detail", pk=seeker_post.pk)
    else:
        form = SeekerPostForm()

    return render(request, "seekers/seeker_create.html", {
        "form": form
    })
def seeker_detail(request, pk):
    post = get_object_or_404(SeekerPost, pk=pk)

    # Grab the content type for this model
    content_type = ContentType.objects.get_for_model(SeekerPost)

    # Fetch top-level comments (exclude replies)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=post.id,
        parent__isnull=True
    )

    # Prepare a fresh form for comment submission
    comment_form = CommentForm()

    return render(request, "seekers/seeker_detail.html", {
        "post": post,
        "comments": comments,
        "comment_form": comment_form,
    })
# 🧭 View all seeker posts (default list)
def seeker_list(request):
    posts = SeekerPost.objects.filter(is_fulfilled=False).order_by("-created_at")

    # Fetch the content type for SeekerPost
    seeker_ct = ContentType.objects.get_for_model(SeekerPost)

    # Build a dictionary of comment counts by post ID
    comment_counts = {
        post.id: Comment.objects.filter(content_type=seeker_ct, object_id=post.id, parent__isnull=True).count()
        for post in posts
    }

    return render(request, "seekers/seeker_list.html", {
        "posts": posts,
        "comment_counts": comment_counts,
    })
# 🙋 Respond to a seeker post (placeholder)
@login_required
def respond_to_seeker(request, pk):
    post = get_object_or_404(SeekerPost, pk=pk)
    # Future: add response form for seller to express interest
    return render(request, "seekers/seeker_respond.html", {"post": post})

@login_required
def create_product_request(request):
    return _create_seeker_post(request, post_type='product', template='seekers/seeker_create_product.html')

@login_required
def create_service_request(request):
    return _create_seeker_post(request, post_type='service', template='seekers/seeker_create_service.html')

@login_required
def create_labor_request(request):
    return _create_seeker_post(request, post_type='labor', template='seekers/seeker_create_labor.html')

@login_required
def _create_seeker_post(request, post_type, template):
    from .forms import SeekerPostForm
    if request.method == "POST":
        form = SeekerPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.request_type = post_type
            post.author = request.user
            post.save()

            # Manually handle up to 6 image uploads
            for i in range(1, 7):
                image_file = request.FILES.get(f'image{i}')
                if image_file:
                    SeekerImage.objects.create(seeker_post=post, image=image_file)

            return redirect(post.get_absolute_url())
    else:
        form = SeekerPostForm(initial={'request_type': post_type})
    return render(request, template, {"form": form})

@login_required
def edit_seeker_post(request, pk):
    post = get_object_or_404(SeekerPost, pk=pk)

    if post.author != request.user:
        return redirect("seekers:seeker_detail", pk=pk)  # Or raise 403

    if request.method == "POST":
        form = SeekerPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect("seekers:seeker_detail", pk=pk)
    else:
        form = SeekerPostForm(instance=post)

    return render(request, "seekers/seeker_edit.html", {"form": form, "post": post})

# 🗑️ Delete a seeker post
@login_required
def delete_seeker_post(request, pk):
    post = get_object_or_404(SeekerPost, pk=pk)

    if post.author != request.user:
        return redirect("seekers:seeker_detail", pk=pk)  # Or raise 403

    if request.method == "POST":
        post.delete()
        return redirect("seekers:seeker_list")

    return render(request, "seekers/seeker_confirm_delete.html", {"post": post})
