from django.db.models import Sum
from django.db import transaction

from rest_framework import serializers

from operator import itemgetter

from apps.common.choices.materials import MaterialType
from apps.organizations.serializers import CurrentUserOrganization, OrganizationSerializer
from apps.processes.models import CoatProcess
from apps.processes.models.base import ProcessStatus
from apps.products.models import Product


class CoatProcessSerializer(serializers.ModelSerializer):
    organization = serializers.HiddenField(default=CurrentUserOrganization())

    class Meta:
        model = CoatProcess
        fields = "__all__"

        read_only_fields = ["status", "started_at", "finished_at", "pure_gold", "organization"]

    def validate(self, attrs):
        organization, gold_input, iron_input = itemgetter("organization", "gold_input", "iron_input")(attrs)

        if organization is None:
            raise serializers.ValidationError({"organization": "User organization not found."})

        gold_555 = Product.objects.filter(organization=organization, material=MaterialType.GOLD_585).aggregate(total_quantity=Sum("quantity"))

        if gold_555["total_quantity"] is None or gold_input > gold_555["total_quantity"]:
            raise serializers.ValidationError({"quantity": "Not enough gold available."})

        return attrs


class GetCoatProcessSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = CoatProcess
        fields = "__all__"

        read_only_fields = ["status", "started_at", "finished_at", "pure_gold"]


class CompleteCoatProcessSerializer(CoatProcessSerializer):

    @transaction.atomic
    def update(self, instance, validated_data):

        instance.status = ProcessStatus.COMPLETED
        instance.finished_at = None

        return super().update(instance, validated_data)
