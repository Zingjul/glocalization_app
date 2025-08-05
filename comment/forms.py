from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text', 'parent']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your comment here...',
                'rows': 3,
            }),
            'parent': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional: Add placeholder flexibility (if ever reused for replies)
        self.fields['text'].widget.attrs.setdefault('placeholder', 'Write your comment...')

    def clean_text(self):
        text = self.cleaned_data.get("text", "")
        if len(text.strip()) < 3:
            raise forms.ValidationError("Your comment must be at least 3 characters long.")
        return text
