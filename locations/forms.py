from django import forms
from .models import Continent, Country, State, Town

class LocationForm(forms.Form):
    continent = forms.ModelChoiceField(queryset=Continent.objects.all(), empty_label="Select Continent")
    country = forms.ModelChoiceField(queryset=Country.objects.none(), empty_label="Select Country", required=False)
    state = forms.ModelChoiceField(queryset=State.objects.none(), empty_label="Select State", required=False)
    town = forms.ModelChoiceField(queryset=Town.objects.none(), empty_label="Select Town", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'continent' in self.data:
            try:
                continent_id = int(self.data.get('continent'))
                self.fields['country'].queryset = Country.objects.filter(continent_id=continent_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Handle invalid continent ID

        if 'country' in self.data:
            try:
                country_id = int(self.data.get('country'))
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Handle invalid country ID

        if 'state' in self.data:
            try:
                state_id = int(self.data.get('state'))
                self.fields['town'].queryset = Town.objects.filter(state_id=state_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Handle invalid state ID