import uuid
from django.db import models


# -------------------------
# 旧：简易量规（/scales/）
# -------------------------
class AIUserScale(models.Model):
    username = models.CharField(max_length=128, db_index=True)
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=64)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)  # 输出到秒
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_user_scale"
        unique_together = (("username", "name"),)
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.username} - {self.name} ({self.level})"


# ---------------------------------------
# 新：版本化量规（/scale-records/）
# ---------------------------------------
class ScaleRecord(models.Model):
    OWNER_SYSTEM = "system"
    OWNER_SC = "sc"
    OWNER_CHOICES = (
        (OWNER_SYSTEM, "System"),
        (OWNER_SC, "SC"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner_type = models.CharField(max_length=10, choices=OWNER_CHOICES)
    owner_id = models.CharField(max_length=128, null=True, blank=True)
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)  # 内部用
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "scale_record"
        indexes = [
            models.Index(fields=["owner_type", "owner_id"]),
            models.Index(fields=["is_public"]),
        ]
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} ({self.owner_type}/{self.owner_id})"


class ScaleVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(ScaleRecord, related_name="versions", on_delete=models.CASCADE)
    version = models.IntegerField()
    updated_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=128)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "scale_version"
        unique_together = (("record", "version"),)
        ordering = ["-version"]

    def __str__(self):
        return f"{self.record_id} v{self.version}"


class ScaleLevel(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    version = models.ForeignKey(ScaleVersion, related_name="levels", on_delete=models.CASCADE)
    position = models.IntegerField()
    label = models.CharField(max_length=255)
    title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    ai_usage = models.TextField()  # = aiUsage
    instructions = models.TextField(null=True, blank=True)
    acknowledgement = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "scale_level"
        ordering = ["position"]

    def __str__(self):
        return f"{self.id} @ v{self.version.version}"
