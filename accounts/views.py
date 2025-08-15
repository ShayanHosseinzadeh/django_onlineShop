from allauth.account.views import SignupView
from django.urls import reverse_lazy

from accounts.forms import CustomSignupForm
from accounts.models import UserProfile


class CustomSignupView(SignupView):
    template_name = 'account/signup.html'
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        return super().form_valid(form)

