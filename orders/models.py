from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _

from products.models import Product


# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name=_('User'))
    first_name = models.CharField(_('Firstname'), max_length=100)
    last_name = models.CharField(_('Lastname'), max_length=100)
    email = models.EmailField(_('Email'), )
    phone_number = models.CharField(_('Phone Number'), max_length=15)
    address = models.CharField(_('Address'), max_length=700)
    paid = models.BooleanField(_('Is_Paid?'), default=False)
    order_notes = models.CharField(_('Order Notes'), max_length=700, blank=True)

    datetime_created = models.DateTimeField(_('Created at'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Modified at'), auto_now=True)

    authority = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Order {self.id}"

    def get_total_price(self):
        result = 0
        # for item in self.items.all():
        #     result += item.price * item.quantity
        return sum(item.quantity * item.price for item in self.items.all())




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'Orderitem {self.id} : {self.product} x {self.quantity} price: ({self.price})'
