from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=77, unique=True)  # unique=True prevents duplicate categories
    def __str__(self):
        return self.name

class Post(models.Model):  # Changed class name to singular "Post" for convention
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    author_phone_number = PhoneNumberField(blank=False)
    author_email = models.EmailField(max_length=254, blank=True)  # Use EmailField for email

    def __str__(self):
        # Improved __str__ method: Display something more informative if description is long
        if self.description and len(self.description) > 50:
            return f"{self.description[:50]}..."  # Truncate if longer than 50 characters
        elif self.description:
            return self.description
        else:
            return f"Post by {self.author.username} on {self.date}" #Fallback if no description

    def get_absolute_url(self):
        return reverse("post_detailed", kwargs={"pk": self.pk})

    class Meta:  # Added Meta class for ordering
        ordering = ['-date']  # Orders posts by date, newest first



class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')  # Important!
    image = models.ImageField(upload_to='post_images/')