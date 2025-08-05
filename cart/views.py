from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext as _

from .forms import CartAddForm
from products.models import Product
from .cart import Cart


def CartDetailView(request):
    cart = Cart(request)
    for item in cart:
        item['product_quantity_update_form'] = CartAddForm(
            initial={
                'quantity': item['quantity'],
                'inplace': True,
            }
        )
    return render(request, 'cart/cart_detail.html', {'cart': cart})


@require_POST
def AddToCart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        cart.add(product, quantity, replace_current_quantity=cleaned_data['inplace'])

    return redirect('cart_detail')


def removecart(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def clear_cart(request):
    cart = Cart(request)
    if len(cart) != 0:
        cart.clear()
        messages.success(request, _('Your card got cleared!'))

    else:
        messages.error(request, _('Your card is not empty!'))

    return redirect('cart_detail')


@require_POST
def update_quantity_htmx(request):
    print('hi')
    cart = Cart(request)
    product_id = request.POST.get('product_id')
    action = request.POST.get('action')

    product = get_object_or_404(Product, id=product_id)
    current_quantity = cart.cart.get(str(product_id), {}).get('quantity', 0)

    if action == 'increase':
        cart.add(product, quantity=1)
    elif action == 'decrease' and current_quantity > 1:
        cart.add(product, quantity=current_quantity - 1, replace_current_quantity=True)
    elif action == 'decrease' and current_quantity == 1:
        cart.remove(product)

    # بررسی کن ببینی هنوز توی سبد هست یا نه
    item = next((i for i in cart if i['product_obj'].id == product.id), None)

    if item:
        item['product_quantity_update_form'] = CartAddForm(
            initial={'quantity': item['quantity'], 'inplace': True}
        )
        html = render_to_string('cart/partials/cart_item.html', {'item': item}, request=request)
        return HttpResponse(html)
    else:
        # اگه حذف شده، یک بلاک خالی برگردون
        return HttpResponse("")

