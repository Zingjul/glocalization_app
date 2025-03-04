from django import forms
from .models import Continent, Country, State, Town

class CustomSearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255, required=False)
    continent = forms.ModelChoiceField(queryset=Continent.objects.all(), required=False, empty_label="Select Continent")
    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, empty_label="Select Country")
    state = forms.ModelChoiceField(queryset=State.objects.all(), required=False, empty_label="Select State")
    town = forms.ModelChoiceField(queryset=Town.objects.all(), required=False, empty_label="Select Town")