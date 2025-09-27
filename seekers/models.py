from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from custom_search.models import Continent as SeekerContinent, Country as SeekerCountry, State as SeekerState, Town as SeekerTown
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from media_app.models import MediaFile
from datetime import timedelta

User = get_user_model()

def default_expiry():
    return timezone.now() + timedelta(days=7)

class SeekerCategory(models.Model):
    """Separate category model for seekers to avoid collision with posts.Category."""
    name = models.CharField(max_length=77, unique=True)

    class Meta:
        db_table = "seeker_category"
        verbose_name = "Seeker Category"
        verbose_name_plural = "Seeker Categories"

    def __str__(self):
        return self.name


class SeekerPost(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    AVAILABILITY_SCOPE_CHOICES = [
        ('global', 'Global'),
        ('continent', 'Continent-wide'),
        ('country', 'Country-wide'),
        ('state', 'State-wide'),
        ('town', 'Town-specific'),
    ]

    availability_scope = models.CharField(
        max_length=10,
        choices=AVAILABILITY_SCOPE_CHOICES,
        default='town',  # Default to most specific
        help_text="Defines the scope of availability for this post (e.g., specific town, entire state, etc.)."
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="seeker_posts"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    category = models.ForeignKey(
        SeekerCategory,
        on_delete=models.CASCADE,
        null=False,
        default=1,
        help_text="Category for this seeker post. Defaults to 'General'."
    )
    business_name = models.CharField(max_length=255, blank=True, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author_phone_number = PhoneNumberField()
    author_email = models.EmailField(blank=True, null=True)

    # ✅ Generic relation to MediaFile (no duplication)
    media_files = GenericRelation(MediaFile, related_query_name="seeker_posts")

    @property
    def images(self):
        return self.media_files.filter(file_type="image")

    @property
    def videos(self):
        return self.media_files.filter(file_type="video")

    post_continent = models.ForeignKey(
        SeekerContinent, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seeker_posts_continent"
    )
    post_country = models.ForeignKey(
        SeekerCountry, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seeker_posts_country"
    )
    post_state = models.ForeignKey(
        SeekerState, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seeker_posts_state"
    )
    post_town = models.ForeignKey(
        SeekerTown, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seeker_posts_town"
    )

    post_continent_input = models.CharField(max_length=100, blank=True, null=True)
    post_country_input = models.CharField(max_length=100, blank=True, null=True)
    post_state_input = models.CharField(max_length=100, blank=True, null=True)
    post_town_input = models.CharField(max_length=100, blank=True, null=True)

    preferred_fulfillment_time = models.CharField(max_length=255, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_fulfilled = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now, editable=False)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# here we can increase the number of days a post will last after successful upload, before it expires and gets deleted from the database
    expires_at = models.DateTimeField(default=default_expiry)

    class Meta:
        db_table = "seeker_post"
        ordering = ["-date"]
        verbose_name = "Seeker Post"
        verbose_name_plural = "Seeker Posts"

    def __str__(self):
        return f"{self.title} by {self.author.username} on {self.date}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("seekers:seeker_detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.post_town_input:
            normalized_town = self.post_town_input.strip().title()

            pending, created = PendingSeekerLocationRequest.objects.get_or_create(
                post=self,
                defaults={
                    "typed_town": normalized_town,
                    "parent_state": self.post_state
                }
            )

            if not created:
                pending.typed_town = normalized_town
                pending.parent_state = self.post_state
                pending.is_reviewed = False
                pending.approved = False
                pending.save()
        else:
            PendingSeekerLocationRequest.objects.filter(post=self).delete()


class PendingSeekerLocationRequest(models.Model):
    post = models.OneToOneField(
        "seekers.SeekerPost",
        on_delete=models.CASCADE,
        related_name="seeker_location_request"
    )
    typed_town = models.CharField(max_length=100, blank=True, null=True)
    parent_state = models.ForeignKey(
        "custom_search.State",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="seeker_pending_requests"
    )
    is_reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pending_seeker_location_request"
        verbose_name = "Pending Seeker Location Request"
        verbose_name_plural = "Pending Seeker Location Requests"

    def __str__(self):
        return f"Pending town '{self.typed_town}' for SeekerPost #{self.post.id}"


class SeekerResponse(models.Model):
    seeker_post = models.ForeignKey("SeekerPost", on_delete=models.CASCADE, related_name="seeker_responses")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seeker_sent_responses")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seeker_received_responses")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seeker_response"
        verbose_name = "Seeker Response"
        verbose_name_plural = "Seeker Responses"

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.seeker_post.title})"


class SeekerSocialMediaHandle(models.Model):
    post = models.OneToOneField(
        'SeekerPost',
        on_delete=models.CASCADE,
        related_name='seeker_social_handles'
    )
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    class Meta:
        db_table = "seeker_social_media_handle"
        verbose_name = "Seeker Social Media Handle"
        verbose_name_plural = "Seeker Social Media Handles"

    def __str__(self):
        return f"Handles for {self.post.title}"
