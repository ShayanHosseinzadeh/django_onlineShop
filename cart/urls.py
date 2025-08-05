from django.urls import path
from .views import CartDetailView, AddToCart, removecart, clear_cart , update_quantity_htmx

# app_name = 'cart'
urlpatterns = [
    path('', CartDetailView, name='cart_detail'),
    path('add/<int:product_id>', AddToCart, name='cart_add'),
    path('remove/<int:product_id>', removecart, name='cart_remove'),
    path('clear/', clear_cart, name='cart_clear'),
    path('update-quantity-htmx/', update_quantity_htmx, name='update_quantity_htmx'),

]
