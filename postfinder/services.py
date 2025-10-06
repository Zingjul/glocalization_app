# postfinder/services.py
from django.db.models import Q
from posts.models import Post

SEARCH_FIELDS = [
    "product_name__icontains",
    "description__icontains",
    "brand__icontains",
    "business_name__icontains",
    "technical_specifications__icontains",
    "warranty__icontains",
]

def build_keyword_filter(query):
    q = Q()
    if not query:
        return q
    if not isinstance(query, str):   # ✅ safeguard
        query = str(query)
    tokens = [t.strip() for t in query.split() if t.strip()]
    for token in tokens:
        token_q = Q()
        for fld in SEARCH_FIELDS:
            token_q |= Q(**{fld: token})
        q &= token_q
    return q

def search_posts(query=None, user=None, bypass=False, location_filters=None):
    """
    - query: search text
    - user: requesting user
    - bypass: if True, ignore visible_to rules and search worldwide
    - location_filters: dict like {'continent': 'Africa', 'country': 'Nigeria', 'state': 'Lagos', 'town': 'Ikeja'}
    """
    # start queryset
    if bypass:
        qs = Post.objects.filter(status="approved")
    else:
        qs = Post.objects.visible_to(user)

    # apply location override if provided (finder UI might supply these)
    if location_filters:
        loc_q = Q()
        # always include global posts
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

    # apply query keywords
    if query:
        kw_q = build_keyword_filter(query)
        if kw_q:
            qs = qs.filter(kw_q)

    return qs.distinct().order_by("-created_at")
