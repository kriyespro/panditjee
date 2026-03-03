from django import forms
from .models import Booking
from django.core.exceptions import ValidationError
from django.utils import timezone

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['puja_category', 'puja_date', 'puja_time', 'address', 'special_notes']
        widgets = {
            'puja_date': forms.DateInput(attrs={'type': 'date'}),
            'puja_time': forms.TimeInput(attrs={'type': 'time'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'special_notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        self.pandit = kwargs.pop('pandit', None)
        super().__init__(*args, **kwargs)
        if self.pandit:
            qs = self.pandit.specializations.all()
            if not qs.exists():
                from apps.core.models import PujaCategory
                qs = PujaCategory.objects.filter(is_active=True)
            self.fields['puja_category'].queryset = qs

    def clean_puja_date(self):
        date = self.cleaned_data.get('puja_date')
        if date and date < timezone.now().date():
            raise ValidationError("You cannot book a date in the past.")
        return date
