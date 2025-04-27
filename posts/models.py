from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from custom_search.models import Continent, Country, State, Town  # Import location models

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=77, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    author_phone_number = PhoneNumberField(blank=False)
    author_email = models.EmailField(max_length=254, blank=True)

    # Location Fields
    use_default_location = models.BooleanField(default=True)  # Determines whether to use profile location
    continent = models.ForeignKey(Continent, on_delete=models.SET_NULL, blank=True, null=True, editable=False)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, blank=True, null=True, editable=False)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, blank=True, null=True, editable=False)
    town = models.ForeignKey(Town, on_delete=models.SET_NULL, blank=True, null=True, editable=False)

    def save(self, *args, **kwargs):
        # If user selects default location, use their profile's location
        if self.use_default_location and not self.pk:  # Only set on creation
            profile = self.author.profile  
            self.continent = profile.continent
            self.country = profile.country
            self.state = profile.state
            self.town = profile.town

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_name} by {self.author.username} on {self.date}"

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={"pk": self.pk})

    class Meta:
        ordering = ["-date"]

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="post_images/")
