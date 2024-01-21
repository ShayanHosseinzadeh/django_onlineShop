from django.shortcuts import render
from django.views import generic
from .forms import CustomCreationForm
from django.urls import reverse_lazy
class SignUpView(generic.CreateView):
    form_class = CustomCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
