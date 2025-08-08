from django.shortcuts import render
from django.views import generic
from products.models import Product, Category


# Create your views here.

class HomePageView(generic.TemplateView):
    template_name = 'pages/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        colors = [
            "bg-blue-500", "bg-green-500", "bg-purple-500",
            "bg-pink-500", "bg-yellow-500", "bg-red-500"
        ]
        hover_colors = [
            "bg-blue-600", "bg-green-600", "bg-purple-600",
            "bg-pink-600", "bg-yellow-600", "bg-red-600"
        ]

        categories = Category.objects.all()
        for i, cat in enumerate(categories):
            cat.color_class = colors[i % len(colors)]
            cat.hover_color = hover_colors[i % len(hover_colors)]

        context['categories'] = categories
        context['products'] = Product.objects.all()
        context['discounted_products'] = Product.objects.filter(discount_percent__gt=0).order_by('-discount_percent')[:4]
        return context


class AboutUsPageView(generic.TemplateView):
    template_name = 'pages/aboutus.html'
