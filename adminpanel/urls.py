from django.urls import path

from . import views

urlpatterns = [
    path('', views.Admin_Home.as_view(), name='admin_dashboard'),
    path('users/', views.AdminUserManage.as_view(), name='admin_user_manage'),
    path('users/bulk-action/', views.BulkUserActionView.as_view(), name='bulk_user_action'),
    path('users/export/excel/', views.ExportUsersToExcelView.as_view(), name='export_users_to_excel'),
    path('orders/', views.AdminOrderManageView.as_view(), name='admin_order_manage'),
    path('products/', views.AdminProductManageView.as_view(), name='admin_product_manage'),
    path('reports/', views.AdminReportsView.as_view(), name='admin_reports'),
    path('notifications/', views.AdminNotificationsView.as_view(), name='admin_notifications'),
    path('settings/', views.AdminSettingsView.as_view(), name='admin_settings'),

    path('users/edit/<int:pk>/', views.UserProfileUpdateView.as_view(), name='edit_user_profile'),
    path('users/delete/<int:pk>/', views.UserProfileDeleteView.as_view(), name='delete_user_profile'),

    path('orders/export/excel/', views.ExportOrdersToExcelView.as_view(), name='export_orders_to_excel'),
    path('orders/bulk-action/', views.BulkOrderActionView.as_view(), name='bulk_order_action'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='panel_order_detail'),
]