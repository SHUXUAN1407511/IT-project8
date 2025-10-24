from django.db import models
from django.utils import timezone


class User(models.Model):
    ROLE_CHOICES = [
        ("admin", "Administrator"),
        ("sc", "Subject Coordinator"),
        ("tutor", "Tutor"),
    ]

    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"

    username = models.CharField(max_length=120, unique=True)
    password = models.CharField(max_length=120)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(max_length=255, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[(STATUS_ACTIVE, "Active"), (STATUS_INACTIVE, "Inactive")],
        default=STATUS_ACTIVE,
    )
    phone = models.CharField(max_length=50, blank=True)
    organization = models.CharField(max_length=120, blank=True)
    bio = models.TextField(blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    auth_token = models.CharField(max_length=64, unique=True, null=True, blank=True)

    def __str__(self):
        label = self.name or self.username
        return f"{label} ({self.role})"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token_hash = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'used' if self.used_at else 'active'
        return f"PasswordResetToken(user={self.user_id}, {status})"

    def is_active(self) -> bool:
        return self.used_at is None and timezone.now() <= self.expires_at

    def mark_used(self) -> None:
        if self.used_at is not None:
            return
        self.used_at = timezone.now()
        self.save(update_fields=['used_at'])
