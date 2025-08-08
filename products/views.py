# products/views.py
from django.core.paginator import Paginator
from django.db.models.aggregates import Count
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
    paginate_by = 8

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
            queryset = queryset.annotate(comment_count=Count('comments')).order_by('-comment_count')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['category'] = self.category

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


def search_results(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = Product.objects.filter(title__icontains=query)
    else:
        results = Product.objects.none()


    paginator = Paginator(results, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    start_index = (page_obj.number - 1) * paginator.per_page + 1 if page_obj else 0
    end_index = start_index + len(page_obj.object_list) - 1 if page_obj else 0
    total_products = paginator.count

    context = {
        'query': query,
        'page_obj': page_obj,
        'start_index': start_index,
        'end_index': end_index,
        'total_products': total_products,
        'results':results,
    }
    return render(request, 'products/search_results.html', context)
