from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from custom_search.models import Continent, Country, State, Town

User = get_user_model()

class SeekerPost(models.Model):
    REQUEST_TYPES = [
        ('product', 'Product'),
        ('service', 'Service'),
        ('labor', 'Labor'),
    ]
    AVAILABILITY_SCOPE_CHOICES = [
        ('global', 'Global'),
        ('continent', 'Continent-wide'),
        ('country', 'Country-wide'),
        ('state', 'State-wide'),
        ('town', 'Town-specific'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="seekers_posts"
    )

    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    availability_scope = models.CharField(max_length=10, choices=AVAILABILITY_SCOPE_CHOICES, default='town')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    business_name = models.CharField(max_length=255, blank=True, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    author_phone_number = PhoneNumberField()
    author_email = models.EmailField(blank=True, null=True)

    post_continent = models.ForeignKey(
        Continent, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seekers_post_continent"
    )
    post_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seekers_post_country"
    )
    post_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seekers_post_state"
    )
    post_town = models.ForeignKey(
        Town, on_delete=models.SET_NULL, blank=True, null=True,
        related_name="seekers_post_town"
    )

    post_continent_input = models.CharField(max_length=100, blank=True, null=True)
    post_country_input = models.CharField(max_length=100, blank=True, null=True)
    post_state_input = models.CharField(max_length=100, blank=True, null=True)
    post_town_input = models.CharField(max_length=100, blank=True, null=True)

    preferred_fulfillment_time = models.CharField(max_length=255, blank=True, null=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_fulfilled = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"

    def get_absolute_url(self):
        return reverse("seekers:seeker_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-created_at"]

def seeker_image_upload_path(instance, filename):
    user_folder = f"user_{instance.seeker_post.author.id}"
    return f"seekers/images/{user_folder}/{filename}"

class SeekerImage(models.Model):
    seeker_post = models.ForeignKey(
        SeekerPost, on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to=seeker_image_upload_path)

    def __str__(self):
        return f"Image for request: {self.seeker_post.title or 'Untitled'}"

    def clean(self):
        if self.image.size > 6 * 1024 * 1024:
            raise ValidationError("Each image must be under 6MB.")

class SeekerResponse(models.Model):
    seeker_post = models.ForeignKey("SeekerPost", on_delete=models.CASCADE, related_name="responses")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_responses")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_responses")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.receiver} ({self.seeker_post.title})"
