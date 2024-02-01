from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from products.models import Product


class Cart:
    """
    Initialize the session and the cart
    """
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = request.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1,replace_current_quantity = False):
        """
        Add a product to the cart or update the cart
        """
        product_id = str(product.id)
        self.cart[product_id] = {'quantity': quantity}
        if replace_current_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        messages.success(self.request, _('Product added successfully'))
        self.save()

    def remove(self, product):
        """
        Remove a product from the cart
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            messages.success(self.request, _('Product removed successfully'))

            self.save()

    def save(self):
        """
        update session
        """
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product_obj'] = product

        for item in cart.values():
            item['total_price'] = item['quantity'] * item['product_obj'].price
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.save()

    def get_total(self):
        product_ids = self.cart.keys()
        return sum(item['quantity'] * item['product_obj'].price for item in self.cart.values())
