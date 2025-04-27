from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']
        widgets = {
            'parent': forms.HiddenInput(),  # Hides the parent field for nested comments
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 3,
            }),  # Adds Bootstrap styling for better UI
        }

    def clean_text(self):
        text = self.cleaned_data.get("text")
        if len(text.strip()) < 3:
            raise forms.ValidationError("Your comment must be at least 3 characters long.")
        return text
