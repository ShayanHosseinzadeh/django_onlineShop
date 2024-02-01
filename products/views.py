from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404, reverse
from django.contrib import messages
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _

from cart.cart import Cart
from .forms import CommentForm
from cart.forms import CartAddForm
from .models import Product, Comment


# Create your views here.
class ProductListView(generic.ListView):
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 4
    # def get(self,request, *args, **kwargs):
    #     messages.success(self.request, ' Welcome to the page')
    #     return super().get(request, args, kwargs)

    def get_queryset(self):
        return Product.available.order_by('-price')

#
def ProductDetailView(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = Comment.verified_comments.filter(product=product).order_by('-datetime_created')
    comment_form = CommentForm()
    add_to_cart_form = CartAddForm
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()
            messages.success(request, _('Your comment has been submited and would be shown after verification.'))
            comment_form = CommentForm()

    return render(request, 'products/product_detail.html',
                  {'product': product,
                   'comments': comments,
                   'comment_form': comment_form,
                   'add_to_cart_form':add_to_cart_form}
                  )


