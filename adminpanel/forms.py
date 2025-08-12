from django import forms
from django.forms.models import ModelForm

from accounts.models import UserProfile


class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'role', 'phone_number', 'address', 'city', 'postal_code', 'birth_date','avatar']