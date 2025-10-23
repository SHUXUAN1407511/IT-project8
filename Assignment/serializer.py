from datetime import datetime

from rest_framework import serializers

from courses.models import Course
from usersystem.models import User
from .models import Assignment


class AssignmentSerializer(serializers.ModelSerializer):
    courseId = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(),
        source='course',
        allow_null=True,
        required=False,
    )
    name = serializers.CharField()
    type = serializers.CharField()
    description = serializers.CharField(allow_blank=True, required=False)
    tutorIds = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='tutor'),
        source='tutors',
        many=True,
        required=False,
        allow_empty=True,
    )
    dueDate = serializers.DateTimeField(
        source='due_date',
        required=False,
        allow_null=True,
    )
    hasTemplate = serializers.BooleanField(
        source='has_template',
        required=False,
    )
    templateUpdatedAt = serializers.DateTimeField(
        source='template_updated_at',
        required=False,
        allow_null=True,
    )
    aiDeclarationStatus = serializers.CharField(
        source='ai_declaration_status',
        required=False,
    )
    createdAt = serializers.DateTimeField(
        source='created_at',
        read_only=True,
    )
    updatedAt = serializers.DateTimeField(
        source='updated_at',
        read_only=True,
    )

    class Meta:
        model = Assignment
        fields = [
            'id',
            'courseId',
            'name',
            'type',
            'description',
            'tutorIds',
            'dueDate',
            'hasTemplate',
            'templateUpdatedAt',
            'aiDeclarationStatus',
            'createdAt',
            'updatedAt',
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']

    def validate_aiDeclarationStatus(self, value: str):
        if value and value not in dict(Assignment.STATUS_CHOICES):
            raise serializers.ValidationError('Invalid declaration status.')
        return value

    def validate_tutorIds(self, value):
        for user in value:
            if user.role != 'tutor':
                raise serializers.ValidationError(f'User "{user.username}" is not a tutor.')
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Ensure IDs are serialized as strings for frontend strict comparisons
        if data.get('courseId') is not None:
            data['courseId'] = str(data['courseId'])
        data['tutorIds'] = [str(tutor_id) for tutor_id in data.get('tutorIds', [])]

        # Format datetime values for consistency
        for key in ['dueDate', 'templateUpdatedAt', 'createdAt', 'updatedAt']:
            value = data.get(key)
            if isinstance(value, (datetime, )):
                data[key] = value.isoformat()
            elif isinstance(value, str) and value:
                # keep strings as is
                continue
            else:
                data[key] = value
        return data

    def create(self, validated_data):
        tutors = validated_data.pop('tutors', [])
        assignment = super().create(validated_data)
        if tutors:
            assignment.tutors.set(tutors)
        return assignment

    def update(self, instance, validated_data):
        tutors = validated_data.pop('tutors', None)
        assignment = super().update(instance, validated_data)
        if tutors is not None:
            assignment.tutors.set(tutors)
        return assignment
