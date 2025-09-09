from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.organizations.serializers import OrganizationSerializer


User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "organization")
        read_only_fields = ("id",)


class GetUserSerializer(BaseUserSerializer):
    organization = OrganizationSerializer(read_only=True)


class CreateUpdateUserSerializer(BaseUserSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ("password",)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = GetUserSerializer(
            instance=self.user,
            context={
                "request": self.context.get("request"),
            },
        )

        data["user"] = serializer.data

        return data
