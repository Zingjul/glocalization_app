from django.contrib import admin
from .models import Continent, Country, State, Town

class CountryInline(admin.TabularInline):  # ✅ Displays countries inside the continent view
    model = Country
    extra = 0  # ✅ Prevents unnecessary empty rows

class StateInline(admin.TabularInline):  # ✅ Displays states inside the country view
    model = State
    extra = 0

class ContinentAdmin(admin.ModelAdmin):
    list_display = ["name"]
    inlines = [CountryInline]  # 🔥 Shows countries within a continent

class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "continent"]
    list_filter = ["continent"]  # ✅ Allows filtering by continent
    inlines = [StateInline]  # 🔥 Shows states within a country

class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "country"]
    list_filter = ["country"]  # ✅ Allows filtering by country

class TownAdmin(admin.ModelAdmin):
    list_display = ["name", "state", "type"]  # ✅ Show town name, state, and type in Admin
    list_filter = ["state", "type"]  # ✅ Allow filtering by state and type
    search_fields = ["name"]  # 🔎 Enable search by town name
    
admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Town, TownAdmin)
