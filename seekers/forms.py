from django import forms
from .models import SeekerPost, SeekerImage
from phonenumber_field.formfields import PhoneNumberField

class SeekerPostForm(forms.ModelForm):
    class Meta:
        model = SeekerPost
        fields = [
            "category",
            "request_type",
            "title",
            "description",
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
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "preferred_fulfillment_time": forms.TextInput(attrs={"placeholder": "e.g. ASAP, within 3 days, weekends only"}),
            "budget": forms.NumberInput(attrs={"placeholder": "Optional – add if relevant"}),
        }

class SeekerImageForm(forms.ModelForm):
    class Meta:
        model = SeekerImage
        fields = ["image"]

SeekerImageFormSet = forms.modelformset_factory(
    SeekerImage,
    form=SeekerImageForm,
    extra=6,  # default number of image fields
    max_num=6,
    can_delete=True
)
