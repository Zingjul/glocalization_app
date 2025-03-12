from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=77, unique=True)
    def __str__(self):
        return self.name

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(null=False, blank=False) # Modified: null=False, blank=False
    date = models.DateTimeField(auto_now_add=True)
    author_phone_number = PhoneNumberField(blank=False)
    author_email = models.EmailField(max_length=254, blank=True)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        if self.description and len(self.description) > 50:
            return f"{self.description[:50]}..."
        elif self.description:
            return self.description
        else:
            return f"Post by {self.author.username} on {self.date}"

    def get_absolute_url(self):
        return reverse("post_detailed", kwargs={"pk": self.pk})

    class Meta:
        ordering = ['-date']

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='post_images/')