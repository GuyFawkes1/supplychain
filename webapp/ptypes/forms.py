from django.contrib.auth.models import User
from django import forms
from .models import ProductTypeCreation


class ProductTypeForm(forms.ModelForm):    
    class Meta:
        model = ProductTypeCreation
        fields = ['ptype_name', 'role_assign', 'check_assign']

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        #fields = ['username', 'password', 'dept'] 
        fields = ['username', 'password']

