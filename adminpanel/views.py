from django.shortcuts import render
from django.views import generic


# Create your views here.

class admin_home(generic.TemplateView):
    template_name = 'adminpanel/admin_dashboard.html'