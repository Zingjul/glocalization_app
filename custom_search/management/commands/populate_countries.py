import json
import os
from django.core.management.base import BaseCommand
from custom_search.models import Country, Continent

class Command(BaseCommand):
    help = "Populate countries from JSON file"

    def handle(self, *args, **options):
        json_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data_generator", "raw", "countries.json"
        )
        json_path = os.path.abspath(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            countries_data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(countries_data)} countries from JSON"))

        created_count = 0

        for entry in countries_data:
            try:
                continent = Continent.objects.get(id=entry["region_id"])
            except Continent.DoesNotExist:
                self.stdout.write(self.style.WARNING(
                    f"❌ Skipped {entry['name']}: Continent with ID {entry['region_id']} not found"
                ))
                continue

            country, created = Country.objects.get_or_create(
                id=entry["id"],
                defaults={
                    "code": entry["iso2"],
                    "name": entry["name"],
                    "country_code": entry["iso2"],
                    "continent": continent,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"✅ Created: {country.name}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Done! Total countries created: {created_count}"))
