from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views import generic
from django.contrib import messages

from pages.forms import ContactForm
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


class ContactUsPageView(generic.FormView):
    template_name = 'pages/contactus.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "پیام شما با موفقیت ارسال شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "لطفاً خطاهای فرم را اصلاح کنید.")
        return super().form_invalid(form)