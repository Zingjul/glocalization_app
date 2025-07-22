from django import forms
from django.core.exceptions import ValidationError
from PIL import Image  # Optional — for validating image dimensions

class ImageFieldsMixin:
    image1 = forms.ImageField(required=False)
    image2 = forms.ImageField(required=False)
    image3 = forms.ImageField(required=False)
    image4 = forms.ImageField(required=False)
    image5 = forms.ImageField(required=False)
    image6 = forms.ImageField(required=False)

    image_fields = ['image1', 'image2', 'image3', 'image4', 'image5', 'image6']
    max_file_size_mb = 5  # Adjust if needed

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
                field_name: f"Image file too large (>{self.max_file_size_mb}MB). Please upload a smaller file."
            })

        valid_types = ['image/jpeg', 'image/png', 'image/webp']
        if hasattr(image, 'content_type') and image.content_type not in valid_types:
            raise ValidationError({
                field_name: "Invalid format. Use JPEG, PNG, or WEBP only."
            })

        try:
            img = Image.open(image)
            max_width, max_height = 4000, 4000
            if img.width > max_width or img.height > max_height:
                raise ValidationError({
                    field_name: f"Image dimensions too large (max {max_width}x{max_height}px)."
                })
        except Exception:
            raise ValidationError({field_name: "Could not open image. Please upload a valid file."})


class LocationFieldsSetupMixin:
    def init_location_labels_and_placeholders(self):
        fields = [
            ("post_continent", "Tell us what continent you're requesting from", "Or type the continent name here"),
            ("post_country", "Country of your request", "Or type the country name here"),
            ("post_state", "State or province", "Or type the state name here"),
            ("post_town", "Town or local area", "Or type the town name here"),
        ]

        for field_prefix, label, placeholder in fields:
            if field_prefix in self.fields:
                self.fields[field_prefix].label = label
            input_field = f"{field_prefix}_input"
            if input_field in self.fields:
                self.fields[input_field].label = ""
                self.fields[input_field].widget.attrs["placeholder"] = placeholder