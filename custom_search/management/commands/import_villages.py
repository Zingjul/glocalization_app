import json
import os
import re
from googletrans import Translator
from django.core.management.base import BaseCommand
from custom_search.models import Country, State, Town

DATA_PATH = os.path.join(os.path.dirname(__file__), "../../../data_generator/ready/extracted_villages.json")

translator = Translator()

def is_non_english(text):
    return bool(re.search(r'[^\u0000-\u007F]', text))

def smart_translate(text):
    if not text:
        return None
    if is_non_english(text):
        try:
            return translator.translate(text, dest="en").text
        except Exception:
            return None
    return text  

def process_json():
    if not os.path.exists(DATA_PATH):
        print(f"⚠️ File {DATA_PATH} not found!")
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def get_country(country_code):
    try:
        return Country.objects.get(country_code=country_code)
    except Country.DoesNotExist:
        print(f"⚠️ Country '{country_code}' not found!")
        return None

def process_entries(entries):
    total_inserted = 0
    for entry in entries:
        name = smart_translate(entry.get("name"))
        state_name = smart_translate(entry.get("state"))
        location_type = "village"
        country_code = entry.get("id")

        if not name or not state_name or not country_code:
            continue

        country_obj = get_country(country_code)
        if not country_obj:
            continue

        state_obj, _ = State.objects.get_or_create(name=state_name, country=country_obj)

        _, created = Town.objects.get_or_create(
            name=name,
            state=state_obj,
            defaults={"type": location_type}
        )

        if created:
            total_inserted += 1

    return total_inserted

class Command(BaseCommand):
    help = "Import cities from JSON"

    def handle(self, *args, **kwargs):
        entries = process_json()
        inserted_count = process_entries(entries)
        print(f"✅ Imported {inserted_count} cities!")
