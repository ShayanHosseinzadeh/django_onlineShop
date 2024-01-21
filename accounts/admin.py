from django.contrib import admin
from .forms import CustomCreationForm,CustomChangeform
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeform
    model = CustomUser
    list_display = ['username','email']
