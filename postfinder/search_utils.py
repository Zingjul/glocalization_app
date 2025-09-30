from django.db.models import Q
from posts.models import Post  # we’re searching posts here

def search_posts(params):
    """
    Search utility for Posts.
    params: request.GET or dict with q, category, continent, country, state, town
    """
    query = params.get("q", "").strip()
    category = params.get("category")
    continent = params.get("continent")
    country = params.get("country")
    state = params.get("state")
    town = params.get("town")

    posts = Post.objects.all()

    # ✅ keyword search
    if query:
        keywords = query.split()
        q_objects = Q()
        for word in keywords:
            q_objects |= (
                Q(product_name__icontains=word) |
                Q(description__icontains=word) |
                Q(author_phone_number__icontains=word) |
                Q(author_email__icontains=word) |
                Q(business_name__icontains=word) |
                Q(service_details__icontains=word) |
                Q(brand__icontains=word) 
            )
        posts = posts.filter(q_objects)

    # ✅ filters
    if category:
        posts = posts.filter(category_id=category)
    if continent:
        posts = posts.filter(post_continent_id=continent)
    if country:
        posts = posts.filter(post_country_id=country)
    if state:
        posts = posts.filter(post_state_id=state)
    if town:
        posts = posts.filter(post_town_id=town)

    return posts
