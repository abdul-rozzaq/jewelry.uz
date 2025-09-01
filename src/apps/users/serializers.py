from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "pk",
            "first_name",
            "last_name",
            "username",
            "role",
            "organization",
        ]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializer(
            instance=self.user,
            context={
                "request": self.context.get("request"),
            },
        )

        data["user"] = serializer.data

        return data
