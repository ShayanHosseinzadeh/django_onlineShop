# core/forms.py
from django import forms

from adminpanel.forms import NoTextClearableFileInput
from .models import SiteSettings

BASE = "w-full px-4 py-2.5 border-2 border-gray-200 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition text-right"


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = ["site_name", "support_email", "support_phone", "support_address", "logo", "favicon",
                  'maintenance_enabled', 'maintenance_message']
        widgets = {
            "site_name": forms.TextInput(attrs={"class": BASE}),
            "support_email": forms.EmailInput(attrs={"class": BASE, "dir": "ltr"}),
            "support_phone": forms.TextInput(attrs={"class": BASE}),
            "support_address": forms.Textarea(attrs={"class": BASE, "rows": 3}),
            "logo": NoTextClearableFileInput(attrs={"id": "id_logo", "class": "hidden", "accept": "image/*"}),
            "favicon": NoTextClearableFileInput(attrs={"id": "id_favicon", "class": "hidden", "accept": "image/*"}),
            "maintenance_enabled": forms.CheckboxInput(attrs={
                "id": "id_maintenance_enabled",
                "class": "sr-only peer",
            }),
            "maintenance_message": forms.Textarea(attrs={
                "class": BASE,
                "rows": 4,
                "placeholder": "پیامی که در حالت نگه‌داری به کاربران نمایش داده می‌شود…",
                "dir": "rtl",
            }),
        }
