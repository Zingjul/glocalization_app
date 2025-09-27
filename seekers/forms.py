# seekers/forms.py
from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from custom_search.models import Continent, Country, State, Town
from .models import (
    SeekerPost,
    SeekerSocialMediaHandle,
)
from .mixins import ImageFieldsMixin, LocationFieldsSetupMixin
from .utils.location_assignment import assign_location_fields  # reuse the posts util if it handles generic location injection
# --- Media forms for SeekerPosts ---
from django.forms import modelformset_factory
from media_app.models import MediaFile



# Base form used by specific seeker forms
class BaseSeekerPostForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    author_phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={"placeholder": "e.g., +1234567890"}),
        required=False
    )

    class Meta:
        model = SeekerPost
        # Only include fields that exist on SeekerPost model
        fields = [
            "availability_scope",
            "business_name",
            "title",
            "description",
            "author_phone_number",
            "author_email",
            "post_continent",
            "post_country",
            "post_state",
            "post_town",
            "post_town_input",
            "preferred_fulfillment_time",
            "budget",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ensure the location dropdowns include any "Unspecified" entries (id=0) if seeded
        self.fields["post_continent"].queryset = Continent.objects.filter(id=0) | Continent.objects.all()
        self.fields["post_country"].queryset = Country.objects.filter(id=0) | Country.objects.all()
        self.fields["post_state"].queryset = State.objects.filter(id=0) | State.objects.all()
        self.fields["post_town"].queryset = Town.objects.filter(id=0) | Town.objects.all()

        # Remove default Django "------" for these select fields
        for f in ("post_continent", "post_country", "post_state", "post_town"):
            if f in self.fields:
                self.fields[f].empty_label = None

        # Default to Unspecified (id=0) if present
        self.fields["post_continent"].initial = Continent.objects.filter(id=0).first()
        self.fields["post_country"].initial = Country.objects.filter(id=0).first()
        self.fields["post_state"].initial = State.objects.filter(id=0).first()
        self.fields["post_town"].initial = Town.objects.filter(id=0).first()

        # Generic labels/placeholders (can be overridden by child forms)
        if "business_name" in self.fields:
            self.fields["business_name"].label = "Business / Organization (optional)"
            self.fields["business_name"].widget.attrs["placeholder"] = "E.g., Acme Ltd."

        self.fields["title"].label = "Title (what are you seeking?)"
        self.fields["title"].widget.attrs["placeholder"] = "Short, clear title (e.g., 'Looking for iPhone 13')"

        self.fields["description"].label = "Description (give details)"
        self.fields["description"].widget.attrs["placeholder"] = "Provide details so sellers can decide quickly."

        self.fields["author_email"].label = "Contact email (optional)"
        self.fields["author_email"].widget.attrs["placeholder"] = "e.g., you@example.com"

        self.fields["author_phone_number"].label = "Contact phone number (optional)"
        self.fields["author_phone_number"].widget.attrs["placeholder"] = "e.g., +1234567890"

        self.fields["preferred_fulfillment_time"].label = "Preferred fulfillment / delivery time (optional)"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "E.g., Within 2 weeks, ASAP"

        self.fields["budget"].label = "Budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "Enter a number, e.g., 15000.00"

        # Initialize mixin helpers
        self.init_image_labels()
        self.init_location_labels_and_placeholders()
        self.init_location_queryset()

    def clean(self):
        cleaned = super().clean()
        scope = cleaned.get("availability_scope")

        unspecified_continent = Continent.objects.filter(id=0).first()
        unspecified_country = Country.objects.filter(id=0).first()
        unspecified_state = State.objects.filter(id=0).first()
        unspecified_town = Town.objects.filter(id=0).first()

        # Apply scope fallback same as posts forms
        if scope == "continent":
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "country":
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "state":
            cleaned["post_town"] = unspecified_town
        elif scope == "town":
            # ✅ If user didn’t select a town (typed instead), fallback
            if not cleaned.get("post_town"):
                cleaned["post_town"] = unspecified_town

        else:  # unspecified or global fallback
            cleaned["post_continent"] = unspecified_continent
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # use existing utility to populate/normalize location-related fields
        try:
            assign_location_fields(self)
        except Exception:
            # don't break saving if assign_location_fields is not available or fails;
            # let the caller handle or log as needed
            pass

        if commit:
            instance.save()
        return instance


# --- Specific seeker forms that mirror the Posts forms but use the SeekerPost fields ---

class ProductSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # product-specific tweaks
        self.fields["title"].label = "Product you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., iPhone 13, Samsung TV"

        self.fields["budget"].label = "Budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "E.g., 15000.00"

    def clean(self):
        cleaned = super().clean()
        scope = cleaned.get("availability_scope")

        unspecified_continent = Continent.objects.filter(id=0).first()
        unspecified_country = Country.objects.filter(id=0).first()
        unspecified_state = State.objects.filter(id=0).first()
        unspecified_town = Town.objects.filter(id=0).first()

        # Apply scope fallback same as posts forms
        if scope == "continent":
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "country":
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "state":
            cleaned["post_town"] = unspecified_town
        elif scope == "town":
            # ✅ If user didn’t select a town (typed instead), fallback
            if not cleaned.get("post_town"):
                cleaned["post_town"] = unspecified_town

        else:  # unspecified or global fallback
            cleaned["post_continent"] = unspecified_continent
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # use existing utility to populate/normalize location-related fields
        try:
            assign_location_fields(self)
        except Exception:
            # don't break saving if assign_location_fields is not available or fails;
            # let the caller handle or log as needed
            pass

        if commit:
            instance.save()
        return instance

class ServiceSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # service-specific tweaks
        self.fields["title"].label = "Service you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Plumbing service, Guitar lessons"

        self.fields["preferred_fulfillment_time"].label = "When do you need the service?"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "E.g., Weekdays, Mornings, ASAP"

    def clean(self):
        cleaned = super().clean()
        scope = cleaned.get("availability_scope")

        unspecified_continent = Continent.objects.filter(id=0).first()
        unspecified_country = Country.objects.filter(id=0).first()
        unspecified_state = State.objects.filter(id=0).first()
        unspecified_town = Town.objects.filter(id=0).first()

        # Apply scope fallback same as posts forms
        if scope == "continent":
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "country":
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "state":
            cleaned["post_town"] = unspecified_town
        elif scope == "town":
            # ✅ If user didn’t select a town (typed instead), fallback
            if not cleaned.get("post_town"):
                cleaned["post_town"] = unspecified_town

        else:  # unspecified or global fallback
            cleaned["post_continent"] = unspecified_continent
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # use existing utility to populate/normalize location-related fields
        try:
            assign_location_fields(self)
        except Exception:
            # don't break saving if assign_location_fields is not available or fails;
            # let the caller handle or log as needed
            pass

        if commit:
            instance.save()
        return instance

class LaborSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # labor-specific tweaks
        self.fields["title"].label = "Labor / Skill you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Electrician, Carpenter"

        self.fields["preferred_fulfillment_time"].label = "Preferred timing (optional)"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "E.g., Immediate, within 3 days"

    def clean(self):
        cleaned = super().clean()
        scope = cleaned.get("availability_scope")

        unspecified_continent = Continent.objects.filter(id=0).first()
        unspecified_country = Country.objects.filter(id=0).first()
        unspecified_state = State.objects.filter(id=0).first()
        unspecified_town = Town.objects.filter(id=0).first()

        # Apply scope fallback same as posts forms
        if scope == "continent":
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "country":
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town
        elif scope == "state":
            cleaned["post_town"] = unspecified_town
        elif scope == "town":
            # ✅ If user didn’t select a town (typed instead), fallback
            if not cleaned.get("post_town"):
                cleaned["post_town"] = unspecified_town

        else:  # unspecified or global fallback
            cleaned["post_continent"] = unspecified_continent
            cleaned["post_country"] = unspecified_country
            cleaned["post_state"] = unspecified_state
            cleaned["post_town"] = unspecified_town

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # use existing utility to populate/normalize location-related fields
        try:
            assign_location_fields(self)
        except Exception:
            # don't break saving if assign_location_fields is not available or fails;
            # let the caller handle or log as needed
            pass

        if commit:
            instance.save()
        return instance

# --- Social Media Handle Form for Seekers ---
class SeekerSocialMediaHandleForm(forms.ModelForm):
    url_validator = URLValidator()

    class Meta:
        model = SeekerSocialMediaHandle
        fields = [
            "linkedin", "twitter", "youtube", "instagram",
            "facebook", "whatsapp", "website"
        ]
        widgets = {
            "linkedin": forms.URLInput(attrs={"placeholder": "https://linkedin.com/in/username"}),
            "twitter": forms.URLInput(attrs={"placeholder": "https://x.com/username"}),
            "youtube": forms.URLInput(attrs={"placeholder": "https://youtube.com/channel/..."}),
            "instagram": forms.URLInput(attrs={"placeholder": "https://instagram.com/username"}),
            "facebook": forms.URLInput(attrs={"placeholder": "https://facebook.com/username"}),
            "whatsapp": forms.URLInput(attrs={"placeholder": "https://wa.me/1234567890"}),
            "website": forms.URLInput(attrs={"placeholder": "https://yourbusiness.com"}),
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



class SeekerMediaForm(forms.ModelForm):
    """
    Handles uploads of media (images/videos) for SeekerPosts.
    """
    class Meta:
        model = MediaFile
        fields = ["file", "file_type", "caption", "is_public"]


# A formset allows multiple uploads at once
SeekerMediaFormSet = modelformset_factory(
    MediaFile,
    form=SeekerMediaForm,
    extra=1,        # one empty form for new upload
    can_delete=True # allow removing existing uploads
)
