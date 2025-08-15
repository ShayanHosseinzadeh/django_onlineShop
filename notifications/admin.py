# notifications/admin.py
from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "verb", "level", "is_read", "created_at")
    list_filter = ("level", "read_at", "created_at")
    search_fields = ("verb", "payload")
