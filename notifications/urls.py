from django.urls import path
from . import views
from .views import make_test_notification

urlpatterns = [
    path("api/notifications/", views.list_notifications, name="notifications-list"),
    path("api/notifications/mark-all-read/", views.mark_all_read, name="notifications-mark-all"),
    path("api/notifications/<int:pk>/read/", views.mark_read, name="notifications-mark"),
    path("api/notifications/test/", make_test_notification, name="notifications-test"),

]