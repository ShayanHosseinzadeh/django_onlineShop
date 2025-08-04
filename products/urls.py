# products/urls.py
from django.urls import path,re_path
from . import views

urlpatterns = [
    # URL pattern for the main product list page
    path('', views.ProductListView.as_view(), name='product_list'),

    # New URL pattern for product lists filtered by category
    re_path(r'^category/(?P<category_slug>[-\w]+)/$', views.ProductListView.as_view(), name='product_list_by_category'),

    # Your existing URL for product detail view (using pk)
    path('<int:pk>/', views.ProductDetailView, name='product_detail'),
]