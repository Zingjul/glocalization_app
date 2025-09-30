# seekers/forms/mixins.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image  # Optional: check image dimensions

from custom_search.models import Continent, Country, State, Town
class LocationFieldsSetupMixin:
    def init_location_labels_and_placeholders(self):
        fields = [
            ("post_continent", "Tell buyer what continent are you posting from?", "Or simply enter continent name here"),
            ("post_country", "Tell buyer what country you are posting from", "Or simply enter country name here"),
            ("post_state", "Tell buyer name of state or province you are posting from", "Or simply enter State name here"),
            ("post_town", "Tell buyer the name of the town you are posting from", "Or simply enter Town name here"),
        ]

        for field_prefix, dropdown_label, input_placeholder in fields:
            dropdown_name = field_prefix
            input_name = f"{field_prefix}_input"

            if dropdown_name in self.fields:
                self.fields[dropdown_name].label = dropdown_label
                self.fields[dropdown_name].disabled = False
                self.fields[dropdown_name].widget.attrs.update({
                    "class": "location-field dropdown-field",
                    "id": f"id_{dropdown_name}",
                })

            if input_name in self.fields:
                self.fields[input_name].label = ""
                self.fields[input_name].disabled = False
                self.fields[input_name].widget.attrs.update({
                    "placeholder": input_placeholder,
                    "class": "location-field input-field",
                    "id": f"id_{input_name}",
                })

    def init_location_queryset(self):
        # ⛓ Dynamically filter dropdowns based on parent selection
        data = self.data if hasattr(self, "data") else {}

        if "post_continent" in data:
            continent_id = data.get("post_continent")
            self.fields["post_country"].queryset = Country.objects.filter(
                continent_id=continent_id
            )

        if "post_country" in data:
            country_id = data.get("post_country")
            self.fields["post_state"].queryset = State.objects.filter(
                country_id=country_id
            )

        if "post_state" in data:
            state_id = data.get("post_state")
            self.fields["post_town"].queryset = Town.objects.filter(
                state_id=state_id
            )


