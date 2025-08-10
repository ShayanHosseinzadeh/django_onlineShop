from django.urls import path, include
from . import views
urlpatterns = [
    path('',views.admin_home.as_view(),name='admin_home'),
]