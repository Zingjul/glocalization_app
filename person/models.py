from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from custom_search.models import Continent, Country, State, Town
from django.utils.timezone import now  # Import timezone utility

class Person(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
        verbose_name=_("User"),
    )
    business_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Business Name"),
    )
    person_profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
    )
    about = models.TextField(
        blank=True,
        verbose_name=_("About"),
    )
    website = models.URLField(
        blank=True,
        verbose_name=_("Website"),
    )
    use_business_name = models.BooleanField(
        default=False,
        verbose_name=_("Use Business Name"),
    )

    # Location fields linked to custom_search
    continent = models.ForeignKey(
        Continent, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons"
    )
    country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons"
    )
    state = models.ForeignKey(
        State, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons"
    )
    town = models.ForeignKey(
        Town, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons"
    )

    # Temporary fields for user-typed location data (for admin review)
    continent_input = models.CharField(max_length=100, blank=True, null=True)
    country_input = models.CharField(max_length=100, blank=True, null=True)
    state_input = models.CharField(max_length=100, blank=True, null=True)
    town_input = models.CharField(max_length=100, blank=True, null=True)

    date_joined = models.DateTimeField(default=now, verbose_name=_("Date Joined"))  # Tracks when the user created profile
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))  # Tracks updates

    def __str__(self):
        return f"{self.user.username} ({self.business_name})" if self.business_name else self.user.username

    def get_absolute_url(self):
        return reverse("person_profile", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-date_joined"]  # Sort profiles by most recent users