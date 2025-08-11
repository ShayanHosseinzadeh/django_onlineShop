from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.Admin_Home.as_view(), name='Admin_Home'),
]