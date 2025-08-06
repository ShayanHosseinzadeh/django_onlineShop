from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from products.models import Product


class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product, quantity=1, replace_current_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0}

        if replace_current_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        messages.success(self.request, _('Product added successfully'))
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            messages.success(self.request, _('Product removed successfully'))
            self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        products_map = {str(product.id): product for product in products}

        for product_id, item in self.cart.items():
            product = products_map.get(product_id)
            if product:
                item = item.copy()
                item['product_obj'] = product
                if product.discount_percent > 0:
                    discounted_price = product.price * (100 - product.discount_percent) // 100
                else:
                    discounted_price = product.price
                item['total_price'] = item['quantity'] * discounted_price
                yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session['cart']
        self.save()

    def get_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total = 0
        for product in products:
            quantity = self.cart[str(product.id)]['quantity']
            if product.discount_percent > 0:
                discounted_price = product.price * (100 - product.discount_percent) // 100
            else:
                discounted_price = product.price
            total += quantity * discounted_price
        return total


    def get_total_discount(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        total_discount = 0
        for product in products:
            quantity = self.cart[str(product.id)]['quantity']
            if product.discount_percent > 0:
                original_total = quantity * product.price
                discounted_total = quantity * (product.price * (100 - product.discount_percent) // 100)
                total_discount += original_total - discounted_total
        return total_discount