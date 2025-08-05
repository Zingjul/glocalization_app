from django import forms
from .models import Continent, Country, State, Town

class CustomSearchForm(forms.Form):
    query = forms.CharField(
        label='Search',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter search keyword'})
    )
    continent = forms.ModelChoiceField(
        queryset=Continent.objects.all(),
        required=False,
        empty_label="Select Continent",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.none(),
        required=False,
        empty_label="Select Country",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.none(),
        required=False,
        empty_label="Select State",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    town = forms.ModelChoiceField(
        queryset=Town.objects.none(),
        required=False,
        empty_label="Select Town",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'continent' in self.data:
            continent_id = self.data.get('continent')
            self.fields['country'].queryset = Country.objects.filter(continent_id=continent_id)

        if 'country' in self.data:
            country_id = self.data.get('country')
            self.fields['state'].queryset = State.objects.filter(country_id=country_id)

        if 'state' in self.data:
            state_id = self.data.get('state')
            self.fields['town'].queryset = Town.objects.filter(state_id=state_id)

    def clean_query(self):
        query = self.cleaned_data.get("query")
        if query and len(query.strip()) < 3:
            raise forms.ValidationError("Search query must be at least 3 characters long.")
        return query
