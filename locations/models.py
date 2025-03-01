from django.db import models

class Continent(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    continent = models.ForeignKey(Continent, on_delete=models.CASCADE, related_name='countries')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Town(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='towns')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name