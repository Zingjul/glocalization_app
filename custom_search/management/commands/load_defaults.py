import os
from django.core.management.base import BaseCommand
from django.db import transaction
from custom_search.models import Continent, Country, State, Town


class Command(BaseCommand):
    help = "Load default 'Unspecified' records for Continent, Country, State, and Town"

    @transaction.atomic
    def handle(self, *args, **options):
        # 1. Continent
        continent, created_continent = Continent.objects.get_or_create(
            id=0,
            defaults={
                "code": "UNSPC",
                "name": "Unspecified Continent",
            }
        )

        # 2. Country
        country, created_country = Country.objects.get_or_create(
            id=0,
            defaults={
                "code": "UNSPC",
                "name": "Unspecified Country",
                "country_code": "ZZ",   # ZZ is an official "Unknown/Unspecified" ISO country code
                "continent": continent,
            }
        )

        # 3. State
        state, created_state = State.objects.get_or_create(
            id=0,
            defaults={
                "code": "UNSPC",
                "name": "Unspecified State",
                "country": country,
            }
        )

        # 4. Town
        town, created_town = Town.objects.get_or_create(
            id=0,
            defaults={
                "code": "UNSPC",
                "name": "Unspecified Town",
                "state": state,
                "type": "town",
            }
        )

        self.stdout.write(self.style.SUCCESS("✅ Default 'Unspecified' locations loaded successfully!"))
        self.stdout.write(self.style.SUCCESS(f"   Continent: {continent.name}"))
        self.stdout.write(self.style.SUCCESS(f"   Country: {country.name}"))
        self.stdout.write(self.style.SUCCESS(f"   State: {state.name}"))
        self.stdout.write(self.style.SUCCESS(f"   Town: {town.name}"))
