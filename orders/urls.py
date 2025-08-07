from django.urls import path

from orders import views

urlpatterns = [
    path('create/', views.order_create_view,name='order_create'),
    path('completed/', views.order_completion,name='order_complete'),
    path('invoice/<int:order_id>', views.order_invoice,name='invoice'),

]