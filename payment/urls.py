from django.urls import path

from payment import views


urlpatterns = [
    path('process/', views.payment_process, name='payment_process',)
]