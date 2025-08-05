from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordResetForm,
    PasswordChangeForm,
    AuthenticationForm
)
from .models import CustomUser
from django.core.exceptions import ValidationError


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Kindly enter your email address!"
        self.fields['password'].label = "Your Password"
        self.fields['username'].widget.attrs.update({
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
            'autocomplete': 'off',
            'placeholder': 'Enter your Gmail address (e.g. johnsmith@gmail.com)',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
            'autocomplete': 'off',
        })

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        if not username.endswith("@gmail.com"):
            raise forms.ValidationError("Please use a Gmail address (e.g., yourname@gmail.com)")
        return username.split('@')[0]


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label_map = {
            'username': 'Email address',
            'email': 'Confirm your email address',
            'phone_number': 'Phone Number',
            'password1': 'Password',
            'password2': 'Confirm Password',
        }
        error_message_map = {
            'required': 'Please fill out this field.',
        }

        for field_name, field in self.fields.items():
            field.label = label_map.get(field_name, field_name.capitalize())
            field.error_messages.update(error_message_map)
            field.widget.attrs.update({
                'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
                'autocomplete': 'off'
            })

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip().lower()
        if not username.endswith("@gmail.com"):
            raise forms.ValidationError("Please use a Gmail address (e.g., yourname@gmail.com)")
        username = username.split("@")[0]
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Sorry! This email prefix is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use. Please use a different email address.")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise forms.ValidationError("This phone number is already in use. Please use a different phone number.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)

        # Ensure virtual_id is set (in case it wasn't set by default)
        if not user.virtual_id:
            from .models import generate_virtual_id
            user.virtual_id = generate_virtual_id()

        # Auto-assign email by appending @gmail.com to the username
        user.email = f"{user.username}@gmail.com"

        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "phone_number", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        label_map = {
            'username': 'Email Prefix',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'first_name': 'First Name',
            'last_name': 'Last Name',
        }
        for name, field in self.fields.items():
            field.label = label_map.get(name, name.capitalize())
            field.widget.attrs.update({
                'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
                'autocomplete': 'off'
            })


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="Kindly enter email address here:",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
        }),
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=email).exists():
            raise ValidationError("No account is associated with this email address.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Old Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
        }),
    )
    new_password1 = forms.CharField(
        label="New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
        }),
        help_text=PasswordChangeForm.base_fields['new_password1'].help_text,
    )
    new_password2 = forms.CharField(
        label="Confirm New Password",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
        }),
    )

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")
        return new_password2


class ConfirmPasswordForm(forms.Form):
    password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control input-wrapper block text-sm font-medium text-gray-700 mb-1 block w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out bg-gray-100 text-gray-900',
            'autocomplete': 'off',
            'placeholder': 'Enter your password to confirm',
        })
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not self.user.check_password(password):
            raise forms.ValidationError("Incorrect password.")
        return password
