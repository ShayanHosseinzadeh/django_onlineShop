# products/views.py
from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg, Q

from cart.cart import Cart
from .forms import CommentForm
from cart.forms import CartAddForm
from .models import Product, Comment, Category


# Create your views here.
class ProductListView(generic.ListView):
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_queryset(self):
        queryset = Product.available.all()

        # Handle category filtering
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            self.category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=self.category)
        else:
            self.category = None

        # Handle sorting
        sort_by = self.request.GET.get('sort_by', 'default')
        if sort_by == 'price':
            queryset = queryset.order_by('price')
        elif sort_by == '-price':
            queryset = queryset.order_by('-price')
        elif sort_by == '-datetime_created':
            queryset = queryset.order_by('-datetime_created')
        elif sort_by == 'popularity':
            # This is a placeholder for a 'popularity' field. Let's assume you have a 'sales_count' or similar
            # For now, we'll order by the number of comments as a proxy for popularity
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category'] = self.category

        # Add sorting parameter to context so template knows which option is selected
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        return context

    def get(self, request, *args, **kwargs):
        if 'HX-Request' in request.headers:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return render(request, 'products/partials/product_grid.html', context)
        return super().get(request, *args, **kwargs)


def ProductDetailView(request, pk):
    # Your existing ProductDetailView logic
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
                   'add_to_cart_form': add_to_cart_form}
                  )
