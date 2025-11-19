from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SubscriptionPlan(models.Model):
    LEVEL_CHOICES = [
        ("basic", "Basic"),
        ("premium", "Premium"),
    ]
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.get_level_display()} Plan"


class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    payment_reported = models.BooleanField(default=False)  

    def __str__(self):
        return f"{self.user.username} → {self.plan}"
