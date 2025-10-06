# seekersfinder/forms.py
from django import forms
from seekers.models import (
    SeekerContinent,
    SeekerCountry,
    SeekerState,
    SeekerTown,
    SeekerCategory,
)


class SeekerFinderFilterForm(forms.Form):
    AVAILABILITY_SCOPE_CHOICES = [
        ("global", "Global"),
        ("continent", "Continent-wide"),
        ("country", "Country-wide"),
        ("state", "State-wide"),
        ("town", "Town-specific"),
    ]

    availability_scope = forms.ChoiceField(
        choices=AVAILABILITY_SCOPE_CHOICES,
        required=False,
        label="Scope"
    )
    category = forms.ModelChoiceField(
        queryset=SeekerCategory.objects.all(),
        required=False,
        label="Category"
    )
    continent = forms.ModelChoiceField(
        queryset=SeekerContinent.objects.all(),
        required=False,
        label="Continent"
    )
    country = forms.ModelChoiceField(
        queryset=SeekerCountry.objects.all(),
        required=False,
        label="Country"
    )
    state = forms.ModelChoiceField(
        queryset=SeekerState.objects.all(),
        required=False,
        label="State"
    )
    town = forms.ModelChoiceField(
        queryset=SeekerTown.objects.all(),
        required=False,
        label="Town"
    )

    def clean(self):
        """
        Ensure hierarchical consistency:
        - If a country is chosen, a continent must also be chosen.
        - If a state is chosen, a country must also be chosen.
        - If a town is chosen, a state must also be chosen.
        """
        cleaned_data = super().clean()
        continent = cleaned_data.get("continent")
        country = cleaned_data.get("country")
        state = cleaned_data.get("state")
        town = cleaned_data.get("town")

        if country and not continent:
            self.add_error("continent", "Please select a continent when filtering by country.")

        if state and not country:
            self.add_error("country", "Please select a country when filtering by state.")

        if town and not state:
            self.add_error("state", "Please select a state when filtering by town.")

        return cleaned_data
