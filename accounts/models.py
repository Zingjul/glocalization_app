# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django_countries.fields import CountryField
import secrets
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from person.utils.phone_codes import get_phone_code_by_iso2
import phonenumbers

# Import your Country model
from custom_search.models import Country


def generate_virtual_id(length=16):
    """Generates a secure random URL-safe string."""
    return secrets.token_urlsafe(length)

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)

    # ✅ Country ISO2 code (e.g., NG, US)
    country_code = CountryField(blank_label="(select country)", blank=True, null=True)

    # ✅ Full phone number with prefix
    phone_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    virtual_id = models.CharField(max_length=32, unique=True, blank=True, null=True)

    # 📊 Follower counts
    follower_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        """Auto-assign virtual ID and phone prefix from country code."""
        if not self.virtual_id:
            self.virtual_id = generate_virtual_id()

        # ✅ Smart phone number formatting using phonenumbers
        if self.country_code and self.phone_number:
            try:
                iso2 = str(self.country_code).upper().strip()
                number_str = str(self.phone_number).strip()
                # If number starts with '+', parse as international, else as national
                if number_str.startswith('+'):
                    parsed_number = phonenumbers.parse(number_str, None)
                else:
                    parsed_number = phonenumbers.parse(number_str, iso2)
                if not phonenumbers.is_valid_number(parsed_number):
                    raise ValueError("Invalid phone number for selected country.")
                formatted_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
                self.phone_number = formatted_number
            except Exception as e:
                print(f"[Phone Number Parsing Error] {e}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.email})" if self.email else self.username

    class Meta:
        app_label = "accounts"

class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="following",
        on_delete=models.CASCADE,
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="followers",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower} → {self.following}"


@receiver(post_save, sender=Follow)
def update_counts_on_follow(sender, instance, created, **kwargs):
    if created:
        instance.following.follower_count = models.F("follower_count") + 1
        instance.follower.following_count = models.F("following_count") + 1
        instance.following.save(update_fields=["follower_count"])
        instance.follower.save(update_fields=["following_count"])

@receiver(post_delete, sender=Follow)
def update_counts_on_unfollow(sender, instance, **kwargs):
    # Refresh from DB to get actual value
    following = instance.following
    follower = instance.follower
    following.refresh_from_db(fields=["follower_count"])
    follower.refresh_from_db(fields=["following_count"])

    following.follower_count = max(0, following.follower_count - 1)
    follower.following_count = max(0, follower.following_count - 1)
    following.save(update_fields=["follower_count"])
    follower.save(update_fields=["following_count"])