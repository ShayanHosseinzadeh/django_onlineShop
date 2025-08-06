from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _

from cart.cart import Cart
from .forms import OrderForm
from .models import OrderItem, Order


# Create your views here.
@login_required
def order_create_view(request):
    order_form = OrderForm()
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, _("You cannot proceed to checkout page with an empty cart!"))
        return redirect('cart_detail')

    if request.method == 'POST':
        order_form = OrderForm(request.POST, )
        if order_form.is_valid():
            order_obj = order_form.save(commit=False)
            order_obj.user = request.user
            order_obj.save()
            request.user.first_name = order_obj.first_name
            request.user.last_name = order_obj.last_name
            request.user.save()
            for item in cart:
                product = item['product_obj']
                OrderItem.objects.create(
                    order=order_obj,
                    product=product,
                    quantity=item['quantity'],
                    price=product.get_discounted_price,
                )
            cart.clear()
            request.session['order_id'] = order_obj.id
            return redirect('order_complete')

        if order_form.errors:
            messages.error(request, _('Please Review the errors and solve them!'))

    return render(request, 'orders/order_create.html', {'order_form': order_form})


@login_required
def order_completion(request):
    order_id = request.session.get('order_id')

    if not order_id:
        return redirect('product_list')

    order = get_object_or_404(Order, id=order_id, user=request.user)

    del request.session['order_id']

    context = {
        'order': order,
    }
    return render(request, 'orders/order_complete.html', context)

