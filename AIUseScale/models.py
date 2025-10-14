from django.db import models

class AIUserScale(models.Model):
    username = models.CharField(max_length=150, db_index=True)
    name = models.CharField(max_length=120)
    level = models.CharField(max_length=10)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_user_scale"
        constraints = [
            models.UniqueConstraint(
                fields=["username", "name"],
                name="uq_aiuserscale_username_name"
            )
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.username} - {self.name}"
