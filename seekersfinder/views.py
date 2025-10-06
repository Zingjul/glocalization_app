# seekersfinder/views.py
from django.shortcuts import render
from seekers.models import SeekerPost, SeekerCategory
from seekers.forms import BaseSeekerPostForm
from .search_utils import search_seeker_posts, build_keyword_filter  # make sure this is the updated one


def seekersfinder_view(request):
    # ✅ bind the form with GET params so dropdown selections persist
    form = BaseSeekerPostForm(request.GET or None)

    # ✅ fetch filtered seeker posts
    results = search_seeker_posts(request.GET)

    return render(request, "seekersfinder/results.html", {
        "form": form,
        "results": results,
        "query": request.GET.get("q", ""),
        "categories": SeekerCategory.objects.all(),
    })
