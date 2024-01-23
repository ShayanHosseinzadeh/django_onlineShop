from django.shortcuts import render
from django.views import generic
from .models import Product

# Create your views here.
class ProductListView(generic.ListView):
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 4
    def get_queryset(self):
        return Product.objects.filter(status='avl').order_by('-price')


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'