from django import forms
from .models import Person
from django.utils.translation import gettext_lazy as _

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['business_name', 'person_profile_picture', 'about', 'website', 'use_business_name']
        labels = {
            'business_name': _("What's the name of your awesome business/service?"),
            'person_profile_picture': _("Add a photo that shows your style!"),
            'about': _("Share your story!"),
            'website': _("Do you have a site with more info? Feel free to add"),
            'use_business_name': _("Display Business Name on Posts?"),
        }
        help_texts = {
            'person_profile_picture': _("Make your profile stand out with a picture!"),
            'about': _("What's the story behind you or your brand?"),
            'website': _("Your personal or business website (optional)."),
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 5}),
            'website': forms.URLInput(),
        }
        error_messages = {
            'business_name': {
                'required': _("Your business name is required."),
            },
        }