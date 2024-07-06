from django import forms
from django.contrib.auth.models import User


# F
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [ "username", "email","password"]
        widgets = {
            "username" : forms.widgets.TextInput(attrs = {"class" : "input", "placeholder" : "User"}),
            "email" : forms.widgets.EmailInput(attrs = {"class" : "input", "placeholder" : "Email"}),
            "password" : forms.widgets.PasswordInput(attrs = {"class" : "input", "placeholder" : "Password"})
        }