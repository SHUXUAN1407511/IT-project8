from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    createdAt = serializers.DateTimeField(source="created_at", read_only=True)
    isRead = serializers.BooleanField(source="is_read", read_only=True)
    relatedType = serializers.CharField(source="related_type", required=False, allow_blank=True)
    relatedId = serializers.CharField(
        source="related_id",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "content",
            "body",
            "createdAt",
            "isRead",
            "relatedType",
            "relatedId",
        ]
