# seekers/forms.py
"""
Complete, DRY seekers forms file.

- BaseSeekerPostForm handles common fields, location defaults, and save/clean behavior.
- Child forms override only labels/placeholders.
- Supports passing `user=` into the form constructor to prefill author contact info.
"""

from django import forms
from phonenumber_field.formfields import PhoneNumberField
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from custom_search.models import Continent, Country, State, Town
from .models import SeekerPost, SeekerSocialMediaHandle
from .mixins import LocationFieldsSetupMixin
# from .utils.location_assignment import assign_location_fields
from posts.utils.location_assignment import assign_location_fields
from posts.utils.location_scope_guard import apply_location_scope_fallback



class BaseSeekerPostForm(forms.ModelForm, LocationFieldsSetupMixin):
    """Base form with shared behaviour for seeker posts (products, services, labor)."""

    author_phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={"placeholder": "e.g., +1234567890"}),
        required=False,
    )

    class Meta:
        model = SeekerPost
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
        """
        Accepts optional `user=` kwarg to prefill contact fields.
        Initializes location querysets / defaults and mixin helpers.
        """
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Prefill contact fields from provided user (if any)
        if user:
            if hasattr(user, "phone_number") and user.phone_number:
                # Note: author_phone_number is a form field (PhoneNumberField), not model field
                self.fields["author_phone_number"].initial = user.phone_number
            if hasattr(user, "email") and user.email:
                self.fields["author_email"].initial = user.email
        # Location querysets: show all available items (Unspecified id=0 can be present)
        # We intentionally use .all() so ordering/annotate from DB works; .initial uses id=0 fallback
        self.fields["post_continent"].queryset = Continent.objects.all()
        self.fields["post_country"].queryset = Country.objects.all()
        self.fields["post_state"].queryset = State.objects.all()
        self.fields["post_town"].queryset = Town.objects.all()


        # ✅ Force "Unspecified" to exist in querysets
        self.fields['post_continent'].queryset = Continent.objects.filter(id=0) | Continent.objects.all()
        self.fields['post_country'].queryset = Country.objects.filter(id=0) | Country.objects.all()
        self.fields['post_state'].queryset = State.objects.filter(id=0) | State.objects.all()
        self.fields['post_town'].queryset = Town.objects.filter(id=0) | Town.objects.all()


        # Remove Django's default "------" empty option for select fields (if they exist)
        for f in ("post_continent", "post_country", "post_state", "post_town"):
            if f in self.fields:
                self.fields[f].empty_label = None

        # Default initial to an "Unspecified" sentinel if present (id=0). If missing, initial becomes None.
        self.fields["post_continent"].initial = Continent.objects.filter(id=0).first()
        self.fields["post_country"].initial = Country.objects.filter(id=0).first()
        self.fields["post_state"].initial = State.objects.filter(id=0).first()
        self.fields["post_town"].initial = Town.objects.filter(id=0).first()

        self.fields["title"].label = "What are you seeking?"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., iPhone 13, Plumbing service"

        self.fields["description"].label = "Description"
        self.fields["description"].widget.attrs["placeholder"] = "Provide details so suppliers can respond quickly."

        self.fields["author_email"].label = "Contact email (optional)"
        self.fields["author_phone_number"].label = "Contact phone number (optional)"

        self.fields["preferred_fulfillment_time"].label = "Preferred timing (optional)"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "E.g., Weekdays, Mornings, ASAP"

        self.fields["budget"].label = "Budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "E.g., 15000.00"

        # 🔹 Init mixin helpers
        self.init_location_labels_and_placeholders()
        self.init_location_queryset()

    def clean(self):
        """
        Normalize location fields depending on availability_scope.
        If town was typed (post_town_input) but not selected, fallback to 'Unspecified' sentinel.
        """
        cleaned = super().clean()
        scope = cleaned.get("availability_scope")

        unspecified_continent = Continent.objects.filter(id=0).first()
        unspecified_country = Country.objects.filter(id=0).first()
        unspecified_state = State.objects.filter(id=0).first()
        unspecified_town = Town.objects.filter(id=0).first()

        # Apply scope fallback rules (same semantics as posts forms)
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
            # If user typed a town name and did not select one, fallback to unspecified and mark for review elsewhere
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
        assign_location_fields(self)  # inject location data

        if commit:
            instance.save()
        return instance


# --- Child forms (only override labels/placeholders) ---
class ProductSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["title"].label = "Product you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., iPhone 13, Samsung TV"

        self.fields["budget"].label = "Budget (optional)"
        self.fields["budget"].widget.attrs["placeholder"] = "E.g., 15000.00"

class ServiceSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Service you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Plumbing service, Guitar lessons"
        self.fields["preferred_fulfillment_time"].label = "When do you need the service?"
        self.fields["preferred_fulfillment_time"].widget.attrs["placeholder"] = "E.g., Within 2 weeks, ASAP"


class LaborSeekerForm(BaseSeekerPostForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Labor / Skill you're seeking"
        self.fields["title"].widget.attrs["placeholder"] = "E.g., Electrician, Carpenter"

# --- Social Media Handle Form for Seekers ---
class SeekerSocialMediaHandleForm(forms.ModelForm):
    url_validator = URLValidator()

    class Meta:
        model = SeekerSocialMediaHandle
        fields = [
            "linkedin",
            "twitter",
            "youtube",
            "instagram",
            "facebook",
            "whatsapp",
            "website",
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
        for field_name, url in cleaned_data.items():
            if url:
                try:
                    self.url_validator(url)
                except ValidationError:
                    self.add_error(field_name, f"Invalid URL provided for {field_name}. Please use a valid URL starting with https://")
        return cleaned_data

