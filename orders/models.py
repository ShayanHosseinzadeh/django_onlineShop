from django.db import models
from django.conf import settings
from django.utils.translation import gettext as _

from products.models import Product


# Create your models here.
from django.utils.translation import gettext_lazy as _

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', _('در انتظار بررسی')),
        ('processing', _('در حال پردازش')),
        ('shipped', _('ارسال شده')),
        ('completed', _('تکمیل شده')),
        ('cancelled', _('لغو شده')),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('کاربر')
    )
    first_name = models.CharField(_('نام'), max_length=100)
    last_name = models.CharField(_('نام خانوادگی'), max_length=100)
    email = models.EmailField(_('ایمیل'))
    phone_number = models.CharField(_('شماره تماس'), max_length=15)
    address = models.CharField(_('آدرس'), max_length=700)
    paid = models.BooleanField(_('پرداخت شده؟'), default=False)
    status = models.CharField(_('وضعیت سفارش'), max_length=20, choices=STATUS_CHOICES, default='pending')
    order_notes = models.CharField(_('یادداشت مشتری'), max_length=700, blank=True)

    zarinpal_data = models.TextField(_('اطلاعات زرین‌پال'), blank=True)
    datetime_created = models.DateTimeField(_('تاریخ ایجاد'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('تاریخ ویرایش'), auto_now=True)

    authority = models.CharField(_('شناسه Authority'), max_length=255, blank=True)
    ref_id = models.CharField(_('کد پیگیری'), max_length=150, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.status}"

    def get_total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()

    def __str__(self):
        return f'Orderitem {self.id} : {self.product} x {self.quantity} price: ({self.price})'
