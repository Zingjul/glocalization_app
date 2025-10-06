# seekerfinder/services.py
from django.db.models import Q
from seekers.models import SeekerPost

SEARCH_FIELDS = [
    "title__icontains",
    "description__icontains",
    "business_name__icontains",
    "category__name__icontains",
]

def build_keyword_filter(query):
    """
    Build an AND filter across tokens, OR across fields for each token.
    e.g. 'nike shoe' → must match 'nike' somewhere AND 'shoe' somewhere.
    """
    q = Q()
    if not query:
        return q
    tokens = [t.strip() for t in query.split() if t.strip()]
    for token in tokens:
        token_q = Q()
        for fld in SEARCH_FIELDS:
            token_q |= Q(**{fld: token})
        q &= token_q
    return q

def visible_to(queryset, user):
    """Return only posts visible to the given user, based on availability scope."""
    profile = getattr(user, "profile", None)

    qs = queryset.filter(status="approved")

    # If no profile, only show global
    if not profile:
        return qs.filter(availability_scope="global")

    filters = Q()
    filters |= Q(availability_scope="global")

    if getattr(profile, "continent", None):
        filters |= Q(availability_scope="continent", post_continent=profile.continent)

    if getattr(profile, "country", None):
        filters |= Q(
            availability_scope="country",
            post_continent=profile.continent,
            post_country=profile.country,
        )

    if getattr(profile, "state", None):
        filters |= Q(
            availability_scope="state",
            post_continent=profile.continent,
            post_country=profile.country,
            post_state=profile.state,
        )

    if getattr(profile, "town", None):
        filters |= Q(
            availability_scope="town",
            post_continent=profile.continent,
            post_country=profile.country,
            post_state=profile.state,
            post_town=profile.town,
        )

    return qs.filter(filters).distinct()

def search_seeker_posts(query=None, user=None, bypass=False, location_filters=None):
    """
    Search seeker posts with optional bypass.
    """
    if bypass:
        qs = SeekerPost.objects.filter(status="approved")
    else:
        qs = visible_to(SeekerPost.objects.all(), user)

    # Apply location override if user selected filters
    if location_filters:
        loc_q = Q()
        loc_q |= Q(availability_scope="global")

        continent = location_filters.get("continent")
        country = location_filters.get("country")
        state = location_filters.get("state")
        town = location_filters.get("town")

        if continent:
            loc_q |= Q(availability_scope="continent", post_continent__name__iexact=continent)
        if country:
            loc_q |= Q(availability_scope="country", post_country__name__iexact=country)
        if state:
            loc_q |= Q(availability_scope="state", post_state__name__iexact=state)
        if town:
            loc_q |= Q(availability_scope="town", post_town__name__iexact=town)

        qs = qs.filter(loc_q)

    # Apply keyword query
    if query:
        kw_q = build_keyword_filter(query)
        if kw_q:
            qs = qs.filter(kw_q)

    return qs.distinct().order_by("-created_at")
