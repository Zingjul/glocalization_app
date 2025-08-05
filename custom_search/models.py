from django.db import models
from django_countries.fields import CountryField
from django.conf import settings

class Continent(models.Model):
    id = models.IntegerField(primary_key=True)  # manually assigned
    code = models.CharField(max_length=5, unique=True, db_index=True, default="TEMP")
    name = models.CharField(max_length=100, unique=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Country(models.Model):
    id = models.IntegerField(primary_key=True)  # manually assigned
    code = models.CharField(max_length=5, unique=True, db_index=True, default="TEMP")
    name = models.CharField(max_length=100, blank=True, unique=True, null=True)
    country_code = CountryField(blank_label='(select country)')
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name="countries", db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name or self.country_code.name


class State(models.Model):
    id = models.IntegerField(primary_key=True)  # manually assigned
    code = models.CharField(max_length=5, unique=True, db_index=True, default="TEMP")
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states", db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Town(models.Model):
    id = models.IntegerField(primary_key=True)  # manually assigned
    code = models.CharField(max_length=5, unique=True, db_index=True, default="TEMP")
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name="towns", db_index=True)
    type = models.CharField(
        max_length=50,
        choices=[("city", "City"), ("town", "Town"), ("village", "Village"), ("hamlet", "Hamlet")],
        default="town",
        db_index=True
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.type})"


class PendingLocationRequest(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pending_location')
    typed_continent = models.CharField(max_length=100, blank=True, null=True)
    typed_country = models.CharField(max_length=100, blank=True, null=True)
    typed_state = models.CharField(max_length=100, blank=True, null=True)
    typed_town = models.CharField(max_length=100, blank=True, null=True)
    is_reviewed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Location request by {self.user.username}"
