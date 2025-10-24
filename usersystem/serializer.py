from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "password", "role"]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        username = validated_data.get("username")
        password = validated_data.get("password")

        if username is not None:
            instance.username = username
        if password is not None:
            instance.password = make_password(password)
        instance.save()
        return instance


class ManagedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "role",
            "status",
            "phone",
            "organization",
            "bio",
            "last_login_at",
        ]
        read_only_fields = ["id", "last_login_at"]


class SelfProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    organization = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "name",
            "email",
            "role",
            "status",
            "phone",
            "organization",
            "bio",
        ]
        read_only_fields = ["id", "username", "role", "status"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["id"] = str(instance.id)
        return data
