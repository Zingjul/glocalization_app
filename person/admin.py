from django.contrib import admin
from .models import Person
from custom_search.models import Continent, Country, State, Town
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "user", "business_name",
        "continent", "country", "state", "town",
        "continent_input", "country_input", "state_input", "town_input"
    )
    list_filter = ("continent", "country", "state", "town")
    search_fields = (
        "user__username", "business_name", 
        "continent_input", "country_input", "state_input", "town_input"
    )
    actions = ["approve_location_inputs"]

    def approve_location_inputs(self, request, queryset):
        approved = 0

        for person in queryset:
            # Handle continent
            if person.continent_input and not person.continent:
                continent_obj, _ = Continent.objects.get_or_create(
                    name=person.continent_input.strip().title()
                )
                person.continent = continent_obj
                person.continent_input = ""

            # Handle country
            if person.country_input and not person.country:
                if not person.continent:
                    self.message_user(request, f"❗ Cannot approve country '{person.country_input}' for {person.user.username} — no continent selected.", level="error")
                    continue

                country_obj, _ = Country.objects.get_or_create(
                    name=person.country_input.strip().title(),
                    defaults={"continent": person.continent}
                )
                person.country = country_obj
                person.country_input = ""

            # Handle state
            if person.state_input and not person.state:
                if not person.country:
                    self.message_user(request, f"❗ Cannot approve state '{person.state_input}' for {person.user.username} — no country selected.", level="error")
                    continue

                state_obj, _ = State.objects.get_or_create(
                    name=person.state_input.strip().title(),
                    defaults={"country": person.country}
                )
                person.state = state_obj
                person.state_input = ""

            # Handle town
            if person.town_input and not person.town:
                if not person.state:
                    self.message_user(request, f"❗ Cannot approve town '{person.town_input}' for {person.user.username} — no state selected.", level="error")
                    continue

                town_obj, _ = Town.objects.get_or_create(
                    name=person.town_input.strip().title(),
                    defaults={"state": person.state}
                )
                person.town = town_obj
                person.town_input = ""

            person.save()
            approved += 1

        self.message_user(request, f"✅ Approved {approved} profile(s) with custom location input.")

    approve_location_inputs.short_description = "Approve selected custom location inputs"
