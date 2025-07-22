from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from custom_search.models import Continent, Country, State, Town

User = get_user_model()

# 🔽 Function for dynamic image path
def post_image_upload_path(instance, filename):
    """Store images inside a folder named after the user ID."""
    user_folder = f"user_{instance.post.author.id}"  # Unique folder for each user
    return f"posts/images/{user_folder}/{filename}"
    
class Category(models.Model):
    name = models.CharField(max_length=77, unique=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]

    # New field to define the scope of the post's availability
    # This will be crucial for implementing the "global within scope" logic
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
        default='town', # Default to most specific
        help_text="Defines the scope of availability for this post (e.g., specific town, entire state, etc.)."
    )
 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=False, editable=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")

    # Common fields
    product_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    author_phone_number = PhoneNumberField()
    author_email = models.EmailField(max_length=254, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    business_name = models.CharField(max_length=255, blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # 🔽 Post-specific location (dropdown selection from custom_search)
    post_continent = models.ForeignKey(
        Continent, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_continent'
    )
    post_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_country'
    )
    post_state = models.ForeignKey(
        State, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_state'
    )
    post_town = models.ForeignKey(
        Town, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='post_specific_town'
    )

    # 📝 Post-specific location (text input fallback if dropdowns don’t cover it)
    post_continent_input = models.CharField(max_length=100, blank=True, null=True)
    post_country_input = models.CharField(max_length=100, blank=True, null=True)
    post_state_input = models.CharField(max_length=100, blank=True, null=True)
    post_town_input = models.CharField(max_length=100, blank=True, null=True)

    # Product-specific fields
    color = models.CharField(max_length=100, blank=True, null=True)
    brand = models.CharField(max_length=100, blank=True, null=True)
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('fairly used', 'Fairly Used')], blank=True, null=True)
    model_version = models.CharField(max_length=100, blank=True, null=True)
    technical_specifications = models.TextField(blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)

    # Service-specific fields
    service_details = models.CharField(max_length=50, choices=[('yes', 'Yes'), ('no', 'No')], blank=True, null=True)
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

    def __str__(self):
        return f"{self.product_name} by {self.author.username} on {self.date}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-date"]


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=post_image_upload_path)

    def __str__(self):
        return f"Image for post: {self.post.product_name or 'No Title'}"

    def clean(self):
        if self.image.size > 6 * 1024 * 1024:
            raise ValidationError("Each image must be under 6MB.")


class SocialPlatform(models.Model):
    name = models.CharField(max_length=100)
    icon = models.ImageField(upload_to="social_icons/", blank=True, null=True)

    def __str__(self):
        return self.name


class SocialMediaHandle(models.Model):
    post = models.OneToOneField('Post', on_delete=models.CASCADE, related_name='social_handles')
    linkedin = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    whatsapp = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Handles for {self.post}"

def get_absolute_url(self):
    return reverse("posts:post_detail", kwargs={"pk": self.pk})