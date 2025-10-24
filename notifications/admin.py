from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "recipient", "related_type", "is_read", "created_at")
    list_filter = ("related_type", "is_read", "created_at")
    search_fields = ("title", "content", "recipient__username", "recipient__name")
