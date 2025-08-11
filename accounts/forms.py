from allauth.account.forms import ResetPasswordForm, SignupForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from accounts.models import UserProfile


class CustomCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


class CustomChangeform(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'email']


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


class CustomSignupForm(SignupForm):
    fullName = forms.CharField(max_length=150, label='نام و نام خانوادگی')

    def save(self, request):
        # First, call the parent save method to create and save the user instance.
        # The base method handles the user creation and returns the user object.
        user = super().save(request)

        # Now that the user exists, you can create and save the UserProfile
        # The user's full_name field is on the UserProfile model, not the User model.
        user_profile = UserProfile.objects.create(
            user=user,
            full_name=self.cleaned_data['fullName']
        )
        user_profile.save()

        return user