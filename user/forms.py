from dataclasses import field, fields
from django import forms
from .models import Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import ProductRequest




class CreateUserForm(UserCreationForm):
    email = forms.EmailField()
    branchID = forms.CharField(required=False)
    

    class Meta:
        model = User
        fields = ['username','email','password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address','phone','image']

class ProductRequestForm(forms.ModelForm):
    class Meta:
        model = ProductRequest
        fields = ('product_name', 'description')



