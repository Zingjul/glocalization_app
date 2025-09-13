# seekers/forms/mixins.py
from django import forms
from django.core.exceptions import ValidationError
from PIL import Image  # Optional: check image dimensions

from seekers.models import (
    SeekerContinent, SeekerCountry, SeekerState, SeekerTown
)


# --- Image Fields Mixin with validation ---
class ImageFieldsMixin:
    image_fields = ['image1', 'image2', 'image3', 'image4', 'image5', 'image6']
    max_file_size_mb = 5  # Size limit (MB)

    def init_image_labels(self):
        labels = [
            "Front view", "Back view", "Right side view",
            "Left side view", "Top view", "Bottom view"
        ]
        for i, field_name in enumerate(self.image_fields):
            if field_name in self.fields:
                self.fields[field_name].label = labels[i]

    def clean(self):
        cleaned_data = super().clean()
        for field in self.image_fields:
            image = cleaned_data.get(field)
            if image:
                self.validate_image(field, image)
        return cleaned_data

    def validate_image(self, field_name, image):
        max_bytes = self.max_file_size_mb * 1024 * 1024
        if image.size > max_bytes:
            raise ValidationError({
                field_name: f"Image file too large (>{self.max_file_size_mb}MB). Please upload a smaller image."
            })

        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in valid_types:
            raise ValidationError({
                field_name: "Only JPEG, PNG, or WEBP image formats are allowed."
            })

        # Optional: check dimensions
        try:
            img = Image.open(image)
            max_width, max_height = 4000, 4000
            if img.width > max_width or img.height > max_height:
                raise ValidationError({
                    field_name: f"Image too large in dimensions (max {max_width}x{max_height}px)."
                })
        except Exception:
            raise ValidationError({field_name: "Invalid image file."})


# --- Location Fields Setup Mixin ---
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
            self.fields["post_country"].queryset = SeekerCountry.objects.filter(
                continent_id=continent_id
            )

        if "post_country" in data:
            country_id = data.get("post_country")
            self.fields["post_state"].queryset = SeekerState.objects.filter(
                country_id=country_id
            )

        if "post_state" in data:
            state_id = data.get("post_state")
            self.fields["post_town"].queryset = SeekerTown.objects.filter(
                state_id=state_id
            )
