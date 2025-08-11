from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomCreationForm


class SignUpView(generic.CreateView):
    form_class = CustomCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
