from rest_framework import serializers

from .models import Material


class MaterialSerializer(serializers.ModelSerializer):
    karat = serializers.SerializerMethodField()

    class Meta:
        model = Material
        fields = "__all__"

    def get_karat(self, obj):
        return obj.karat
