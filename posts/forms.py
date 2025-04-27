from django import forms
from .models import Post, PostImage
from phonenumber_field.formfields import PhoneNumberField

class PostForm(forms.ModelForm):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))

    use_default_location = forms.ChoiceField(
        choices=[(True, "Use my default location"), (False, "Specify a custom location")],
        widget=forms.RadioSelect,
        initial=True,
        label="Location Option",
    )

    class Meta:
        model = Post
        fields = [
            "category", "product_name", "description", "author_phone_number", "author_email",
            "use_default_location"
        ]  # 🔥 Removed non-editable location fields

        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "author_phone_number": forms.TextInput(attrs={"placeholder": "e.g., 08012345678"}),
            "author_email": forms.EmailInput(attrs={"placeholder": "e.g., yourname@example.com"}),
            "product_name": forms.TextInput(attrs={"placeholder": "Enter a real-world product name"}),
        }
        labels = {
            "category": "Post Category",
            "product_name": "Product Name",
            "description": "Post Description",
            "author_phone_number": "Your Phone Number",
            "author_email": "Your Email",
            "use_default_location": "Choose Location Preference",
        }
        help_texts = {
            "description": "Write your post description here.",
            "use_default_location": "Select default to use your profile location or specify a new location.",
        }

    def save(self, commit=True):
        post = super().save(commit=False)

        # 🔥 Assign location automatically if user selects "default location"
        if post.use_default_location:
            profile = post.author.profile  # Access user profile location
            post.continent = profile.continent
            post.country = profile.country
            post.state = profile.state
            post.town = profile.town

        if commit:
            post.save()
        return post
