from rest_framework import serializers
from django.utils import timezone
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = Assignment
        fields = ["id", "subject", "assignment_title", "due_date", "assignment_type", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_due_date(self, v):
        if v <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return v
