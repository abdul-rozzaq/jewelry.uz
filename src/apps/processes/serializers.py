from rest_framework import serializers

from apps.organizations.serializers import OrganizationSerializer
from apps.processes.models import ProcessInput, ProcessOutput, Process


class ProcessInputGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessInput
        fields = "__all__"


class ProcessOutputGetSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessOutput
        fields = "__all__"


class GetProcessSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    inputs = ProcessInputGetSerializer(many=True)
    outputs = ProcessOutputGetSerializer(many=True)

    class Meta:
        model = Process
        fields = "__all__"


class ProcessInputCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessInput
        fields = ["inventory", "quantity"]


class ProcessOutputCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessOutput
        fields = ["material", "quantity"]


class CreateProcessSerializer(serializers.ModelSerializer):
    inputs = ProcessInputCreateSerializer(many=True, required=False)
    outputs = ProcessOutputCreateSerializer(many=True, required=False)

    class Meta:
        model = Process
        fields = [
            "organization",
            "process_type",
            "status",
            "started_at",
            "finished_at",
            "inputs",
            "outputs",
        ]

    def create(self, validated_data):
        inputs_data = validated_data.pop("inputs", [])
        outputs_data = validated_data.pop("outputs", [])

        process = Process.objects.create(**validated_data)

        # ProcessInput yaratish
        for input_data in inputs_data:
            ProcessInput.objects.create(process=process, **input_data)

        # ProcessOutput yaratish
        for output_data in outputs_data:
            ProcessOutput.objects.create(process=process, **output_data)

        return process
