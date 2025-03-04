# comments/forms.py

from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text','parent']
        widgets = {
            'parent': forms.HiddenInput(), #Hides the parent field.
        }