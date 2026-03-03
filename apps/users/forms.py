"""apps/users/forms.py — Auth forms"""
from django import forms
from .models import User


class LoginForm(forms.Form):
    email    = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password', 'class': 'form-input'}))


class ClientRegisterForm(forms.ModelForm):
    password  = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'form-input'}), label='Confirm Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Mobile Number', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned


class PanditRegisterForm(forms.ModelForm):
    password        = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    password2       = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Confirm Password'}), label='Confirm Password')
    experience_years = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Years of experience'}))
    languages       = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Hindi, Gujarati, Sanskrit'}))
    base_price      = forms.DecimalField(min_value=1, widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Starting price (₹)'}))
    id_proof        = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-input'}))
    bank_account_name   = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    bank_account_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    ifsc_code       = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'IFSC Code'}))

    from apps.core.models import City, PujaCategory
    city            = forms.ModelChoiceField(queryset=City.objects.filter(is_active=True),
                                              widget=forms.Select(attrs={'class': 'form-input'}))
    specializations = forms.ModelMultipleChoiceField(queryset=PujaCategory.objects.filter(is_active=True),
                                                      widget=forms.CheckboxSelectMultiple(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'email':      forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-input'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Mobile Number', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('password2'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned
