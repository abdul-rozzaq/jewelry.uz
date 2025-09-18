from rest_framework import serializers


class DashboardStatsSerializer(serializers.Serializer):
    materials = serializers.DictField()
    workshops = serializers.DictField()
    transfers = serializers.DictField()
    pending = serializers.DictField()
