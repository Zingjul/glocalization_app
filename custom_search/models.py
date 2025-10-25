from django.db import models
from django_countries.fields import CountryField
from django.conf import settings
from person.utils.phone_codes import get_phone_code_by_iso2

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
    phone_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name or self.country_code.name
    
    def save(self, *args, **kwargs):
        if not self.phone_code:
            self.phone_code = get_phone_code_by_iso2(self.country_code)
        super().save(*args, **kwargs)

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
    code = models.CharField(max_length=5, db_index=True, default="TEMP")
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
