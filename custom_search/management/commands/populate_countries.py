import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')  # Replace with your project's settings module
django.setup()

from django.core.management.base import BaseCommand
from custom_search.models import Continent, Country
from django_countries import countries

class Command(BaseCommand):
    help = 'Populates countries from django-countries'

    def handle(self, *args, **options):
        for country_code, country_name in list(countries):
            print(f"Processing: {country_code} - {country_name}") # added print statement
            continent_name = self.get_continent(country_code)
            print(f"Continent name: {continent_name}") # added print statement

            if continent_name:
                try:
                    continent = Continent.objects.get(name=continent_name)
                    try:
                        Country.objects.get_or_create(country_code=country_code, defaults={'name': country_name, 'continent': continent})
                        self.stdout.write(self.style.SUCCESS(f'Added country: {country_name}'),)
                    except Exception as country_error:
                        self.stdout.write(self.style.ERROR(f"Error creating country {country_name}: {country_error}"),)
                except Continent.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Continent {continent_name} does not exist for country {country_name}'),)
                except Exception as continent_error:
                    self.stdout.write(self.style.ERROR(f"Error getting continent {continent_name}: {continent_error}"),)
            else:
                self.stdout.write(self.style.ERROR(f"Continent not found for country: {country_name}"),)

    def get_continent(self, country_code):
        continent_mapping = {
            'AF': 'Asia',  # Afghanistan
            'AL': 'Europe',  # Albania
            'DZ': 'Africa',  # Algeria
            'AS': 'Australia',  # American Samoa
            'AD': 'Europe',  # Andorra
            'AO': 'Africa',  # Angola
            'AI': 'North America',  # Anguilla
            'AQ': 'Antarctica',  # Antarctica
            'AG': 'North America',  # Antigua and Barbuda
            'AR': 'South America',  # Argentina
            'AM': 'Asia',  # Armenia
            'AW': 'North America',  # Aruba
            'AU': 'Australia',  # Australia
            'AT': 'Europe',  # Austria
            'AZ': 'Asia',  # Azerbaijan
            'BS': 'North America',  # Bahamas
            'BH': 'Asia',  # Bahrain
            'BD': 'Asia',  # Bangladesh
            'BB': 'North America',  # Barbados
            'BY': 'Europe',  # Belarus
            'BE': 'Europe',  # Belgium
            'BZ': 'North America',  # Belize
            'BJ': 'Africa',  # Benin
            'BM': 'North America',  # Bermuda
            'BT': 'Asia',  # Bhutan
            'BO': 'South America',  # Bolivia
            'BA': 'Europe',  # Bosnia and Herzegovina
            'BW': 'Africa',  # Botswana
            'BV': 'Antarctica',  # Bouvet Island
            'BR': 'South America',  # Brazil
            'IO': 'Asia',  # British Indian Ocean Territory
            'BN': 'Asia',  # Brunei Darussalam
            'BG': 'Europe',  # Bulgaria
            'BF': 'Africa',  # Burkina Faso
            'BI': 'Africa',  # Burundi
            'KH': 'Asia',  # Cambodia
            'CM': 'Africa',  # Cameroon
            'CA': 'North America',  # Canada
            'CV': 'Africa',  # Cape Verde
            'KY': 'North America',  # Cayman Islands
            'CF': 'Africa',  # Central African Republic
            'TD': 'Africa',  # Chad
            'CL': 'South America',  # Chile
            'CN': 'Asia',  # China
            'CX': 'Australia',  # Christmas Island
            'CC': 'Australia',  # Cocos (Keeling) Islands
            'CO': 'South America',  # Colombia
            'KM': 'Africa',  # Comoros
            'CG': 'Africa',  # Congo
            'CD': 'Africa',  # Congo, The Democratic Republic of the
            'CK': 'Australia',  # Cook Islands
            'CR': 'North America',  # Costa Rica
            'CI': 'Africa',  # Cote D'Ivoire
            'HR': 'Europe',  # Croatia
            'CU': 'North America',  # Cuba
            'CY': 'Asia',  # Cyprus
            'CZ': 'Europe',  # Czech Republic
            'DK': 'Europe',  # Denmark
            'DJ': 'Africa',  # Djibouti
            'DM': 'North America',  # Dominica
            'DO': 'North America',  # Dominican Republic
            'EC': 'South America',  # Ecuador
            'EG': 'Africa',  # Egypt
            'SV': 'North America',  # El Salvador
            'GQ': 'Africa',  # Equatorial Guinea
            'ER': 'Africa',  # Eritrea
            'EE': 'Europe',  # Estonia
            'ET': 'Africa',  # Ethiopia
            'FK': 'South America',  # Falkland Islands (Malvinas)
            'FO': 'Europe',  # Faroe Islands
            'FJ': 'Australia',  # Fiji
            'FI': 'Europe',  # Finland
            'FR': 'Europe',  # France
            'GF': 'South America',  # French Guiana
            'PF': 'Australia',  # French Polynesia
            'TF': 'Antarctica',  # French Southern Territories
            'GA': 'Africa',  # Gabon
            'GM': 'Africa',  # Gambia
            'GE': 'Asia',  # Georgia
            'DE': 'Europe',  # Germany
            'GH': 'Africa',  # Ghana
            'GI': 'Europe',  # Gibraltar
            'GR': 'Europe',  # Greece
            'GL': 'North America',  # Greenland
            'GD': 'North America',  # Grenada
            'GP': 'North America',  # Guadeloupe
            'GU': 'Australia',  # Guam
            'GT': 'North America',  # Guatemala
            'GG': 'Europe',  # Guernsey
            'GN': 'Africa',  # Guinea
            'GW': 'Africa',  # Guinea-Bissau
            'GY': 'South America',  # Guyana
            'HT': 'North America',  # Haiti
            'HM': 'Antarctica',  # Heard Island and McDonald Islands
            'VA': 'Europe',  # Holy See (Vatican City State)
            'HN': 'North America',  # Honduras
            'HK': 'Asia',  # Hong Kong
            'HU': 'Europe',  # Hungary
            'IS': 'Europe',  # Iceland
            'IN': 'Asia',  # India
            'ID': 'Asia',  # Indonesia
            'IR': 'Asia',  # Iran, Islamic Republic of
            'IQ': 'Asia',  # Iraq
            'IE': 'Europe',  # Ireland
            'IM': 'Europe',  # Isle of Man
            'IL': 'Asia',  # Israel
            'IT': 'Europe',  # Italy
            'JM': 'North America',  # Jamaica
            'JP': 'Asia',  # Japan
            'JE': 'Europe',  # Jersey
            'JO': 'Asia',  # Jordan
            'KZ': 'Asia',  # Kazakhstan
            'KE': 'Africa',  # Kenya
            'KI': 'Australia',  # Kiribati
            'KP': 'Asia',  # Korea, Democratic People's Republic of
            'KR': 'Asia',  # Korea, Republic of
            'KW': 'Asia',  # Kuwait
            'KG': 'Asia',  # Kyrgyzstan
            'LA': 'Asia',  # Lao People's Democratic Republic
            'LV': 'Europe',  # Latvia
            'LB': 'Asia',  # Lebanon
            'LS': 'Africa',  # Lesotho
            'LR': 'Africa',  # Liberia
            'LY': 'Africa',  # Libyan Arab Jamahiriya
            'LI': 'Europe',  # Liechtenstein
            'LT': 'Europe',  # Lithuania
            'LU': 'Europe',  # Luxembourg
            'MO': 'Asia',  # Macao
            'MK': 'Europe',  # Macedonia, The Former Yugoslav Republic of
            'MG': 'Africa',  # Madagascar
            'MW': 'Africa',  # Malawi
            'MY': 'Asia',  # Malaysia
            'MV': 'Asia',  # Maldives
            'ML': 'Africa',  # Mali
            'MT': 'Europe',  # Malta
            'MH': 'Australia',  # Marshall Islands
            'MQ': 'North America',  # Martinique
            'MR': 'Africa',  # Mauritania
            'MU': 'Africa',  # Mauritius
            'YT': 'Africa',  # Mayotte
            'MX': 'North America',  # Mexico
            'FM': 'Australia',  # Micronesia, Federated States of
            'MD': 'Europe',  # Moldova, Republic of
            'MC': 'Europe',  # Monaco
            'MN': 'Asia',  # Mongolia
            'MS': 'North America',  # Montserrat
            'MA': 'Africa',  # Morocco
            'MZ': 'Africa',  # Mozambique
            'MM': 'Asia',  # Myanmar
            'NA': 'Africa',  # Namibia
            'NR': 'Australia',  # Nauru
            'NP': 'Asia',  # Nepal
            'NL': 'Europe',  # Netherlands
            'AN': 'North America',  # Netherlands Antilles
            'NC': 'Australia',  # New Caledonia
            'NZ': 'Australia',  # New Zealand
            'NI': 'North America',  # Nicaragua
            'NE': 'Africa',  # Niger
            'NG': 'Africa',  # Nigeria
            'NU': 'Australia',  # Niue
            'NF': 'Australia',  # Norfolk Island
            'MP': 'Australia',  # Northern Mariana Islands
            'NO': 'Europe',  # Norway
            'OM': 'Asia',  # Oman
            'PK': 'Asia',  # Pakistan
            'PW': 'Australia',  # Palau
            'PS': 'Asia',  # Palestinian Territory, Occupied
            'PA': 'North America',  # Panama
            'PG': 'Australia',  # Papua New Guinea
            'PY': 'South America',  # Paraguay
            'PE': 'South America',  # Peru
            'PH': 'Asia',  # Philippines
            'PN': 'Australia',  # Pitcairn
            'PL': 'Europe',  # Poland
            'PT': 'Europe',  # Portugal
            'PR': 'North America',  # Puerto Rico
            'QA': 'Asia',  # Qatar
            'RE': 'Africa',  # Reunion
            'RO': 'Europe',  # Romania
            'RU': 'Europe',  # Russian Federation
            'RW': 'Africa',  # Rwanda
            'SH': 'Africa',  # Saint Helena
            'KN': 'North America',  # Saint Kitts and Nevis
            'LC': 'North America',  # Saint Lucia
            'PM': 'North America',  # Saint Pierre and Miquelon
            'VC': 'North America',  # Saint Vincent and the Grenadines
            'WS': 'Australia',  # Samoa
            'SM': 'Europe',  # San Marino
            'ST': 'Africa',  # Sao Tome and Principe
            'SA': 'Asia',  # Saudi Arabia
            'SN': 'Africa',  # Senegal
            'CS': 'Europe',  # Serbia and Montenegro
            'SC': 'Africa',  # Seychelles
            'SL': 'Africa',  # Sierra Leone
            'SG': 'Asia',  # Singapore
            'SK': 'Europe',  # Slovakia
            'SI': 'Europe',  # Slovenia
            'SB': 'Australia',  # Solomon Islands
            'SO': 'Africa',  # Somalia
            'ZA': 'Africa',  # South Africa
            'GS': 'Antarctica',  # South Georgia and the South Sandwich Islands
            'ES': 'Europe',  # Spain
            'LK': 'Asia',  # Sri Lanka
            'SD': 'Africa',  # Sudan
            'SR': 'South America',  # Suriname
            'SJ': 'Europe',  # Svalbard and Jan Mayen
            'SZ': 'Africa',  # Swaziland
            'SE': 'Europe',  # Sweden
            'CH': 'Europe',  # Switzerland
            'SY': 'Asia',  # Syrian Arab Republic
            'TW': 'Asia',  # Taiwan, Province of China
            'TJ': 'Asia',  # Tajikistan
            'TZ': 'Africa',  # Tanzania, United Republic of
            'TH': 'Asia',  # Thailand
            'TL': 'Asia',  # Timor-Leste
            'TG': 'Africa',  # Togo
            'TK': 'Australia',  # Tokelau
            'TO': 'Australia',  # Tonga
            'TT': 'North America',  # Trinidad and Tobago
            'TN': 'Africa',  # Tunisia
            'TR': 'Asia',  # Turkey
            'TM': 'Asia',  # Turkmenistan
            'TC': 'North America',  # Turks and Caicos Islands
            'TV': 'Australia',  # Tuvalu
            'UG': 'Africa',  # Uganda
            'UA': 'Europe',  # Ukraine
            'AE': 'Asia',  # United Arab Emirates
            'GB': 'Europe',  # United Kingdom
            'US': 'North America',  # United States
            'UM': 'Australia',  # United States Minor Outlying Islands
            'UY': 'South America',  # Uruguay
            'UZ': 'Asia',  # Uzbekistan
            'VU': 'Australia',  # Vanuatu
            'VE': 'South America',  # Venezuela
            'VN': 'Asia',  # Viet Nam
            'VG': 'North America',  # Virgin Islands, British
            'VI': 'North America',  # Virgin Islands, U.S.
            'WF': 'Australia',  # Wallis and Futuna
            'EH': 'Africa',  # Western Sahara
            'YE': 'Asia',  # Yemen
            'ZM': 'Africa',  # Zambia
            'ZW': 'Africa',  # Zimbabwe
        }
        return continent_mapping.get(country_code)