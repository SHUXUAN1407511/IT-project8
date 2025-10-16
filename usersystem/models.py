from django.db import models


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

    def __str__(self):
        label = self.name or self.username
        return f"{label} ({self.role})"
