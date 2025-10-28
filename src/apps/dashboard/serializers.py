from rest_framework import serializers


class StatisticsField(serializers.Serializer):
    count = serializers.IntegerField(required=True)
    total = serializers.FloatField(required=True)


class DashboardStatsSerializer(serializers.Serializer):
    materials = StatisticsField()
    organizations = StatisticsField()
    transactions = StatisticsField()
    gold = StatisticsField()
