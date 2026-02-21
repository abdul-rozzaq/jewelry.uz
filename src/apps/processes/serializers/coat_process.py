from apps.organizations.serializers import OrganizationSerializer
from rest_framework import serializers

from apps.processes.models import CoatProcess


class CoatProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoatProcess
        fields = "__all__"

        read_only_fields = ["status", "started_at", "finished_at", "pure_gold"]


class GetCoatProcessSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer()

    class Meta:
        model = CoatProcess
        fields = "__all__"

        read_only_fields = ["status", "started_at", "finished_at", "pure_gold"]
