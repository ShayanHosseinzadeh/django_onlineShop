from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404, reverse

from .forms import CommentForm
from .models import Product, Comment


# Create your views here.
class ProductListView(generic.ListView):
    template_name = 'products/products_list.html'
    context_object_name = 'products'
    paginate_by = 4

    def get_queryset(self):
        return Product.objects.filter(status='avl').order_by('-price')


def ProductDetailView(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = Comment.verified_comments.order_by('-datetime_created')
    comment_form = CommentForm()
    return render(request, 'products/product_detail.html',
                  {'product': product,
                   'comments': comments,
                   'comment_form': comment_form}
                  )
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()

# class ProductDetailView(generic.DetailView):
#     model = Product
#     template_name = 'products/product_detail.html'
#     context_object_name = 'product'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['comment_form'] = CommentForm()
#         return context

#
# class CommentCreateView(generic.CreateView):
#     model = Comment
#     form_class = CommentForm
#     def get_success_url(self):
#         return reverse('product_list')
#
#     def form_valid(self, form):
#         comment = form.save(commit=False)
#         comment.user = self.request.user
#
#         product_id = int(self.kwargs['product_id'])
#         product = get_object_or_404(Product, id=product_id)
#
#         comment.product = product
#         return super().form_valid(form)
#
