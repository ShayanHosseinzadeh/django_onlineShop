from django.db import models
from django.urls import reverse

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
        return reverse('product_detail',args=[self.id])
