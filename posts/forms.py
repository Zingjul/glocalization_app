from django import forms
from .models import Post, PostImage
from phonenumber_field.formfields import PhoneNumberField

class PostForm(forms.ModelForm):
    author_phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'placeholder': 'e.g., +1234567890'}))
    class Meta:
        model = Post
        fields = ['category', 'description', 'author_phone_number', 'author_email', 'product_name'] # Add 'product_name' here
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'author_phone_number': forms.TextInput(attrs={'placeholder': 'e.g., 08012345678'}),
            'author_email': forms.EmailInput(attrs={'placeholder': 'e.g., yourname@example.com'}),
            'product_name': forms.TextInput(attrs={'placeholder': 'Enter a real-world product name'}) #added product_name widget.
        }
        labels = {
            'category': 'Post Category',
            'description': 'Post Description',
            'author_phone_number': 'Your Phone Number',
            'author_email': 'Your Email',
            'product_name': 'Product Name', #added product_name label.
        }
        help_texts = {
            'description': 'Write your post description here.',
        }
        error_messages = {
            'description': {
                'required': 'The description is required',
            },
        }

class PostImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']
        labels = {'image':'',}
class CustomPostImageFormSet(forms.BaseInlineFormSet):
    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        form.fields['DELETE'].widget = forms.HiddenInput()
        return form

PostImageFormSet = forms.inlineformset_factory(Post, PostImage, form=PostImageForm, formset=CustomPostImageFormSet, extra=6, can_delete=True)