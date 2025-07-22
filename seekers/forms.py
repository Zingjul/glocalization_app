from django import forms
from phonenumber_field.formfields import PhoneNumberField
from .models import SeekerPost, SeekerImage
from .mixins import ImageFieldsMixin, LocationFieldsSetupMixin  # Import same mixins
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback

class ProductSeekerForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = SeekerPost
        fields = [
            "title", "description",
            "availability_scope",
            "post_continent", "post_continent_input",
            "post_country", "post_country_input",
            "post_state", "post_state_input",
            "post_town", "post_town_input",
            "preferred_fulfillment_time",
            "budget",
            "author_phone_number",
            "author_email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Labels and placeholders
        self.fields['title'].label = "What product are you looking for?"
        self.fields['title'].widget.attrs['placeholder'] = "E.g., Fridge, Solar Panel, School Shoes..."

        self.fields['description'].label = "Describe the product or need clearly"
        self.fields['description'].widget.attrs['placeholder'] = "The clearer your request, the better your chances."

        self.fields['preferred_fulfillment_time'].label = "When do you need it fulfilled?"
        self.fields['preferred_fulfillment_time'].widget.attrs['placeholder'] = "e.g. ASAP, next weekend, etc."

        self.fields['budget'].label = "Estimated budget (optional)"
        self.fields['budget'].widget.attrs['placeholder'] = "e.g. 50,000 NGN"

        self.fields['author_email'].label = "Your email address"
        self.fields['author_email'].widget.attrs['placeholder'] = "e.g. you@example.com"

        self.fields['author_phone_number'].label = "Your phone number"
        self.fields['author_phone_number'].widget.attrs['placeholder'] = "e.g. +2348012345678"

        self.init_image_labels()
        self.init_location_labels_and_placeholders()

    def clean(self):
            cleaned_data = super().clean()
            return apply_location_scope_fallback(cleaned_data, self)

class LaborSeekerForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = SeekerPost
        fields = [
            "title", "description",
            "availability_scope",
            "post_continent", "post_continent_input",
            "post_country", "post_country_input",
            "post_state", "post_state_input",
            "post_town", "post_town_input",
            "preferred_fulfillment_time",
            "budget",
            "author_phone_number",
            "author_email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].label = "What labor are you requesting?"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Painter, Plumber, Roofer..."

        self.fields["description"].label = "Describe your labor needs clearly"
        self.fields["description"].widget.attrs["placeholder"] = "Buyers need to understand what task you're requesting."

        self.fields["preferred_fulfillment_time"].label = "Fulfillment time (optional)"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "e.g. next week"

        self.fields["budget"].label = "Estimated budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "e.g. 25,000 NGN"

        self.fields["author_email"].label = "Your email address"
        self.fields["author_email"].widget.attrs["placeholder"] = "e.g. you@example.com"

        self.fields["author_phone_number"].label = "Your phone number"
        self.fields["author_phone_number"].widget.attrs["placeholder"] = "e.g. +2348012345678"

        self.init_image_labels()
        self.init_location_labels_and_placeholders()

    def clean(self):
            cleaned_data = super().clean()
            return apply_location_scope_fallback(cleaned_data, self)

#######################
class ServiceSeekerForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    class Meta:
        model = SeekerPost
        fields = [
            "title", "description",
            "availability_scope",
            "post_continent", "post_continent_input",
            "post_country", "post_country_input",
            "post_state", "post_state_input",
            "post_town", "post_town_input",
            "preferred_fulfillment_time",
            "budget",
            "author_phone_number",
            "author_email",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].label = "What service are you requesting?"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Painter, Plumber, Roofer..."

        self.fields["description"].label = "Describe your labor needs clearly"
        self.fields["description"].widget.attrs["placeholder"] = "Buyers need to understand what task you're requesting."

        self.fields["preferred_fulfillment_time"].label = "Fulfillment time (optional)"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "e.g. next week"

        self.fields["budget"].label = "Estimated budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "e.g. 25,000 NGN"

        self.fields["author_email"].label = "Your email address"
        self.fields["author_email"].widget.attrs["placeholder"] = "e.g. you@example.com"

        self.fields["author_phone_number"].label = "Your phone number"
        self.fields["author_phone_number"].widget.attrs["placeholder"] = "e.g. +2348012345678"

        self.init_image_labels()
        self.init_location_labels_and_placeholders()

    def clean(self):
            cleaned_data = super().clean()
            return apply_location_scope_fallback(cleaned_data, self)

class SeekerImageForm(forms.ModelForm):
    class Meta:
        model = SeekerImage
        fields = ["image"]

SeekerImageFormSet = forms.modelformset_factory(
    SeekerImage,
    form=SeekerImageForm,
    extra=6,
    max_num=6,
    can_delete=True
)
