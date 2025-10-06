from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from custom_search.models import Continent, Country, State, Town
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from media_app.models import MediaFile   # ✅ proper import
from datetime import timedelta
from .managers import PostQuerySet
User = get_user_model()

def default_expiry():
    return timezone.now() + timedelta(days=7)

class Category(models.Model):
    name = models.CharField(max_length=77, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
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
        default='town',
        help_text="Defines the scope of availability for this post."
    )
    objects = PostQuerySet.as_manager()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    # Common fields
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    author_phone_number = PhoneNumberField()
    author_email = models.EmailField(max_length=254, blank=True)
    date = models.DateTimeField(default=timezone.now, editable=False)
    business_name = models.CharField(max_length=255, blank=True, null=True)

    # ✅ Generic relation to MediaFile (no duplication)
    media_files = GenericRelation(MediaFile, related_query_name="posts")

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # 🔽 Post-specific location (dropdown selection)
    post_continent = models.ForeignKey(
        Continent, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_continent', default=0
    )
    post_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_country', default=0
    )
    post_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_state', default=0
    )
    post_town = models.ForeignKey(
        Town, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_town', default=0
    )

    # Fallback location inputs
    post_continent_input = models.CharField(max_length=100, blank=True, null=True)
    post_country_input = models.CharField(max_length=100, blank=True, null=True)
    post_state_input = models.CharField(max_length=100, blank=True, null=True)
    post_town_input = models.CharField(max_length=100, blank=True, null=True)

    # Product-specific fields
    color = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    condition = models.CharField(
        max_length=50,
        choices=[('new', 'New'), ('fairly used', 'Fairly Used')],
        blank=True, null=True
    )
    model_version = models.CharField(max_length=100, blank=True, null=True)
    technical_specifications = models.TextField(blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)

    # Service-specific fields
    service_details = models.CharField(
        max_length=50,
        choices=[('yes', 'Yes'), ('no', 'No')],
        blank=True, null=True
    )
    qualifications = models.TextField(blank=True, null=True)
    availability_schedule = models.CharField(max_length=255, blank=True, null=True)
    service_guarantees = models.TextField(blank=True, null=True)

    # Labor-specific fields
    labor_experience_years = models.PositiveIntegerField(blank=True, null=True)
    labor_availability = models.CharField(max_length=255, blank=True, null=True)

    # General availability
    availability = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    expires_at = models.DateTimeField(default=default_expiry)

    @property
    def images(self):
        return self.media_files.filter(file_type="image")

    @property
    def videos(self):
        return self.media_files.filter(file_type="video")

    def __str__(self):
        return f"{self.product_name} by {self.author.username} on {self.date}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.post_town_input:
            normalized_town = self.post_town_input.strip().title()

            pending, created = PendingLocationRequest.objects.get_or_create(
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
            PendingLocationRequest.objects.filter(post=self).delete()


class PendingLocationRequest(models.Model):
    post = models.OneToOneField(
        Post,
        on_delete=models.CASCADE,
        related_name="post_location_requests"
    )
    typed_town = models.CharField(max_length=100, blank=True, null=True)
    parent_state = models.ForeignKey(
        "custom_search.State",
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name="post_pending_requests"
    )
    is_reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending town '{self.typed_town}' for Post #{self.post.id}"


class SocialPlatform(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="social_icons/", blank=True, null=True)

    def __str__(self):
        return self.name


class SocialMediaHandle(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='social_handles')
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Handles for {self.post}"
