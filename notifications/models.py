import uuid

from django.db import models

from usersystem.models import User


class Notification(models.Model):
    """
    Stores in-app notifications for platform users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        User,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    body = models.TextField(blank=True)
    related_type = models.CharField(max_length=50, blank=True)
    related_id = models.CharField(max_length=128, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["related_type", "related_id"]),
        ]

    def __str__(self):
        return f"{self.title} -> {self.recipient_id}"
