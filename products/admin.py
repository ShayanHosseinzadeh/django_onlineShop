from django.contrib import admin
from .models import Product,Comment
# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price','quantity','status')



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text','user','product','datetime_created','stars','is_verified')