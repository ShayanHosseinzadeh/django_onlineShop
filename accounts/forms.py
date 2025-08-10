from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm,UserCreationForm
from allauth.account.forms import ResetPasswordForm
from django.contrib.auth import get_user_model
from django import forms

class CustomCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username','email']


class CustomChangeform(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['username','email']



User = get_user_model()


class CustomResetPasswordForm(ResetPasswordForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        users = User.objects.filter(email=email)

        if not users.exists():
            raise forms.ValidationError("ایمیل وجود ندارد.")

        self.users = users
        return email