from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from posts.models import PendingLocationRequest
from media_app.models import MediaFile
from custom_search.models import Continent, Country, State, Town
from django.contrib.contenttypes.fields import GenericRelation
def profile_pic_upload_path(instance, filename):
    # Each user gets their own folder inside profile_pics/
    return f"profile_pics/user_{instance.user.id}/{filename}"

def gallery_upload_path(instance, filename):
    # Each user gets their own folder inside gallery/
    return f"gallery/user_{instance.person.user.id}/{filename}"

class Person(models.Model):
    APPROVAL_CHOICES = [
        ('awaiting_user', 'Awaiting User'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    media_files = GenericRelation(MediaFile, related_query_name='person')

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,   #IF WE use the word "CASCADE" in place of "PROTECT" then, the whole will be deleted if we try to delete the profile  
        primary_key=True, related_name='profile', verbose_name=_("User"),
    )
    business_name = models.CharField(max_length=255, blank=True, verbose_name=_("Business Name"))
    real_name = models.CharField(max_length=255, blank=True, verbose_name=_("Real Name"))
    person_profile_picture = models.ImageField(
        upload_to=profile_pic_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Profile Picture")
    )
    about = models.TextField(blank=True, verbose_name=_("About"))
    website = models.URLField(blank=True, verbose_name=_("Website"))
    use_business_name = models.BooleanField(default=False, verbose_name=_("Use Business Name"))

    # Approval / review tracking
    approval_status = models.CharField(
        max_length=15,
        choices=APPROVAL_CHOICES,
        default='awaiting_user',
        verbose_name=_("Approval Status"),
        help_text="Users cannot edit their profile while pending approval.",
    )
    review_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Review Message"),
        help_text="The admin selects a message to inform the user after verification.",
    )

    # Linked dropdown-based location
    continent = models.ForeignKey(
        Continent, on_delete=models.CASCADE, default=0, blank=True, null=True,
        related_name='specific_continent'
    )
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, default=0, blank=True, null=True,
        related_name='specific_country'
    )
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, default=0, blank=True, null=True,
        related_name='specific_state'
    )
    town = models.ForeignKey(
        Town, on_delete=models.CASCADE, default=0, blank=True, null=True,
        related_name='specific_town'
    )
    # User-typed fallback (to be reviewed by admin)
    continent_input = models.CharField(max_length=100, blank=True, null=True)
    country_input = models.CharField(max_length=100, blank=True, null=True)
    state_input = models.CharField(max_length=100, blank=True, null=True)
    town_input = models.CharField(max_length=100, blank=True, null=True)

    date_joined = models.DateTimeField(default=now, verbose_name=_("Date Joined"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Last Updated"))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        unspecified_town = Town.objects.filter(id=0).first()

        print("DEBUG → town:", self.town)
        print("DEBUG → town.id:", getattr(self.town, "id", None))
        print("DEBUG → town_input:", self.town_input)

        if self.town_input and self.town == unspecified_town:
            print("DEBUG → Creating PendingLocationRequest...")
            if not PendingLocationRequest.objects.filter(
                person=self, typed_town=self.town_input
            ).exists():
                PendingLocationRequest.objects.create(
                    person=self,
                    typed_town=self.town_input,
                    parent_state=self.state
                )
                
    @property
    def follower_count(self):
        return self.user.follower_count

    @property
    def following_count(self):
        return self.user.following_count

    @property
    def is_followed_by_current_user(self):
        from accounts.models import Follow  # avoid circular imports
        from django.contrib.auth import get_user_model
        user = getattr(self, "_current_request_user", None)
        if user and user.is_authenticated:
            return Follow.objects.filter(follower=user, following=self.user).exists()
        return False

    @property
    def subscription(self):
        from entitle.models import UserSubscription
        try:
            return UserSubscription.objects.get(user=self.user)
        except UserSubscription.DoesNotExist:
            return None

    @property
    def auto_approval_hours(self):
        sub = self.subscription
        if sub and sub.is_active:
            return sub.plan.auto_approval_hours
        return 24  # default fallback for free/unsubscribed users

    def __str__(self):
        return f"{self.user.username} ({self.business_name})" if self.business_name else self.user.username

    def get_absolute_url(self):
        return reverse("person_detail", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")
        ordering = ["-date_joined"]

    @property
    def profile_picture(self):
        """Get the first image media file as profile picture"""
        profile_pic = self.media_files.filter(file_type='image').first()
        return profile_pic
    
    @property
    def profile_picture_url(self):
        """Get profile picture URL or None"""
        pic = self.profile_picture
        return pic.file.url if pic else None

    @property
    def gallery_images(self):
        """Get all gallery images"""
        return self.gallery_items.filter(media_type='image')

    @property
    def gallery_videos(self):
        """Get all gallery videos"""
        return self.gallery_items.filter(media_type='video')

    @property
    def gallery_count(self):
        """Get total gallery items count"""
        return self.gallery_items.count()
        
class PendingLocationRequest(models.Model):
    """Stores user-typed locations for admin review before approval."""
    person = models.OneToOneField(
        Person,
        on_delete=models.CASCADE,
        related_name="pending_location_request"
    )
    typed_town = models.CharField(max_length=100, blank=True, null=True)
    parent_state = models.ForeignKey(
        State,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="pending_person_requests"
    )
    is_reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending town '{self.typed_town}' for Person {self.person.user.username}"

class Availability(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday'),
        ]
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.person} - {self.day_of_week}: {self.start_time} to {self.end_time}"

class PersonGallery(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='gallery_items',
        verbose_name=_("Person")
    )
    file = models.FileField(
        upload_to=gallery_upload_path,
        verbose_name=_("File")
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
        default='image',
        verbose_name=_("Media Type")
    )
    caption = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Caption")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Uploaded At")
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Display Order")
    )
    
    class Meta:
        verbose_name = _("Gallery Item")
        verbose_name_plural = _("Gallery Items")
        ordering = ['order', '-uploaded_at']
    
    def __str__(self):
        return f"{self.person.user.username} - {self.media_type} ({self.id})"
    
    def save(self, *args, **kwargs):
        # Auto-detect media type based on file extension
        if self.file:
            extension = self.file.name.lower().split('.')[-1]
            video_extensions = ['mp4', 'mov', 'avi', 'mkv', 'webm']
            if extension in video_extensions:
                self.media_type = 'video'
            else:
                self.media_type = 'image'
        super().save(*args, **kwargs)