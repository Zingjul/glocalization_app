from django.contrib import admin
from .models import Continent, Country, State, Town

admin.site.register(Continent)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Town)