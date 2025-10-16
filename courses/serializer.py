from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='Course_name', max_length=120)
    term = serializers.CharField(source='semester', max_length=20)
    description = serializers.CharField(source='Description', allow_blank=True, required=False)
    scId = serializers.CharField(source='coordinator', allow_blank=True, required=False)

    createdAt = serializers.DateTimeField(source='created_at', format="%Y-%m-%d %H:%M:%S", read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'code', 'term', 'description', 'scId',
            'createdAt', 'updatedAt',
        ]
        read_only_fields = ['id', 'createdAt', 'updatedAt']

    def validate(self, attrs):
        code = attrs.get('code') or getattr(self.instance, 'code', None)
        sem = attrs.get('semester') or getattr(self.instance, 'semester', None)
        if code and sem:
            qs = Course.objects.filter(code=code, semester=sem)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({'code': 'code already exists in this term'})
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = str(data['id'])
        if data.get('scId') is not None:
            data['scId'] = str(data['scId'])
        return data
