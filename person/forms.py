from django import forms
from .models import Person
from custom_search.models import Continent, Country, State, Town
from django.utils.translation import gettext_lazy as _

class PersonForm(forms.ModelForm):
    # Dropdown fields (existing)
    continent = forms.ModelChoiceField(
        queryset=Continent.objects.all(),
        required=False,
        empty_label=_("Select Continent"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        required=False,
        empty_label=_("Select Country"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    state = forms.ModelChoiceField(
        queryset=State.objects.all(),
        required=False,
        empty_label=_("Select State"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    town = forms.ModelChoiceField(
        queryset=Town.objects.all(),
        required=False,
        empty_label=_("Select Town"),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # NEW text input fields for user to type location if not listed
    continent_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            # 'class': 'form-textarea block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900',
            # 'placeholder': _('Type your continent if not listed'),
        }),
        label=_("Or enter your continent")
    )
    country_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            # 'class': 'form-textarea block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900',
            # 'placeholder': _('Type your country if not listed'),
        }),
        label=_("Or enter your country")
    )
    state_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            # 'class': 'form-textarea block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900',
            # 'placeholder': _('Type your state if not listed'),
        }),
        label=_("Or enter your state")
    )
    town_input = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            # 'class': 'form-textarea block w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-100 text-gray-900',
            # 'placeholder': _('Type your town if not listed'),
        }),
        label=_("Or enter your town")
    )

    class Meta:
        model = Person
        fields = [
            'person_profile_picture', 'real_name', 'business_name', 'about', 'website', 'continent', 'country', 'state', 'town', 'continent_input', 'country_input', 'state_input', 'town_input',
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
            # Your existing widget styles here...
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
                'required': _("Please select your continent or type it below."),
            },
            'country': {
                'required': _("Please select your country or type it below."),
            },
            'state': {
                'required': _("Please select your state or type it below."),
            },
            'town': {
                'required': _("Please select your town or type it below."),
            },
        }
    def clean(self):
        cleaned_data = super().clean()

        # For each location, prefer typed input if filled, else dropdown selection
        for loc in ['continent', 'country', 'state', 'town']:
            typed_value = cleaned_data.get(f"{loc}_input")
            dropdown_value = cleaned_data.get(loc)

            if typed_value:
                # User typed custom value; store it and clear dropdown field to avoid conflicts
                cleaned_data[loc] = None  # Clear the dropdown value
                cleaned_data[f"{loc}_input"] = typed_value.strip()
            else:
                # No typed input; use dropdown value, clear typed input
                cleaned_data[f"{loc}_input"] = None

        return cleaned_data
