from django import forms
from .models import Post
from custom_search.models import Continent, Country, State, Town
from phonenumber_field.formfields import PhoneNumberField

class PostForm(forms.ModelForm):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890', 'class':'w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent'}))

    use_default_location = forms.ChoiceField(
        choices=[(True, "Use my default location"), (False, "Specify a custom location")],
        widget=forms.RadioSelect,
        initial=True,
        label="Location Option",
    )

    # 🔥 Dual input fields: Dropdown & Text Input (Auto-Suggest)
    continent = forms.ModelChoiceField(queryset=Continent.objects.all(), required=False, empty_label="Select Continent")
    continent_text = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Type a continent", "class":"w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"}))

    country = forms.ModelChoiceField(queryset=Country.objects.all(), required=False, empty_label="Select Country")
    country_text = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Type a country", "class":"w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"}))

    state = forms.ModelChoiceField(queryset=State.objects.all(), required=False, empty_label="Select State")
    state_text = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Type a state", "class":"w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"}))

    town = forms.ModelChoiceField(queryset=Town.objects.all(), required=False, empty_label="Select Town")
    town_text = forms.CharField(required=False, widget=forms.TextInput(attrs={"placeholder": "Type a town", "class":"w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-green-400 focus:border-transparent"}))

    class Meta:
        model = Post
        fields = ["category", "product_name", "description", "author_phone_number", "author_email", "use_default_location"]

    def clean(self):
        cleaned_data = super().clean()

        # 🔥 Validate user-typed location input
        def validate_field(field_name, model):
            user_input = cleaned_data.get(f"{field_name}_text")
            if user_input:
                if not model.objects.filter(name__iexact=user_input).exists():
                    self.add_error(f"{field_name}_text", f"Invalid {field_name}. Please select from the list.")
                else:
                    cleaned_data[field_name] = model.objects.get(name__iexact=user_input)

        validate_field("continent", Continent)
        validate_field("country", Country)
        validate_field("state", State)
        validate_field("town", Town)

        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)

        # 🔥 Assign location automatically if user selects "default location"
        if post.use_default_location:
            profile = post.author.profile
            post.continent = profile.continent
            post.country = profile.country
            post.state = profile.state
            post.town = profile.town
        else:
            post.continent = self.cleaned_data.get("continent")
            post.country = self.cleaned_data.get("country")
            post.state = self.cleaned_data.get("state")
            post.town = self.cleaned_data.get("town")

        if commit:
            post.save()
        return post
