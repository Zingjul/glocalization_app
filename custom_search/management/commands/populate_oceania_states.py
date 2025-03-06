import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.core.management.base import BaseCommand
from custom_search.models import Country, State

class Command(BaseCommand):
    help = 'Populates North American states/provinces (Saint Vincent and the Grenadines to United States)'

    def handle(self, *args, **options):
        self.populate_saint_vincent_and_the_grenadines()
        self.populate_trinidad_and_tobago()
        self.populate_united_states()

    def populate_saint_vincent_and_the_grenadines(self):
        try:
            country = Country.objects.get(country_code='VC')
        except Country.DoesNotExist:
            self.stdout.write(self.style.ERROR('Saint Vincent and the Grenadines not found.'))
            return
        states = ['Charlotte', 'Grenadines', 'Saint Andrew', 'Saint David', 'Saint George', 'Saint Patrick']
        for state in states:
            State.objects.get_or_create(name=state, country=country)
            self.stdout.write(self.style.SUCCESS(f'Added Saint Vincent and the Grenadines state: {state}'))

    def populate_trinidad_and_tobago(self):
        try:
            country = Country.objects.get(country_code='TT')
        except Country.DoesNotExist:
            self.stdout.write(self.style.ERROR('Trinidad and Tobago not found.'))
            return
        states = ['Arima', 'Chaguanas', 'Couva-Tabaquite-Talparo', 'Diego Martin', 'Eastern Tobago', 'Penal-Debe', 'Point Fortin', 'Port of Spain', 'Princes Town', 'San Fernando', 'San Juan-Laventille', 'Sangre Grande', 'Siparia', 'Southwest Tobago', 'Tunapuna-Piarco']
        for state in states:
            State.objects.get_or_create(name=state, country=country)
            self.stdout.write(self.style.SUCCESS(f'Added Trinidad and Tobago state: {state}'))

    def populate_united_states(self):
        try:
            country = Country.objects.get(country_code='US')
        except Country.DoesNotExist:
            self.stdout.write(self.style.ERROR('United States not found.'))
            return
        states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
        for state in states:
            State.objects.get_or_create(name=state, country=country)
            self.stdout.write(self.style.SUCCESS(f'Added United States state: {state}'))
