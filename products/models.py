# products/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.db.models import Avg

from ckeditor.fields import RichTextField


# --- New Category Model ---
class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True, verbose_name=_('Category Name'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Category Slug'))

    class Meta:
        ordering = ('name',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])


# Custom Manager for available products
class AvailableProducts(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='avl')


# --- Updated Product Model ---
class Product(models.Model):
    STATUS_CHOICES = (
        ('avl', _('Available')),
        ('una', _('Unavailable')),

    )
    # New ForeignKey for Category
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True,
                                 verbose_name=_('Category'))

    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = RichTextField(verbose_name=_('Description'))
    short_description = models.TextField(verbose_name=_('Short Description'), blank=True)
    datetime_created = models.DateTimeField(default=timezone.now, verbose_name=_('Date of Creation'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modifed'))
    price = models.PositiveIntegerField(default=0, verbose_name=_('Price'))
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, verbose_name=_('Status'))
    stock_quantity = models.PositiveIntegerField(default=1, verbose_name=_('In stock'))
    image = models.ImageField(verbose_name=_('Product Image'), upload_to='product/product_image', blank=True, )

    # Original get_absolute_url method is kept
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])

    # New get_average_rating method is kept, it doesn't affect the original code
    def get_average_rating(self):
        average_rating = self.comments.filter(is_verified=True).aggregate(Avg('stars'))['stars__avg']
        return round(average_rating, 1) if average_rating else 0

    objects = models.Manager()
    available = AvailableProducts()

    def __str__(self):
        return self.title


# Custom Manager for verified comments
class VerifiedComments(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_verified=True)


# --- Updated Comment Model ---
class Comment(models.Model):
    PRODUCT_STARS = (
        ('1', _('Very Bad')),
        ('2', _(' Bad')),
        ('3', _(' Normal')),
        ('4', _(' Good')),
        ('5', _('Very Good')),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', verbose_name=_('product'))
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='comments',
                             verbose_name=_('Comment Author'))
    text = models.TextField(blank=False, verbose_name=_('Text'))
    is_verified = models.BooleanField(default=False, verbose_name=_('Verifed?'))
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_('Modified at'))
    stars = models.CharField(max_length=10, choices=PRODUCT_STARS, verbose_name=_('Rate'))

    objects = models.Manager()
    verified_comments = VerifiedComments()

    def __str__(self):
        return f"{self.user}:{self.text}"