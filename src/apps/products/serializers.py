from decimal import Decimal, ROUND_HALF_UP
from rest_framework import serializers

from apps.common.choices.materials import MaterialType
from apps.organizations.serializers import OrganizationSerializer
from apps.projects.serializers import ProjectSerializer
from apps.projects.models import Project

from .models import Product


class ProductWriteSerializer(serializers.ModelSerializer):
    project_id = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), source="project", write_only=True, required=False, allow_null=True)
    material = serializers.ChoiceField(choices=MaterialType.choices)

    class Meta:
        model = Product
        fields = (
            "id",
            "material",
            "project_id",
            "quantity",
            "purity",
            "is_composite",
            "pure_gold",
            "source_description",
        )
        extra_kwargs = {
            "pure_gold": {"required": False},
        }

    def validate(self, attrs):
        is_composite = attrs.get("is_composite", False)
        quantity = attrs.get("quantity")
        pure_gold = attrs.get("pure_gold")

        # When composite, pure_gold is required and must be > 0
        if is_composite:
            if pure_gold is None or pure_gold <= 0:
                raise serializers.ValidationError({"pure_gold": "pure_gold is required and must be > 0 when is_composite=True."})

        # pure_gold must not exceed total quantity
        if pure_gold is not None and quantity is not None and pure_gold > quantity:
            raise serializers.ValidationError({"pure_gold": "pure_gold cannot be greater than quantity."})

        return attrs

    def save(self, **kwargs):
        product = super().save(**kwargs)

        # Recalculate or persist pure_gold according to is_composite
        if product.is_composite:
            # keep provided pure_gold, only update purity
            product.save(update_fields=["purity"])
        else:
            # For specific materials that don't mix with gold or have fixed purity, usage might differ.
            # But preserving logic for now.
            try:
                raw = (product.quantity * product.purity) / Decimal("100")
                product.pure_gold = raw.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
                product.save(update_fields=["purity", "pure_gold"])
            except Exception:
                # If any casting/decimal issue occurs, at least persist purity
                product.save(update_fields=["purity"])

        return product


class ProductReadSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)
    material = serializers.CharField(source="get_material_display") 
    karat = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "organization",
            "project",
            "material",
            "quantity",
            "purity",
            "is_composite",
            "pure_gold",
            "karat",
            "source_description",
            "created_at",
            "updated_at",
        )

    def get_karat(self, obj):
        return obj.karat
