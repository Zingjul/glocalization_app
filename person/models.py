from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

class Person(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='profile',
        verbose_name=_("User"),
    )
    business_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("Business Name"),
    )
    person_profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        verbose_name=_("Profile Picture"),
    )
    about = models.TextField(
        blank=True,
        verbose_name=_("About"),
    )
    website = models.URLField(
        blank=True,
        verbose_name=_("Website"),
    )
    use_business_name = models.BooleanField(
        default=False,
        verbose_name=_("Use Business Name"),
    )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("person_profile", kwargs={"pk": self.pk})

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")