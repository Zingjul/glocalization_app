from django.shortcuts import render
from posts.models import Post, Category
from posts.forms import ProductPostForm
from .search_utils import search_posts, build_keyword_filter  # make sure this is the updated one

def postfinder_view(request):
    # ✅ bind the form with GET params so dropdown selections persist
    form = ProductPostForm(request.GET or None)

    # ✅ fetch filtered posts
    results = search_posts(request.GET)

    # Optionally filter results by keyword if 'query' is present
    query = request.GET.get("q", "")
    if query:
        q = build_keyword_filter(query)
        results = results.filter(q)

    return render(request, "postfinder/results.html", {
        "form": form,
        "results": results,
        "query": query,
        "categories": Category.objects.all(),
    })