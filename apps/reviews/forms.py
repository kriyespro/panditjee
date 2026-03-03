from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'input-field w-24'}),
            'review_text': forms.Textarea(attrs={'rows': 3, 'class': 'input-field', 'placeholder': 'Share your experience...'}),
        }
