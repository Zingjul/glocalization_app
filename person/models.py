from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from custom_search.models import Continent, Country, State, Town
from django.utils.timezone import now  # Import timezone utility

class Person(models.Model):
    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
        verbose_name=_("User"),
    )
    business_name = models.CharField(max_length=255, blank=True, verbose_name=_("Business Name"))
    real_name = models.CharField(max_length=255, blank=True, verbose_name=_("Real Name"))
    person_profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name=_("Profile Picture"))
    about = models.TextField(blank=True, verbose_name=_("About"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    use_business_name = models.BooleanField(default=False, verbose_name=_("Use Business Name"))

    # Approval status to track verification process
    approval_status = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default='pending',
        verbose_name=_("Approval Status"),
        help_text="Users cannot edit their profile while pending approval.",
    )

    # Admin-selected review message for notifications
    review_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Review Message"),
        help_text="The admin selects a message to inform the user after verification.",
    )

    # Location fields linked to custom_search
    continent = models.ForeignKey(Continent, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons")
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons")
    town = models.ForeignKey(Town, on_delete=models.SET_NULL, blank=True, null=True, related_name="persons")

    # Temporary fields for user-typed location data (for admin review)
    continent_input = models.CharField(max_length=100, blank=True, null=True)
    country_input = models.CharField(max_length=100, blank=True, null=True)
    state_input = models.CharField(max_length=100, blank=True, null=True)
    town_input = models.CharField(max_length=100, blank=True, null=True)

    date_joined = models.DateTimeField(default=now, verbose_name=_("Date Joined"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    def save(self, *args, **kwargs):
        # If state_input is provided and state is empty, try to match it
        if self.state_input and not self.state:
            self.state = State.objects.filter(name__iexact=self.state_input).first()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.business_name})" if self.business_name else self.user.username

    def get_absolute_url(self):
        return reverse("person_profile", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-date_joined"]

class Availability(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.person} - {self.day_of_week}: {self.start_time} to {self.end_time}"