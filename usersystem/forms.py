from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100)
    password = forms.CharField(label='Password', max_length=100)

class RegisterForm(forms.Form):
    username = forms.CharField(label='Username', max_length=100, min_length=6)
    password = forms.CharField(label='Password', max_length=100, min_length=6)
    confirmpassword = forms.CharField(label='Confirm Password', max_length=100, min_length=6)

    def clean(self):
        username = self.cleaned_data.get('username')
        exists = User.objects.filter(Username=username).exists()
        if exists:
            raise forms.ValidationError("Username already exists")
        return username

