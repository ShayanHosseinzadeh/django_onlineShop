from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm,UserCreationForm


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username','email']


class CustomChangeform(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['username','email']