from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.aggregates import Sum
from django.db.models.expressions import F
from django.db.models.fields import IntegerField
from django.db.models.functions.comparison import Cast
from django.views import generic

from orders.models import Order, OrderItem
from products.models import Product


class Admin_Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'adminpanel/admin_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        total_revenue = OrderItem.objects.filter(
            order__status='completed'
        ).aggregate(
            total=Cast(Sum(F('quantity') * F('price')), IntegerField())
        )['total'] or 0
        total_orders = Order.objects.count()

        total_products = Product.objects.count()

        User = get_user_model()
        total_users = User.objects.count()

        context.update({
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'total_products': total_products,
            'total_users': total_users,
        })
        return context