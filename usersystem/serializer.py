from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

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
