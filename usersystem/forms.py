from django import forms
from .models import User

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=100)
    password = forms.CharField(label='password', max_length=100)

class RegisterForm(forms.Form):
    username = forms.CharField(label='username', max_length=100, min_length=6)
    password = forms.CharField(label='password', max_length=100, min_length=6,
                               widget=forms.PasswordInput)
    confirmpassword = forms.CharField(label='Confirm Password', max_length=100, min_length=6,
                                      widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirmpassword')
        if p1 and p2 and p1 != p2:
            self.add_error('confirmpassword', 'Passwords do not match')
        return cleaned
