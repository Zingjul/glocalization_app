from django.db import models
from django_countries.fields import CountryField

class Continent(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)  # Ensures uniqueness for continents

    class Meta:
        ordering = ['name']  # Sorts alphabetically for better UI display

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, blank=True, unique=True, null=True)
    country_code = CountryField(blank_label='(select country)')
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name="countries",  db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name or self.country_code.name

class State(models.Model):
    id = models.CharField(max_length=20, primary_key=True)  # ✅ Change to CharField to allow string-based IDs
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="states",  db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
class Town(models.Model):
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