from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

# Create your models here.

class AvailableProducts(models.Manager):
    def get_queryset(self):
        return super(AvailableProducts, self).get_queryset().filter(status='avl')


class Product(models.Model):
    STATUS_CHOICES = (
        ('avl', 'Available'),
        ('una', 'Unavailable'),

    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    stock_quantity = models.PositiveIntegerField(default=1)

    objects = models.Manager()
    available = AvailableProducts()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])


class VerifiedComments(models.Manager):
    def get_queryset(self):
        return super(VerifiedComments, self).get_queryset().filter(is_verified=True)


class Comment(models.Model):
    PRODUCT_STARS = (
        ('1', _('Very Bad')),
        ('2', _(' Bad')),
        ('3', _(' Normal')),
        ('4', _(' Good')),
        ('5', _('Very Good')),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments',verbose_name=_('product'))
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments',verbose_name=_('Comment Author'))
    text = models.TextField(blank=False, verbose_name=_('Text'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verifed?'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('Modified at'))
    stars = models.CharField(max_length=10, choices=PRODUCT_STARS, verbose_name=_('Rate'))

    objects = models.Manager()
    verified_comments = VerifiedComments()

    def __str__(self):
        return f"{self.user}:{self.text}"
