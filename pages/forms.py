from django import forms

from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message', 'privacy_accepted']
        widgets = {
            'privacy_accepted': forms.CheckboxInput(attrs={
                'class': 'mt-1 ml-3 w-4 h-4 text-primary border-2 border-black-light rounded focus:ring-orange-light',
            }),
            # بقیه ویجت‌ها...
        }
        labels = {
            'privacy_accepted': 'با قوانین و مقررات و حریم خصوصی موافقم',
            # بقیه لیبل‌ها...
        }

    def clean_privacy_accepted(self):
        accepted = self.cleaned_data.get('privacy_accepted')
        if not accepted:
            raise forms.ValidationError('برای ارسال پیام باید با قوانین و مقررات موافقت کنید.')
        return accepted