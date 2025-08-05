from django.contrib import admin
from .models import Continent, Country, State, Town, PendingLocationRequest

# 🔗 Inline: Countries shown within a Continent
class CountryInline(admin.TabularInline):
    model = Country
    extra = 0
    show_change_link = True  # ✅ Make countries clickable from inline

# 🔗 Inline: States shown within a Country
class StateInline(admin.TabularInline):
    model = State
    extra = 0
    show_change_link = True

# 🔗 Inline: Towns shown within a State
class TownInline(admin.TabularInline):
    model = Town
    extra = 0
    show_change_link = True

# 🌍 Continent Admin
class ContinentAdmin(admin.ModelAdmin):
    list_display = ["name", "country_count"]
    search_fields = ["name"]
    inlines = [CountryInline]  # ✅ Display countries inline

    def country_count(self, obj):
        return obj.countries.count()
    country_count.short_description = "Countries"

# 🗺 Country Admin
class CountryAdmin(admin.ModelAdmin):
    list_display = ["name", "continent", "state_count"]
    list_filter = ["continent"]
    search_fields = ["name"]
    inlines = [StateInline]

    def state_count(self, obj):
        return obj.states.count()
    state_count.short_description = "States"

# 🏞 State Admin
class StateAdmin(admin.ModelAdmin):
    list_display = ["name", "country", "town_count"]
    list_filter = ["country"]
    search_fields = ["name"]
    inlines = [TownInline]

    def town_count(self, obj):
        return obj.towns.count()
    town_count.short_description = "Towns"

# 🏘 Town Admin
class TownAdmin(admin.ModelAdmin):
    list_display = ["name", "state", "type"]
    list_filter = ["state", "type"]
    search_fields = ["name"]

# 🚀 Register Admin Interfaces
admin.site.register(Continent, ContinentAdmin)
admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Town, TownAdmin)
