from django import forms
from .models import Account

class Registrationform(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'required': True
    }))
    

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number' , 'email', 'password']
        


