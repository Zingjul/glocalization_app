from django.db.models import Q
from seekers.models import SeekerPost

def search_seeker_posts(params):
    """
    Search utility for SeekerPosts.
    params: request.GET or dict with q, category, continent, country, state, town
    """
    query = params.get("q", "").strip()
    category = params.get("category")
    continent = params.get("continent")
    country = params.get("country")
    state = params.get("state")
    town = params.get("town")

    seeker_posts = SeekerPost.objects.all()

    # ✅ keyword search
    if query:
        keywords = query.split()
        q_objects = Q()
        for word in keywords:
            q_objects |= (
                Q(business_name__icontains=word) |
                Q(title__icontains=word) |
                Q(description__icontains=word) |
                Q(author_phone_number__icontains=word) |
                Q(author_email__icontains=word)
            )
        seeker_posts = seeker_posts.filter(q_objects)

    # ✅ filters
    if category:
        seeker_posts = seeker_posts.filter(category_id=category)
    if continent:
        seeker_posts = seeker_posts.filter(post_continent_id=continent)
    if country:
        seeker_posts = seeker_posts.filter(post_country_id=country)
    if state:
        seeker_posts = seeker_posts.filter(post_state_id=state)
    if town:
        seeker_posts = seeker_posts.filter(post_town_id=town)

    return seeker_posts
