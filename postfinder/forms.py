# postfinder/forms.py
from django import forms
from custom_search.models import Continent, Country, State, Town

class PostFinderFilterForm(forms.Form):
    AVAILABILITY_SCOPE_CHOICES = [
        ("continent", "Continent"),
        ("country", "Country"),
        ("state", "State"),
        ("town", "Town"),
    ]

    availability_scope = forms.ChoiceField(
        choices=AVAILABILITY_SCOPE_CHOICES,
        required=True,
        label="Filter by Scope"
    )

    continent = forms.ModelChoiceField(
        queryset=Continent.objects.all().order_by("name"),
        required=False,
        label="Continent"
    )

    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by("name"),
        required=False,
        label="Country"
    )

    state = forms.ModelChoiceField(
        queryset=State.objects.all().order_by("name"),
        required=False,
        label="State"
    )

    town = forms.ModelChoiceField(
        queryset=Town.objects.all().order_by("name"),
        required=False,
        label="Town"
    )

    def clean(self):
        """
        Validate that the user filled in the correct hierarchy
        depending on the chosen availability_scope.
        """
        cleaned_data = super().clean()
        scope = cleaned_data.get("availability_scope")

        if scope == "continent" and not cleaned_data.get("continent"):
            self.add_error("continent", "Please select a continent.")

        elif scope == "country":
            if not cleaned_data.get("continent"):
                self.add_error("continent", "Please select a continent.")
            if not cleaned_data.get("country"):
                self.add_error("country", "Please select a country.")

        elif scope == "state":
            if not cleaned_data.get("continent"):
                self.add_error("continent", "Please select a continent.")
            if not cleaned_data.get("country"):
                self.add_error("country", "Please select a country.")
            if not cleaned_data.get("state"):
                self.add_error("state", "Please select a state.")

        elif scope == "town":
            if not cleaned_data.get("continent"):
                self.add_error("continent", "Please select a continent.")
            if not cleaned_data.get("country"):
                self.add_error("country", "Please select a country.")
            if not cleaned_data.get("state"):
                self.add_error("state", "Please select a state.")
            if not cleaned_data.get("town"):
                self.add_error("town", "Please select a town.")

        return cleaned_data
