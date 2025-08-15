from django.urls import path

from core.views import AdminSiteSettingsView
from . import views
from .views import BulkProductActionView, AdminProductUpdateView, AdminProductDeleteView

urlpatterns = [
    path('', views.Admin_Home.as_view(), name='admin_dashboard'),
    path('users/', views.AdminUserManage.as_view(), name='admin_user_manage'),
    path('users/bulk-action/', views.BulkUserActionView.as_view(), name='bulk_user_action'),
    path('users/export/excel/', views.ExportUsersToExcelView.as_view(), name='export_users_to_excel'),
    path('orders/manage/', views.AdminOrderManageView.as_view(), name='admin_order_manage'),
    path('reports/', views.AdminReportsView.as_view(), name='admin_reports'),

    path('users/new/', views.UserProfileCreateView.as_view(), name='user_create'),
    path('users/edit/<int:pk>/', views.UserProfileUpdateView.as_view(), name='edit_user_profile'),
    path('users/delete/<int:pk>/', views.UserProfileDeleteView.as_view(), name='delete_user_profile'),

    path('orders/export/excel/', views.ExportOrdersToExcelView.as_view(), name='export_orders_to_excel'),
    path('orders/bulk-action/', views.BulkOrderActionView.as_view(), name='bulk_order_action'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='panel_order_detail'),
    path('orders/edit/<int:pk>/', views.OrderUpdateView.as_view(), name='order_update'),
    path('orders/delete/<int:pk>/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('orders/new/', views.OrderCreateView.as_view(), name='admin_order_create'),

    path('products/bulk-action/', BulkProductActionView.as_view(), name='bulk_product_action'),
    path('products/', views.AdminProductManageView.as_view(), name='admin_product_manage'),
    path('products/<int:pk>', views.AdminProductDetailView.as_view(), name='admin_product_detail'),
    path("products/<int:pk>/edit/", AdminProductUpdateView.as_view(), name="admin_product_edit"),
    path("products/<int:pk>/delete/", AdminProductDeleteView.as_view(), name="admin_product_delete"),

    path('categories/', views.AdminCategoryManageView.as_view(), name='admin_category_manage'),
    path('categories/create/modal/', views.AdminCategoryCreateModalView.as_view(), name='admin_category_create_modal'),
    path('categories/<int:pk>/edit/modal/', views.AdminCategoryUpdateModalView.as_view(),
         name='admin_category_edit_modal'),
    path('categories/<int:pk>/delete/modal/', views.AdminCategoryDeleteModalView.as_view(),
         name='admin_category_delete_modal'),

    path("admin/reports/", views.AdminReportsView.as_view(), name="admin_reports"),

    path("admin/settings/", AdminSiteSettingsView.as_view(), name="admin_settings"),


    path("notifications/", views.AdminNotificationsIndexView.as_view(), name="admin_notifications"),
    path("notifications/partial/", views.AdminNotificationsPartialView.as_view(), name="admin_notifications_partial"),
    path("notifications/<int:pk>/toggle/", views.AdminNotificationToggleReadView.as_view(),
         name="admin_notification_toggle"),
    path("panel/notifications/mark-all-read/", views.AdminNotificationsMarkAllReadView.as_view(),
         name="admin_notifications_mark_all"),


    path('orders/',views.UserOrderListView.as_view(), name='user_order_list'),
]