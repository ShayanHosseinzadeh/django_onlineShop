from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model


# Create your models here.
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
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id])


class VerifiedComments(models.Manager):
    def get_queryset(self):
        return super(VerifiedComments, self).get_queryset().filter(is_verified=True)



class Comment(models.Model):
    PRODUCT_STARS = (
        ('1', 'Very Bad'),
        ('2', ' Bad'),
        ('3', ' Normal'),
        ('4', ' Good'),
        ('5', 'Very Good'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='comments')
    text = models.TextField(blank=False,verbose_name='متن نظر')
    is_verified = models.BooleanField(default=False)
    datetime_created = models.DateTimeField(auto_now_add=True)
    datetime_modified = models.DateTimeField(auto_now=True)
    stars = models.CharField(max_length=10, choices=PRODUCT_STARS,verbose_name='امتیاز')

    objects = models.Manager()
    verified_comments = VerifiedComments()

    def __str__(self):
        return f"{self.user}:{self.text}"

