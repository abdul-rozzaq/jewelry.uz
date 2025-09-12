from rest_framework import serializers

from apps.inventory.models import OrganizationInventory
from apps.organizations.serializers import OrganizationSerializer
from apps.processes.models import ProcessInput, ProcessOutput, Process
from apps.users.models import User


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

    def validate_inventory(self, inventory: OrganizationInventory):
        user: User = self.context["request"].user

        if user.organization != inventory.organization:
            raise serializers.ValidationError({"detail": "Siz bu mahsulotdan foydalana olmaysiz"})

        return inventory

    def validate(self, attrs):
        inventory: OrganizationInventory = attrs["inventory"]
        quantity = attrs["quantity"]

        if inventory.quantity < quantity:
            raise serializers.ValidationError({"detail": "Mahsulot yetarli emas"})

        return attrs


class ProcessOutputCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessOutput
        fields = ["material", "quantity"]


class CreateProcessSerializer(serializers.ModelSerializer):
    inputs = ProcessInputCreateSerializer(many=True, required=True, allow_empty=False)
    outputs = ProcessOutputCreateSerializer(many=True, required=True, allow_empty=False)

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

        read_only_fields = ["id", "created_at", "updated_at", "organization"]

    def create(self, validated_data):
        inputs_data = validated_data.pop("inputs", [])
        outputs_data = validated_data.pop("outputs", [])

        process = Process.objects.create(**validated_data)

        for input_data in inputs_data:
            ProcessInput.objects.create(process=process, **input_data)

        for output_data in outputs_data:
            ProcessOutput.objects.create(process=process, **output_data)

        return process
