# posts/managers.py
from django.db import models
from django.db.models import Q
# This file defines custom query logic for filtering posts based on a user's profile and location.

class PostQuerySet(models.QuerySet):
    def visible_to(self, user):
        # Get the user's profile (if they have one)
        profile = getattr(user, "profile", None)
        # Start with only posts that are approved
        qs = self.filter(status="approved")

        # CASE 1: If the user has no profile, show all approved posts (no location filtering)
        if not profile:
            return qs
            
        # CASE 3:
        # Build up filters for posts that match the user's location
        filters = Q()
        # Always include global posts
        filters |= Q(availability_scope="global")

        # If the user has a continent set, include posts for that continent
        if getattr(profile, "continent", None):
            filters |= Q(availability_scope="continent", post_continent=profile.continent)

        # If the user has a country set, include posts for that country
        if getattr(profile, "country", None):
            filters |= Q(
                availability_scope="country",
                post_continent=profile.continent,
                post_country=profile.country,
            )

        # If the user has a state set, include posts for that state
        if getattr(profile, "state", None):
            filters |= Q(
                availability_scope="state",
                post_continent=profile.continent,
                post_country=profile.country,
                post_state=profile.state,
            )

        # If the user has a town set, include posts for that town
        if getattr(profile, "town", None):
            filters |= Q(
                availability_scope="town",
                post_continent=profile.continent,
                post_country=profile.country,
                post_state=profile.state,
                post_town=profile.town,
            )

        # CASE 2: user has a profile but it's not yet approved → show all approved posts
        if profile.approval_status != "approved":
            return qs
    
        # Return all posts that match any of these filters, without duplicates
        return qs.filter(filters).distinct()