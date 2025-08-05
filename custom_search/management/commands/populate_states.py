import json
import os
from django.core.management.base import BaseCommand
from custom_search.models import Country, State, Continent
from .skipped_continent_mapping import skipped_country_continent_mapping
# 🔥 Path to JSON file (update based on location)
JSON_PATH = os.path.join(os.path.dirname(__file__), "../../../data_generator/ready/country_states.json")

# ✅ Continent mapping (using your preferred format)
continent_mapping = {
    # 🌍 Africa
    "Algeria": "Africa", "Angola": "Africa", "Benin": "Africa", "Botswana": "Africa", "Burkina Faso": "Africa",
    "Burundi": "Africa", "Cabo Verde": "Africa", "Cameroon": "Africa", "Central African Republic": "Africa",
    "Chad": "Africa", "Comoros": "Africa", "Congo": "Africa", "Congo, The Democratic Republic of the": "Africa",
    "Côte d'Ivoire": "Africa", "Djibouti": "Africa", "Egypt": "Africa", "Equatorial Guinea": "Africa",
    "Eritrea": "Africa", "Eswatini": "Africa", "Ethiopia": "Africa", "Gabon": "Africa", "Gambia": "Africa",
    "Ghana": "Africa", "Guinea": "Africa", "Guinea-Bissau": "Africa", "Kenya": "Africa", "Lesotho": "Africa",
    "Liberia": "Africa", "Libya": "Africa", "Madagascar": "Africa", "Malawi": "Africa", "Mali": "Africa",
    "Mauritania": "Africa", "Mauritius": "Africa", "Morocco": "Africa", "Mozambique": "Africa", "Namibia": "Africa",
    "Niger": "Africa", "Nigeria": "Africa", "Rwanda": "Africa", "Sao Tome and Principe": "Africa",
    "Senegal": "Africa", "Seychelles": "Africa", "Sierra Leone": "Africa", "Somalia": "Africa", "South Africa": "Africa",
    "South Sudan": "Africa", "Sudan": "Africa", "Tanzania": "Africa", "Togo": "Africa", "Tunisia": "Africa",
    "Uganda": "Africa", "Zambia": "Africa", "Zimbabwe": "Africa", "Western Sahara": "Africa",

    # 🌏 Asia
    "Afghanistan": "Asia", "Armenia": "Asia", "Azerbaijan": "Asia", "Bahrain": "Asia", "Bangladesh": "Asia",
    "Bhutan": "Asia", "Brunei Darussalam": "Asia", "Cambodia": "Asia", "China": "Asia", "Cyprus": "Asia",
    "Georgia": "Asia", "Hong Kong": "Asia", "India": "Asia", "Indonesia": "Asia", "Iran, Islamic Republic of": "Asia",
    "Iraq": "Asia", "Israel": "Asia", "Japan": "Asia", "Jordan": "Asia", "Kazakhstan": "Asia", "Kuwait": "Asia",
    "Kyrgyzstan": "Asia", "Lao People's Democratic Republic": "Asia", "Lebanon": "Asia", "Malaysia": "Asia",
    "Maldives": "Asia", "Mongolia": "Asia", "Myanmar (Burma)": "Asia", "Nepal": "Asia", "North Korea": "Asia",
    "Oman": "Asia", "Pakistan": "Asia", "Palestine": "Asia", "Philippines": "Asia", "Qatar": "Asia",
    "Saudi Arabia": "Asia", "Singapore": "Asia", "South Korea": "Asia", "Sri Lanka": "Asia", "Syria": "Asia",
    "Taiwan": "Asia", "Tajikistan": "Asia", "Thailand": "Asia", "Timor-Leste": "Asia", "Turkey": "Asia",
    "Turkmenistan": "Asia", "United Arab Emirates": "Asia", "Uzbekistan": "Asia", "Vietnam": "Asia", "Yemen": "Asia",

    # 🌍 Europe
    "Albania": "Europe", "Andorra": "Europe", "Austria": "Europe", "Belarus": "Europe", "Belgium": "Europe",
    "Bosnia and Herzegovina": "Europe", "Bulgaria": "Europe", "Croatia": "Europe", "Czechia": "Europe",
    "Denmark": "Europe", "Estonia": "Europe", "Finland": "Europe", "France": "Europe", "Germany": "Europe",
    "Gibraltar": "Europe", "Greece": "Europe", "Hungary": "Europe", "Iceland": "Europe", "Ireland": "Europe",
    "Isle of Man": "Europe", "Italy": "Europe", "Jersey": "Europe", "Kosovo": "Europe", "Latvia": "Europe",
    "Liechtenstein": "Europe", "Lithuania": "Europe", "Luxembourg": "Europe", "Malta": "Europe",
    "Moldova": "Europe", "Monaco": "Europe", "Montenegro": "Europe", "Netherlands": "Europe",
    "North Macedonia": "Europe", "Norway": "Europe", "Poland": "Europe", "Portugal": "Europe",
    "Romania": "Europe", "Russia": "Europe", "San Marino": "Europe", "Serbia": "Europe", "Slovakia": "Europe",
    "Slovenia": "Europe", "Spain": "Europe", "Sweden": "Europe", "Switzerland": "Europe", "Ukraine": "Europe",
    "United Kingdom": "Europe", "Vatican City": "Europe", "Åland Islands": "Europe", "Faroe Islands": "Europe",
    "Guernsey": "Europe", "Georgia": "Europe", "Armenia": "Europe",

    # 🌎 North America
    "Antigua and Barbuda": "North America", "Bahamas": "North America", "Barbados": "North America",
    "Belize": "North America", "Canada": "North America", "Costa Rica": "North America", "Cuba": "North America",
    "Dominica": "North America", "Dominican Republic": "North America", "El Salvador": "North America",
    "Greenland": "North America", "Grenada": "North America", "Guadeloupe": "North America",
    "Guatemala": "North America", "Haiti": "North America", "Honduras": "North America", "Jamaica": "North America",
    "Mexico": "North America", "Nicaragua": "North America", "Panama": "North America", "Saint Kitts and Nevis": "North America",
    "Saint Lucia": "North America", "Saint Vincent and the Grenadines": "North America", "Trinidad and Tobago": "North America",
    "United States": "North America", "Anguilla": "North America", "Bermuda": "North America",
    "Cayman Islands": "North America",

    # 🌎 South America
    "Argentina": "South America", "Bolivia, Plurinational State of": "South America", "Brazil": "South America",
    "Chile": "South America", "Colombia": "South America", "Ecuador": "South America", "French Guiana": "South America",
    "Guyana": "South America", "Paraguay": "South America", "Peru": "South America", "Suriname": "South America",
    "Uruguay": "South America", "Venezuela": "South America",

    # 🌏 Oceania
    "Australia": "Oceania", "Fiji": "Oceania", "Kiribati": "Oceania", "Marshall Islands": "Oceania",
    "Micronesia, Federated States of": "Oceania", "Nauru": "Oceania", "New Zealand": "Oceania", "Palau": "Oceania",
    "Papua New Guinea": "Oceania", "Samoa": "Oceania", "Solomon Islands": "Oceania", "Tonga": "Oceania",
    "Tuvalu": "Oceania", "Vanuatu": "Oceania", "Cook Islands": "Oceania", "Christmas Island": "Oceania",
    "Cocos (Keeling) Islands": "Oceania", "American Samoa": "Oceania", "Guam": "Oceania",

    # ❄ Antarctica & Territories
    "Antarctica": "Antarctica", "Bouvet Island": "Antarctica",
    "Heard Island and McDonald Islands": "Antarctica", "French Southern Territories": "Antarctica"
}
continent_mapping.update(skipped_country_continent_mapping)

country_name_map = {
    "Bolivia, Plurinational State of": "Bolivia",
    "Brunei Darussalam": "Brunei",
    "Congo, The Democratic Republic of the": "Democratic Republic of the Congo",
    "Micronesia, Federated States of": "Micronesia",
    "Iran, Islamic Republic of": "Iran",
    "Korea, Republic of": "South Korea",
    "Lao People's Democratic Republic": "Laos",
    "Moldova, Republic of": "Moldova",
    "Korea, Democratic People's Republic of": "North Korea",
    "Russian Federation": "Russia",
    "Eswatini": "Switzerland",  # Depending on your DB, though Eswatini is the new name
    "Syrian Arab Republic": "Syria",
    "Taiwan, Province of China": "Taiwan",
    "Tanzania, United Republic of": "Tanzania",
    "United States": "United States of America",
    "Holy See (Vatican City State)": "Vatican City",
    "Venezuela, Bolivarian Republic of": "Venezuela",
    "Virgin Islands, British": "British Virgin Islands",
    "Virgin Islands, U.S.": "United States Virgin Islands",
    "Viet Nam": "Vietnam",
}

def get_continent(country_name):
    """ Match country to its continent using direct dictionary lookup """
    return continent_mapping.get(country_name, None)  # ✅ Returns `None` if not found

class Command(BaseCommand):
    help = "Populate states with correct country and continent mappings"

    def handle(self, *args, **kwargs):
        """ Populate states while ensuring every country has a valid continent """
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)

            total_states = 0
            skipped_countries = []

            for country_name, states in data.items():
                normalized_name = country_name_map.get(country_name, country_name)
                continent_name = get_continent(country_name)

                if not continent_name:
                    skipped_countries.append(country_name)
                    continue

                country_obj = Country.objects.filter(name=normalized_name).first()
                if not country_obj:
                    skipped_countries.append(country_name)
                    continue

                for state in states:
                    state_name = state["name"]
                    state_id = state["id"]

                    # 🔡 Generate state code from country code and cleaned state name
                    country_code = country_obj.code.upper()
                    state_code_raw = state_name.strip().replace(" ", "").replace("-", "")
                    state_code = f"{country_code}-{state_code_raw.upper()[:6]}"

                    # ✅ Create state with ID, name, country, and generated code
                    _, created = State.objects.get_or_create(
                        id=state_id,
                        defaults={
                            "name": state_name,
                            "country": country_obj,
                            "code": state_code,
                        }
                    )

                    if created:
                        total_states += 1

                        # ⏱ Progress log every 100 states added
                        if total_states % 100 == 0:
                            self.stdout.write(f"🔄 Added {total_states} states so far...")

            self.stdout.write(self.style.SUCCESS(f"\n✅ Successfully populated {total_states} states!"))

            if skipped_countries:
                self.stderr.write(f"\n⚠️ Skipped {len(skipped_countries)} countries due to missing mappings or missing countries in DB.")
                for country in skipped_countries:
                    self.stderr.write(f"- {country}")

        except Exception as e:
            self.stderr.write(f"❌ Error populating states: {e}")
