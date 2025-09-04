import json
import os
from django.core.management.base import BaseCommand
from custom_search.models import Country, State

class Command(BaseCommand):
    help = "Populate states from JSON file"

    def handle(self, *args, **options):
        json_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "data_generator", "raw", "states.json"
        )
        json_path = os.path.abspath(json_path)

        with open(json_path, "r", encoding="utf-8") as f:
            states_data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f"Loaded {len(states_data)} states from JSON"))

        created_count = 0
        skipped_count = 0

        for item in states_data:
            country = None

            # Match country
            country_id = item.get("country_id")
            if country_id:
                country = Country.objects.filter(id=country_id).first()
            if not country and item.get("country_code"):
                country = Country.objects.filter(code=item["country_code"]).first()

            if not country:
                skipped_count += 1
                continue

            # Guarantee uniqueness of code
            raw_code = item.get("iso2")
            if raw_code and not State.objects.filter(code=raw_code).exists():
                code = raw_code
            else:
                code = f"{country.code}_{item['id']}"  # always unique

            obj, created = State.objects.update_or_create(
                id=item["id"],   # preserve provided ID
                defaults={
                    "code": code,
                    "name": item.get("name"),
                    "country": country,
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"🎉 Done! States created: {created_count}, Skipped (no country match): {skipped_count}"
        ))
