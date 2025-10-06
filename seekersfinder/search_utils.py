from django.db.models import Q
from seekers.models import SeekerPost

def normalize(val):
    """Turn '0' or '' into None, keep valid IDs."""
    return val if val and val != "0" else None

# ------------------------------
# Location hierarchy utilities
# ------------------------------

def get_seeker_location_hierarchy(seeker_post):
    """Given a SeekerPost instance, return its location hierarchy as a dict of model instances."""
    return {
        "continent": seeker_post.post_continent,
        "country": seeker_post.post_country,
        "state": seeker_post.post_state,
        "town": seeker_post.post_town,
    }

def get_location_hierarchy_from_params(params):
    """Extract location hierarchy from search params (IDs)."""
    return {
        "continent": normalize(params.get("post_continent") or params.get("continent")),
        "country": normalize(params.get("post_country") or params.get("country")),
        "state": normalize(params.get("post_state") or params.get("state")),
        "town": normalize(
            params.get("post_town")
            or params.get("town")
            or params.get("post_town_input")
        ),
    }

def location_hierarchy_to_dict(hierarchy):
    """Convert location hierarchy with model instances to IDs."""
    return {
        "continent": hierarchy["continent"].id if hierarchy["continent"] else None,
        "country": hierarchy["country"].id if hierarchy["country"] else None,
        "state": hierarchy["state"].id if hierarchy["state"] else None,
        "town": hierarchy["town"].id if hierarchy["town"] else None,
    }

def location_hierarchy_to_names(hierarchy):
    """Convert location hierarchy with model instances to names."""
    return {
        "continent": hierarchy["continent"].name if hierarchy["continent"] else None,
        "country": hierarchy["country"].name if hierarchy["country"] else None,
        "state": hierarchy["state"].name if hierarchy["state"] else None,
        "town": hierarchy["town"].name if hierarchy["town"] else None,
    }

def determine_availability_scope(hierarchy):
    """Determine the deepest level of location specified in the hierarchy."""
    if hierarchy["town"]:
        return "town"
    elif hierarchy["state"]:
        return "state"
    elif hierarchy["country"]:
        return "country"
    elif hierarchy["continent"]:
        return "continent"
    else:
        return None

def extract_unique_location_options(seeker_posts):
    """Extract unique location options from a queryset of seeker posts for filter dropdowns."""
    continents, countries, states, towns = {}, {}, {}, {}

    for seeker_post in seeker_posts:
        if seeker_post.post_continent:
            continents.setdefault(seeker_post.post_continent.id, seeker_post.post_continent)
        if seeker_post.post_country:
            countries.setdefault(seeker_post.post_country.id, seeker_post.post_country)
        if seeker_post.post_state:
            states.setdefault(seeker_post.post_state.id, seeker_post.post_state)
        if seeker_post.post_town:
            towns.setdefault(seeker_post.post_town.id, seeker_post.post_town)

    return {
        "continents": list(continents.values()),
        "countries": list(countries.values()),
        "states": list(states.values()),
        "towns": list(towns.values()),
    }

# ------------------------------
# Search logic
# ------------------------------

def search_seeker_posts(params):
    """
    Search utility for SeekerPosts with hierarchical filtering.
    - availability_scope = how deep the user wants to search
    - seeker's own availability_scope does NOT limit results
    """
    query = params.get("q", "").strip()
    category = normalize(params.get("category"))
    availability_scope = params.get("availability_scope")

    # normalize hierarchy from params
    continent = normalize(params.get("continent") or params.get("post_continent"))
    country   = normalize(params.get("country")   or params.get("post_country"))
    state     = normalize(params.get("state")     or params.get("post_state"))
    town      = normalize(
        params.get("town")
        or params.get("post_town")
        or params.get("post_town_input")
    )

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

    # ✅ category filter
    if category:
        seeker_posts = seeker_posts.filter(category_id=category)

    # ✅ hierarchical location filtering (user-driven, not seeker-scope-driven)
    if availability_scope == "continent" and continent:
        seeker_posts = seeker_posts.filter(post_continent_id=continent)

    elif availability_scope == "country" and continent and country:
        seeker_posts = seeker_posts.filter(
            post_continent_id=continent,
            post_country_id=country,
        )

    elif availability_scope == "state" and continent and country and state:
        seeker_posts = seeker_posts.filter(
            post_continent_id=continent,
            post_country_id=country,
            post_state_id=state,
        )

    elif availability_scope == "town" and continent and country and state and town:
        seeker_posts = seeker_posts.filter(
            post_continent_id=continent,
            post_country_id=country,
            post_state_id=state,
            post_town_id=town,
        )

    return seeker_posts

def build_keyword_filter(query):
    """
    Build a Q object for keyword search across relevant Post fields.
    """
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
    return q_objects

# ------------------------------
# Context builder
# ------------------------------

def build_search_context(params, seeker_posts):
    """Build context dict for rendering search results and filters."""
    location_hierarchy = get_location_hierarchy_from_params(params)
    availability_scope = determine_availability_scope(location_hierarchy)

    return {
        "search_query": params.get("q", "").strip(),
        "selected_category": normalize(params.get("category")),
        "availability_scope": availability_scope,
        "location_hierarchy": location_hierarchy,
        "seeker_posts": seeker_posts,
    }