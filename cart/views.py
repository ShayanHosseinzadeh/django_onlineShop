from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from .forms import CartAddForm
from products.models import Product
from .cart import Cart


def CartDetailView(request):
    cart = Cart(request)
    for item in cart:
        item['product_quantity_update_form'] = CartAddForm(
            initial={
                'quantity': item['quantity'],
                'inplace':True,
            }
        )
    return render(request, 'cart/cart_detail.html',{'cart':cart})


@require_POST
def AddToCart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        cart.add(product, quantity,replace_current_quantity=cleaned_data['inplace'])

    return redirect('cart_detail')

def removecart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')