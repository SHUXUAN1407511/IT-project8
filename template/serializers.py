from typing import Any, Dict, List

from rest_framework import serializers

from .models import AssignmentTemplate


class TemplateRowField(serializers.ListField):
    """
    Validates the template rows payload. Each row should be a dict of string keys to string values.
    """

    def __init__(self, **kwargs):
        kwargs.setdefault(
            "child",
            serializers.DictField(
                child=serializers.CharField(allow_blank=True, required=False),
                allow_empty=True,
            ),
        )
        super().__init__(**kwargs)

    def to_internal_value(self, data: Any) -> List[Dict[str, str]]:
        rows = super().to_internal_value(data)
        normalized: List[Dict[str, str]] = []
        for row in rows:
            normalized_row: Dict[str, str] = {}
            for key, value in row.items():
                normalized_row[str(key)] = "" if value is None else str(value)
            normalized.append(normalized_row)
        return normalized


class AssignmentTemplateSerializer(serializers.ModelSerializer):
    assignmentId = serializers.CharField(source="assignment_id", read_only=True)
    rows = TemplateRowField(allow_empty=True)
    isPublished = serializers.BooleanField(source="is_published", read_only=True)
    updatedAt = serializers.DateTimeField(source="updated_at", read_only=True)
    updatedBy = serializers.CharField(source="updated_by", allow_blank=True, required=False)
    lastPublishedAt = serializers.DateTimeField(
        source="last_published_at", allow_null=True, read_only=True
    )

    class Meta:
        model = AssignmentTemplate
        fields = [
            "id",
            "assignmentId",
            "rows",
            "isPublished",
            "updatedAt",
            "updatedBy",
            "lastPublishedAt",
        ]

    def create(self, validated_data: Dict[str, Any]) -> AssignmentTemplate:
        return AssignmentTemplate.objects.create(**validated_data)

    def update(
        self, instance: AssignmentTemplate, validated_data: Dict[str, Any]
    ) -> AssignmentTemplate:
        if "rows" in validated_data:
            instance.rows = validated_data["rows"]
        if "updated_by" in validated_data:
            instance.updated_by = validated_data["updated_by"]
        instance.save()
        return instance
