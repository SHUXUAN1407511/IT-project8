from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Course
        fields = [
            "id", "code", "name", "teacher", "semester", "credits",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_code(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("code cannot be empty")
        return v

    def validate_name(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("name cannot be empty")
        return v

    def validate_semester(self, v):
        v = (v or "").strip()
        if not v:
            raise serializers.ValidationError("semester cannot be empty")
        return v

    def validate_credits(self, v):
        if v is None or v < 0:
            raise serializers.ValidationError("credits must be a non-negative integer")
        return v

    def validate(self, attrs):
        for k in ["code", "name", "teacher", "semester"]:
            if k in attrs and isinstance(attrs[k], str):
                attrs[k] = attrs[k].strip()

        code = attrs.get("code") or getattr(self.instance, "code", None)
        semester = attrs.get("semester") or getattr(self.instance, "semester", None)

        if code and semester:
            qs = Course.objects.filter(code=code, semester=semester)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"code": "this code already exists in this semester"})
        return attrs
