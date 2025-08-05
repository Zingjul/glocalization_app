from django.contrib import admin
from .models import Person, Availability
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
            # ✅ Strictly assign existing Continent if found
            if person.continent_input and not person.continent:
                continent_obj = Continent.objects.filter(name__iexact=person.continent_input.strip()).first()
                if continent_obj:
                    person.continent = continent_obj
                else:
                    continent_obj = Continent.objects.create(name=person.continent_input.strip().title())
                    person.continent = continent_obj
                person.continent_input = ""

            # ✅ Strictly assign existing Country if found
            if person.country_input and not person.country:
                country_obj = Country.objects.filter(name__iexact=person.country_input.strip(), continent=person.continent).first()
                if country_obj:
                    person.country = country_obj
                else:
                    if not person.continent:
                        self.message_user(request, f"❗ Cannot approve country '{person.country_input}' for {person.user.username} — no continent selected.", level="error")
                        continue
                    country_obj = Country.objects.create(name=person.country_input.strip().title(), continent=person.continent)
                    person.country = country_obj
                person.country_input = ""

            # ✅ Strictly assign existing State if found
            if person.state_input and not person.state:
                state_obj = State.objects.filter(name__iexact=person.state_input.strip(), country=person.country).first()
                if state_obj:
                    person.state = state_obj
                else:
                    if not person.country:
                        self.message_user(request, f"❗ Cannot approve state '{person.state_input}' for {person.user.username} — no country selected.", level="error")
                        continue
                    state_obj = State(name=person.state_input.strip().title(), country=person.country)
                    try:
                        state_obj.save()  # ✅ Save new state safely
                        person.state = state_obj
                    except IntegrityError:
                        self.message_user(request, f"❌ Error: Duplicate state '{person.state_input}' detected. Approval skipped for {person.user.username}.", level="error")
                        continue
                person.state_input = ""

            # ✅ Strictly assign existing Town if found
            if person.town_input and not person.town:
                town_obj = Town.objects.filter(name__iexact=person.town_input.strip(), state=person.state).first()
                if town_obj:
                    person.town = town_obj
                else:
                    if not person.state:
                        self.message_user(request, f"❗ Cannot approve town '{person.town_input}' for {person.user.username} — no state selected.", level="error")
                        continue
                    town_obj = Town(name=person.town_input.strip().title(), state=person.state)
                    town_obj.save()
                    person.town = town_obj
                person.town_input = ""

            # ✅ Mark profile as "approved"
            person.approval_status = "approved"
            person.save()
            approved += 1

        self.message_user(request, f"✅ Approved {approved} profile(s) and verified their location.")

    approve_location_inputs.short_description = "Verify and assign existing locations, creating new ones only when necessary"
