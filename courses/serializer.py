from typing import Any, MutableMapping

from rest_framework import serializers

from usersystem.models import User

from .models import Course


class CoordinatorField(serializers.PrimaryKeyRelatedField):
    def to_internal_value(self, data):
        if data in (None, "", "null"):
            return None
        return super().to_internal_value(data)


class CourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="course_name", max_length=120)
    term = serializers.CharField(source="semester", max_length=20)
    description = serializers.CharField(allow_blank=True, required=False)
    coordinatorId = CoordinatorField(
        source="coordinator",
        queryset=User.objects.filter(role="sc", status=User.STATUS_ACTIVE),
        allow_null=True,
        required=False,
    )
    coordinatorName = serializers.SerializerMethodField(read_only=True)

    createdAt = serializers.DateTimeField(
        source="created_at",
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
    )
    updatedAt = serializers.DateTimeField(
        source="updated_at",
        format="%Y-%m-%d %H:%M:%S",
        read_only=True,
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "code",
            "term",
            "description",
            "coordinatorId",
            "coordinatorName",
            "createdAt",
            "updatedAt",
        ]
        read_only_fields = ["id", "coordinatorName", "createdAt", "updatedAt"]

    def to_internal_value(self, data: Any) -> MutableMapping[str, Any]:
        if isinstance(data, MutableMapping):
            if "coordinator_id" in data and "coordinatorId" not in data:
                data = data.copy()
                data["coordinatorId"] = data.pop("coordinator_id")
        return super().to_internal_value(data)

    def validate(self, attrs):
        code = attrs.get("code") or getattr(self.instance, "code", None)
        sem = attrs.get("semester") or getattr(self.instance, "semester", None)
        if code and sem:
            qs = Course.objects.filter(code=code, semester=sem)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"code": "code already exists in this term"}
                )
        coordinator = attrs.get("coordinator")
        if coordinator and coordinator.role != "sc":
            raise serializers.ValidationError(
                {"coordinatorId": "coordinator must be a subject coordinator"}
            )
        if coordinator and coordinator.status != User.STATUS_ACTIVE:
            raise serializers.ValidationError(
                {"coordinatorId": "coordinator must be active"}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.pk)
        coordinator = getattr(instance, "coordinator", None)
        data["coordinatorId"] = (
            str(coordinator.pk) if coordinator is not None else ""
        )
        return data

    def get_coordinatorName(self, instance: Course) -> str:
        coordinator = getattr(instance, "coordinator", None)
        if not coordinator:
            return ""
        return coordinator.name or coordinator.username
