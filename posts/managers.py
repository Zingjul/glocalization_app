# posts/managers.py
from django.db import models
from django.db.models import Q

class PostQuerySet(models.QuerySet):
    def visible_to(self, user):
        profile = getattr(user, "profile", None)
        qs = self.filter(status="approved")

        # If no profile, only global
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
