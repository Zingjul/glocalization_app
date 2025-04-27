from django import forms
from .models import Person
from custom_search.models import Continent, Country, State, Town  # Import location models
from django.utils.translation import gettext_lazy as _

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'business_name', 'person_profile_picture', 'about', 'website', 'use_business_name',
            'continent', 'country', 'state', 'town'
        ]
        labels = {
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
            'about': _("What's the story behind you or your brand?"),
            'website': _("Your personal or business website (optional)."),
            'continent': _("Choose the continent where you live."),
            'country': _("Select the country you're located in."),
            'state': _("Pick your state."),
            'town': _("Select your town for precise location."),
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'continent': forms.Select(attrs={'class': 'form-select'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'town': forms.Select(attrs={'class': 'form-select'}),
        }
        error_messages = {
            'business_name': {
                'required': _("Your business name is required."),
            },
        }

    continent = forms.ModelChoiceField(
        queryset=Continent.objects.all(), required=False, empty_label="Select Continent"
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(), required=False, empty_label="Select Country"
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(), required=False, empty_label="Select State"
    )
    town = forms.ModelChoiceField(
        queryset=Town.objects.all(), required=False, empty_label="Select Town"
    )
