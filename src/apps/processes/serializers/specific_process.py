from rest_framework import serializers
from django.db import transaction

from apps.processes.models import GoldDowngradeProcess
from apps.processes.services.gold_downgrade_strategy import GoldDowngradeStrategy
from apps.products.models import Product


# class CoatProcessSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CoatProcess
#         fields = "__all__"

#         read_only_fields = ["status", "started_at", "finished_at", "pure_gold"]


# class CoatProcessSerializer(serializers.ModelSerializer):
#     gold_product_id = serializers.IntegerField(write_only=True)
#     iron_product_id = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = CoatProcess
#         fields = [
#             "id", "organization", "status", "started_at", "finished_at",
#             "gold_input", "iron_input", "scrap_output", "iron_gold_output",
#             "gold_product_id", "iron_product_id", "pure_gold"
#         ]
#         read_only_fields = ["id", "status", "started_at", "finished_at", "pure_gold"]

#     def create(self, validated_data):
#         gold_prod_id = validated_data.pop("gold_product_id")
#         iron_prod_id = validated_data.pop("iron_product_id")

#         # Validation of products belonging to organization
#         org = validated_data.get("organization")
#         # Note: organization might be set from view perform_create automatically or passed here.

#         gold_prod = Product.objects.get(id=gold_prod_id, organization=org)
#         iron_prod = Product.objects.get(id=iron_prod_id, organization=org)

#         with transaction.atomic():
#             process = super().create(validated_data)

#             strategy_data = {
#                 "gold_product": gold_prod,
#                 "iron_product": iron_prod
#             }

#             strategy = CoatStrategyV2(process, strategy_data)
#             strategy.execute()

#         return process


class GoldDowngradeProcessSerializer(serializers.ModelSerializer):
    source_product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = GoldDowngradeProcess
        fields = ["id", "organization", "status", "started_at", "finished_at", "gold_999_input", "gold_585_output", "source_product_id", "pure_gold"]
        read_only_fields = ["id", "status", "started_at", "finished_at", "pure_gold"]

    def create(self, validated_data):
        source_prod_id = validated_data.pop("source_product_id")
        org = validated_data.get("organization")

        source_prod = Product.objects.get(id=source_prod_id, organization=org)

        # Additional validation: source must be 999?
        # Strategy might handle it or here.
        if source_prod.purity < 999:  # Approximate check
            raise serializers.ValidationError("Source product must be ~999 purity for downgrade base")

        with transaction.atomic():
            process = super().create(validated_data)

            strategy_data = {"source_product": source_prod}

            strategy = GoldDowngradeStrategy(process, strategy_data)
            strategy.execute()

        return process
