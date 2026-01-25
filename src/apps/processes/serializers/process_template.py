from rest_framework import serializers

from apps.materials.serializers import MaterialSerializer
from apps.processes.models import ProcessTemplateItem, ProcessTemplate


class ProcessTemplateItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

    class Meta:
        model = ProcessTemplateItem
        fields = ["id", "material", "use_all_material"]


class ProcessTemplateSerializer(serializers.ModelSerializer):
    inputs = ProcessTemplateItemSerializer(many=True, read_only=True)
    outputs = ProcessTemplateItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessTemplate
        fields = "__all__"
