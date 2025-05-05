import json
import os
import re
from googletrans import Translator

# 📁 File setup
BASE_DIR = os.path.join(os.path.dirname(__file__), "./towns/")
OUTPUT_FILE = "extracted_cities.json"

# 🌍 Manual translations
manual_name_map = {
    "بورت هاركورت": "Port Harcourt",
    "دبي": "Dubai",
    "الرياض": "Riyadh",
    "القاهرة": "Cairo",
    "广西壮族自治区": "Guangxi Zhuang Autonomous Region",
    "北京市": "Beijing",
    "上海市": "Shanghai",
    # Add more as needed...
}

# 🌐 Translator setup
translator = Translator()

# 🔎 Detect non-English text
def is_non_english(text):
    return bool(re.search(r'[^\u0000-\u007F]', text))

# 🔄 Translate safely, return None on error
def smart_translate(text):
    if not text:
        return None
    if text in manual_name_map:
        return manual_name_map[text]
    if is_non_english(text):
        try:
            translated = translator.translate(text, dest='en')
            return translated.text
        except Exception as e:
            print(f"⚠️ Skipping due to translation error: '{text}' -> {e}")
            return None
    return text  # already English

cities_data = []

for country_code in os.listdir(BASE_DIR):
    parent_folder = os.path.join(BASE_DIR, country_code)

    if not os.path.isdir(parent_folder):
        continue

    sub_folder = os.path.join(parent_folder, country_code)
    ndjson_path = os.path.join(sub_folder, "place-city.ndjson")

    if not os.path.exists(ndjson_path):
        continue

    try:
        with open(ndjson_path, "r", encoding="utf-8") as file:
            for line in file:
                data = json.loads(line)

                city_name = data.get("other_names", {}).get("name:en") or data.get("name")
                state_name = data["address"].get("state")
                country_id = data["address"].get("country_code")

                if not city_name or not state_name or not country_id:
                    continue

                # 🔄 Translate safely
                city_name = smart_translate(city_name)
                state_name = smart_translate(state_name)
                country_id = smart_translate(country_id)

                if not city_name or not state_name or not country_id:
                    continue  # ⛔ Skip if translation failed

                cities_data.append({
                    "name": city_name,
                    "state": state_name,
                    "type": "city",
                    "id": smart_translate(country_id).upper(),
                })

    except Exception as e:
        print(f"❌ Error processing {country_code}: {e}")

# ✅ Save results
if cities_data:
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as json_file:
            json.dump(cities_data, json_file, indent=4, ensure_ascii=False)
        print(f"🚀 Successfully saved translated city data to '{OUTPUT_FILE}'")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
else:
    print("⚠️ No valid city data extracted!")
