from rest_framework import serializers
from .models import AIUserScale, ScaleRecord, ScaleVersion, ScaleLevel


# -------------------------
# 旧接口：/scales/
# -------------------------
class AIUserScaleSerializer(serializers.ModelSerializer):
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = AIUserScale
        fields = ["id", "username", "name", "level", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, v):
        if not v or not v.strip():
            raise serializers.ValidationError("name cannot be empty")
        return v.strip()

    def validate(self, attrs):
        username = attrs.get("username") or getattr(self.instance, "username", None)
        name = attrs.get("name") or getattr(self.instance, "name", None)
        if username and name:
            qs = AIUserScale.objects.filter(username=username, name=name)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"name": "this title already exists"})
        return attrs


# -------------------------
# 新接口：/scale-records/
# -------------------------
class ScaleLevelSerializer(serializers.ModelSerializer):
    aiUsage = serializers.CharField(source="ai_usage")
    acknowledgement = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    instructions = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ScaleLevel
        fields = [
            "id", "label", "title", "description",
            "aiUsage", "instructions", "acknowledgement"
        ]


class ScaleVersionSerializer(serializers.ModelSerializer):
    updatedAt = serializers.DateTimeField(source="updated_at", format="%Y-%m-%d %H:%M:%S", read_only=True)
    updatedBy = serializers.CharField(source="updated_by")
    levels = ScaleLevelSerializer(many=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = ScaleVersion
        fields = ["id", "version", "updatedAt", "updatedBy", "notes", "levels"]


class ScaleRecordSerializer(serializers.ModelSerializer):
    ownerType = serializers.CharField(source="owner_type")
    ownerId = serializers.CharField(source="owner_id", required=False, allow_null=True, allow_blank=True)
    isPublic = serializers.BooleanField(source="is_public")

    currentVersion = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = ScaleRecord
        fields = [
            "id", "name",
            "ownerType", "ownerId", "isPublic",
            "currentVersion", "history",
        ]

    def get_currentVersion(self, obj: ScaleRecord):
        latest = obj.versions.order_by("-version").first()
        return ScaleVersionSerializer(latest).data if latest else None

    def get_history(self, obj: ScaleRecord):
        qs = obj.versions.order_by("-version")
        latest = qs.first()
        if not latest:
            return []
        others = qs.exclude(pk=latest.pk)
        return ScaleVersionSerializer(others, many=True).data


class SaveScaleVersionRequestSerializer(serializers.Serializer):
    scaleId = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    updatedBy = serializers.CharField(required=False, allow_blank=True)
    levels = ScaleLevelSerializer(many=True)
