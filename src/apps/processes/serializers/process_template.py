from rest_framework import serializers

from apps.materials.serializers import MaterialSerializer
from apps.processes.models import ProcessTemplateInputItem, ProcessTemplateOutputItem, ProcessTemplate


class ProcessTemplateInputItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    material_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProcessTemplateInputItem
        fields = ["id", "material", "material_id", "role", "use_all_material"]


class ProcessTemplateOutputItemSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    material_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ProcessTemplateOutputItem
        fields = ["id", "material", "material_id", "role", "use_all_material"]


class ProcessTemplateSerializer(serializers.ModelSerializer):
    template_inputs = ProcessTemplateInputItemSerializer(many=True, read_only=True)
    template_outputs = ProcessTemplateOutputItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProcessTemplate
        fields = ["id", "name", "template_inputs", "template_outputs"]
