from django.contrib import admin
from .models import Product,Comment
# Register your models here.


class CommentInline(admin.StackedInline):
    model = Comment
    fields = ('text','user','stars','is_verified')
    extra = 1
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title','price','stock_quantity','status')
    inlines = [CommentInline]



@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text','user','product','datetime_created','stars','is_verified')