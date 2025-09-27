# person/forms.py
from django import forms
from .models import Person
from custom_search.models import Continent, Country, State, Town
from django.utils.translation import gettext_lazy as _
from accounts.models import Follow
from .mixins import ImageFieldsMixin, LocationFieldsSetupMixin
from posts.utils.location_assignment import assign_location_fields


class PersonForm(forms.ModelForm, ImageFieldsMixin, LocationFieldsSetupMixin):
    class Meta:
        model = Person
        fields = [
            "person_profile_picture",
            "real_name",
            "business_name",
            "about",
            "website",
            "continent",
            "country",
            "state",
            "town",
            "town_input",
            "use_business_name",
        ]

        labels = {
            'real_name': _("Provide your real name!"),
            'business_name': _("What's the name of your awesome business/service?"),
            'person_profile_picture': _("Add a photo that shows your style!"),
            'about': _("Share your story!"),
            'website': _("Do you have a site with more info? Feel free to add"),
            'use_business_name': _("Display Business Name on Posts?"),
            'continent': _("Select Your Continent"),
            'country': _("Select Your Country"),
            'state': _("Select Your State"),
            'town': _("Select Your Town"),
        }

        help_texts = {
            'person_profile_picture': _("Make your profile stand out with a picture!"),
            'real_name': _("What's the story behind you or your brand?"),
            'about': _("What's the story behind you or your brand?"),
            'website': _("Your personal or business website (optional)."),
            'continent': _("Choose the continent where you live."),
            'country': _("Select the country you're located in."),
            'state': _("Pick your state."),
            'town': _("Select your town for precise location."),
        }

        widgets = {
                'business_name': forms.TextInput(attrs={
                'class': 'form-input block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900'
            }),
                'about': forms.Textarea(attrs={
                'class': 'form-textarea block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900',
                'rows': 4,
            }),
                'website': forms.URLInput(attrs={
                'class': 'form-input block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900'
            }),
                'use_business_name': forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-green-600 transition duration-150 ease-in-out'
            }),
        }

        error_messages = {
            'business_name': {
                'required': _("Please enter the name of your business or service."),
                'max_length': _("The business name is too long. Please shorten it."),
            },
            'about': {
                'required': _("Please provide some information about yourself or your brand."),
            },
            'website': {
                'invalid': _("Please enter a valid website URL."),
            },
            'continent': {
                'required': _("Please select your continent."),
            },
            'country': {
                'required': _("Please select your country."),
            },
            'state': {
                'required': _("Please select your state."),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ Force "Unspecified" into all dropdowns
        self.fields['continent'].queryset = Continent.objects.filter(id=0) | Continent.objects.all()
        self.fields['country'].queryset = Country.objects.filter(id=0) | Country.objects.all()
        self.fields['state'].queryset = State.objects.filter(id=0) | State.objects.all()
        self.fields['town'].queryset = Town.objects.filter(id=0) | Town.objects.all()

        # ✅ Remove Django’s default “------”
        for field in ["continent", "country", "state", "town"]:
            if field in self.fields:
                self.fields[field].empty_label = None

        # ✅ Default initial = "Unspecified"
        self.fields["continent"].initial = Continent.objects.filter(id=0).first()
        self.fields["country"].initial = Country.objects.filter(id=0).first()
        self.fields["state"].initial = State.objects.filter(id=0).first()
        self.fields["town"].initial = Town.objects.filter(id=0).first()

    
    def save(self, commit=True):
        instance = super().save(commit=False)
        assign_location_fields(self)  # ✅ injects location data (dropdown or typed input)
        if commit:
            instance.save()
        return instance

class ProfileFollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = []  # no manual inputs

    def __init__(self, follower, following, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.follower = follower
        self.following = following

    def clean(self):
        cleaned_data = super().clean()
        if self.follower == self.following:
            raise forms.ValidationError("You cannot follow yourself.")
        if Follow.objects.filter(follower=self.follower, following=self.following).exists():
            raise forms.ValidationError("You already follow this user.")
        return cleaned_data

    def save(self, commit=True):
        follow = Follow(follower=self.follower, following=self.following)
        if commit:
            follow.save()
        return follow
    