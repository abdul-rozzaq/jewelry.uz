from rest_framework import serializers

from apps.materials.serializers import MaterialSerializer
from apps.products.models import Product
from apps.organizations.serializers import OrganizationSerializer
from apps.processes.models import ProcessInput, ProcessOutput, Process, ProcessTemplate, ProcessType
from apps.products.serializers import ProductReadSerializer
from apps.users.models import User


class ProcessInputGetSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    product = ProductReadSerializer(read_only=True)

    class Meta:
        model = ProcessInput
        fields = "__all__"


class ProcessOutputGetSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)

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
        fields = ["product", "material", "quantity"]

    def validate_product(self, product: Product):
        user: User = self.context["request"].user

        if product and user.organization != product.organization:
            raise serializers.ValidationError({"detail": "Siz bu mahsulotdan foydalana olmaysiz"})

        return product

    # def validate(self, attrs):
    #     product: Product = attrs["product"]
    #     quantity = attrs["quantity"]

    #     if product.quantity < quantity:
    #         raise serializers.ValidationError({"detail": "Mahsulot yetarli emas"})

    #     return attrs


class ProcessOutputCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcessOutput
        fields = ["material", "quantity"]


class CreateProcessSerializer(serializers.ModelSerializer):
    inputs = ProcessInputCreateSerializer(many=True, required=True, allow_empty=False)
    outputs = ProcessOutputCreateSerializer(many=True, required=True, allow_empty=False)

    process_type = serializers.PrimaryKeyRelatedField(queryset=ProcessType.objects.all(), required=False, allow_null=True)

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


class ProcessTemplateSerializer(serializers.ModelSerializer):
    inputs = MaterialSerializer(many=True)
    outputs = MaterialSerializer(many=True)

    class Meta:
        model = ProcessTemplate
        fields = "__all__"


class ProcessTypeSerializer(serializers.ModelSerializer):
    template = ProcessTemplateSerializer()

    class Meta:
        model = ProcessType
        fields = "__all__"
