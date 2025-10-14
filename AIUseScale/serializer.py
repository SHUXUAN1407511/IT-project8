# app/serializers.py
from rest_framework import serializers
from .models import AIUserScale

class AIUserScaleSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = AIUserScale
        fields = ["id", "username", "name", "level", "notes", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, v: str):
        if not v or not v.strip():
            raise serializers.ValidationError("name cannot be empty")
        return v.strip()

    def validate(self, attrs):
        username = attrs.get("username") or getattr(self.instance, "username", None)
        name = attrs.get("name") or getattr(self.instance, "name", None)

        qs = AIUserScale.objects.filter(username=username, name=name)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if name and username and qs.exists():
            raise serializers.ValidationError({"name": "this title already exists"})
        return attrs

    def create(self, validated_data):
        return AIUserScale.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
