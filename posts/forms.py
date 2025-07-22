# forms.py 
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import Post, SocialMediaHandle
from .mixins import ImageFieldsMixin, LocationFieldsSetupMixin  # <-- import your mixins here
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from .models import SocialMediaHandle
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback

# forms.py

class ProductPostForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = Post
        fields = [
            'availability_scope',
            "product_name", "description", "author_phone_number", "author_email",
            "post_continent", "post_continent_input", "post_country", "post_country_input",
            "post_state", "post_state_input", "post_town", "post_town_input",
            "brand", "condition",          
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels and placeholders
        self.fields['product_name'].label = "Name of the product you're selling"
        self.fields['product_name'].widget.attrs['placeholder'] = "E.g., iPhone 13, Samsung TV, Hammer, Jeans..."

        self.fields['description'].label = "Describe this product in detail (Very Important)"
        self.fields['description'].widget.attrs['placeholder'] = "Buyers need full details to decide. Describe condition, specs, etc."

        self.fields['author_email'].label = "Your email address"
        self.fields['author_email'].widget.attrs['placeholder'] = "e.g., you@example.com"

        self.fields['author_phone_number'].label = "Your phone number"
        self.fields['author_phone_number'].widget.attrs['placeholder'] = "e.g., +1234567890"

        self.fields['brand'].label = "Brand name (optional)"
        self.fields['brand'].widget.attrs['placeholder'] = "E.g., Apple, Samsung, Nike, etc."
    
        self.fields['condition'].label = "Condition of the product"
        self.fields['condition'].widget.attrs['placeholder'] = "E.g., New, Fairly used, Broken"

        # Initialize reusable mixins
        self.init_image_labels()
        self.init_location_labels_and_placeholders()

    def clean(self):
        cleaned_data = super().clean()
        return apply_location_scope_fallback(cleaned_data, self)
    def save(self, commit=True):
        instance = super().save(commit=False)
        assign_location_fields(self)  # manually inject location fields from cleaned_data to model instance

        if commit:
            instance.save()
        return instance


# Service-specific post form
class ServicePostForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = Post
        fields = [
            'availability_scope',
            "product_name", "description", "author_phone_number", "author_email",
            "post_continent", "post_continent_input", "post_country", "post_country_input",
            "post_state", "post_state_input", "post_town", "post_town_input",
            "service_details", "qualifications", "availability_schedule", "service_guarantees",          
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['product_name'].label = "What services are you offering?"
        self.fields['product_name'].widget.attrs['placeholder'] = "E.g., Guitar, Watches, iPhone 13, Dumbells, Pots..."

        self.fields['description'].label = "Describe your services to a buyer (Very Important)"
        self.fields['description'].widget.attrs['placeholder'] = (
            "The descriptions you provide helps potential buyers..."
        )

        self.fields['author_email'].label = "Your email address"
        self.fields['author_email'].widget.attrs['placeholder'] = "e.g., you@example.com"

        self.fields['author_phone_number'].label = "Your phone number"
        self.fields['author_phone_number'].widget.attrs['placeholder'] = "e.g., +1234567890"

        self.fields['service_details'].label = "Do you offer outdoor services (Home services)"
        self.fields['service_details'].widget.attrs['placeholder'] = "Enter brand name"

        self.fields['qualifications'].label = "Tell buyers your qualification (optional)"
        self.fields['qualifications'].widget.attrs['placeholder'] = "E.g., Certified Electrician"

        self.fields['availability_schedule'].label = "Time"
        self.fields['availability_schedule'].widget.attrs['placeholder'] = "active times"

        self.fields['service_guarantees'].label = "Give buyers guarantees (optional)"
        self.fields['service_guarantees'].widget.attrs['placeholder'] = "Enter guarantees if any"

        self.init_image_labels()
        self.init_location_labels_and_placeholders()

    def clean(self):
        cleaned_data = super().clean()
        return apply_location_scope_fallback(cleaned_data, self)
    def save(self, commit=True):
        instance = super().save(commit=False)
        assign_location_fields(self)  # manually inject location fields from cleaned_data to model instance

        if commit:
            instance.save()
        return instance
    

# Labor-specific post form
class LaborPostForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = Post
        fields = [
            'availability_scope',
            "product_name", "description", "author_phone_number", "author_email",
            "post_continent", "post_continent_input", "post_country", "post_country_input",
            "post_state", "post_state_input", "post_town", "post_town_input",
            "labor_experience_years",          
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['product_name'].label = "What labor work do you do"
        self.fields['product_name'].widget.attrs['placeholder'] = "E.g., Plumbing, Carpentry, Welding..."

        self.fields['description'].label = "Give a brief description to the buyer about what labor you do (Very Important)"
        self.fields['description'].widget.attrs['placeholder'] = "The descriptions you provide help potential buyers reach you faster"

        self.fields['author_email'].label = "Your email address"
        self.fields['author_email'].widget.attrs['placeholder'] = "e.g., you@example.com"

        self.fields['author_phone_number'].label = "Your phone number"
        self.fields['author_phone_number'].widget.attrs['placeholder'] = "e.g., +1234567890"

        self.fields['labor_experience_years'].label = "Years of experience (optional)"
        self.fields['labor_experience_years'].widget.attrs['placeholder'] = "E.g., 3"

        self.init_image_labels()
        self.init_location_labels_and_placeholders()
        self.init_location_queryset() 
    def clean(self):
        cleaned_data = super().clean()
        return apply_location_scope_fallback(cleaned_data, self)
    def save(self, commit=True):
        instance = super().save(commit=False)
        assign_location_fields(self)  # manually inject location fields from cleaned_data to model instance

        if commit:
            instance.save()
        return instance


# Social Media Handle Form (unchanged)
class SocialMediaHandleForm(forms.ModelForm):
    url_validator = URLValidator()

    class Meta:
        model = SocialMediaHandle
        fields = [
            'linkedin', 'twitter', 'youtube', 'instagram',
            'facebook', 'whatsapp', 'website'
        ]
        widgets = {
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://x.com/username'}),
            'youtube': forms.URLInput(attrs={'placeholder': 'https://youtube.com/channel/...'}),
            'instagram': forms.URLInput(attrs={'placeholder': 'https://instagram.com/username'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/username'}),
            'whatsapp': forms.URLInput(attrs={'placeholder': 'https://wa.me/1234567890'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourbusiness.com'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.fields:
            url = cleaned_data.get(field_name)
            if url:
                try:
                    self.url_validator(url)
                except ValidationError:
                    self.add_error(
                        field_name,
                        f"Invalid URL provided for {field_name}. Please use a valid format starting with https://"
                    )
        return cleaned_data