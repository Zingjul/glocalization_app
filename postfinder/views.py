from django.shortcuts import render
from .search_utils import search_posts
from posts.models import Category

def postfinder_view(request):
    results = search_posts(request.GET)
    return render(request, "postfinder/results.html", {
        "results": results,
        "query": request.GET.get("q", ""),
        "categories": Category.objects.all(),
    })


# from django.shortcuts import render
# from django.db.models import Q
# from posts.models import Post
# from custom_search.forms import CustomSearchForm
# from custom_search.models import Continent, Country, State, Town

# def filter_posts(request):
#     form = CustomSearchForm(request.GET or None)
#     posts = Post.objects.none()

#     scope = request.GET.get("scope", "global").lower().strip()

#     # Preload inputs
#     selected_continent = selected_country = selected_state = selected_town = None
#     typed_continent = typed_country = typed_state = typed_town = ""
#     keyword = ""

#     if form.is_valid():
#         selected_continent = form.cleaned_data.get("continent")
#         selected_country = form.cleaned_data.get("country")
#         selected_state = form.cleaned_data.get("state")
#         selected_town = form.cleaned_data.get("town")
#         keyword = form.cleaned_data.get("query", "").strip()

#     typed_continent = request.GET.get("continent_text", "").strip()
#     typed_country = request.GET.get("country_text", "").strip()
#     typed_state = request.GET.get("state_text", "").strip()
#     typed_town = request.GET.get("town_text", "").strip()

#     if scope == "global":
#         posts = Post.objects.all()

#         if keyword:
#             posts = posts.filter(
#                 Q(product_name__icontains=keyword) |
#                 Q(description__icontains=keyword) |
#                 Q(business_name__icontains=keyword)
#             )
#         else:
#             posts = Post.objects.none()
#     elif scope == "continent":
#         continent_obj = selected_continent or Continent.objects.filter(name__iexact=typed_continent).first()
#         if continent_obj:
#             countries = Country.objects.filter(continent=continent_obj)
#             states = State.objects.filter(country__in=countries)
#             towns = Town.objects.filter(state__in=states)

#             posts = Post.objects.filter(
#                 Q(availability_scope="continent", post_continent_input__iexact=continent_obj.name) |
#                 Q(availability_scope="country", post_country_input__in=[c.name for c in countries]) |
#                 Q(availability_scope="state", post_state_input__in=[s.name for s in states]) |
#                 Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
#             )
#         else:
#             posts = Post.objects.none()

#     elif scope == "country":
#         country_obj = selected_country or Country.objects.filter(name__iexact=typed_country).first()
#         if country_obj:
#             states = State.objects.filter(country=country_obj)
#             towns = Town.objects.filter(state__in=states)

#             posts = Post.objects.filter(
#                 Q(availability_scope="country", post_country_input__iexact=country_obj.name) |
#                 Q(availability_scope="state", post_state_input__in=[s.name for s in states]) |
#                 Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
#             )
#         else:
#             posts = Post.objects.none()

#     elif scope == "state":
#         state_obj = selected_state or State.objects.filter(name__iexact=typed_state).first()
#         if state_obj:
#             towns = Town.objects.filter(state=state_obj)

#             posts = Post.objects.filter(
#                 Q(availability_scope="state", post_state_input__iexact=state_obj.name) |
#                 Q(availability_scope="town", post_town_input__in=[t.name for t in towns])
#             )
#         else:
#             posts = Post.objects.none()

#     elif scope == "town":
#         town_obj = selected_town or Town.objects.filter(name__iexact=typed_town).first()
#         if town_obj:
#             posts = Post.objects.filter(
#                 Q(availability_scope="town", post_town_input__iexact=town_obj.name) |
#                 Q(availability_scope="state", post_state_input__iexact=town_obj.state.name) |
#                 Q(availability_scope="country", post_country_input__iexact=town_obj.state.country.name)
#             )
#         else:
#             posts = Post.objects.none()

#     # 🧠 Apply keyword filter
#     if keyword:
#         posts = posts.filter(
#             Q(product_name__icontains=keyword) |
#             Q(description__icontains=keyword) |
#             Q(business_name__icontains=keyword)
#         )

#     # 📍 Construct search path for user feedback
#     search_path = []
#     if scope in ["continent", "country", "state", "town"]:
#         continent_obj = selected_continent or Continent.objects.filter(name__iexact=typed_continent).first()
#         if continent_obj:
#             search_path.append(continent_obj.name)
#     if scope in ["country", "state", "town"]:
#         country_obj = selected_country or Country.objects.filter(name__iexact=typed_country).first()
#         if country_obj:
#             search_path.append(country_obj.name)
#     if scope in ["state", "town"]:
#         state_obj = selected_state or State.objects.filter(name__iexact=typed_state).first()
#         if state_obj:
#             search_path.append(state_obj.name)
#     if scope == "town":
#         town_obj = selected_town or Town.objects.filter(name__iexact=typed_town).first()
#         if town_obj:
#             search_path.append(town_obj.name)

#     return render(request, "postfinder/search_filters.html", {
#         "form": form,
#         "posts": posts,
#         "search_path": search_path
#     })
