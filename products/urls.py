from django.urls import path

from products import views
urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>', views.ProductDetailView, name='product_detail'),

]